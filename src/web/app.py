"""Local web UI for the whole flow: pick files -> make cards -> pick cards -> export.

Run: uv run src/ui.py   (prints the address; the stage profile is on another port)
"""

import socket
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core import config
from core.config import DATA_FOLDER, ENV_FILE
from core.card_library import delete_cards, edit_card, list_cards
from core.export import export_cards
from core.languages import PLUGINS, Plugin
from core.making_cards import RunReport, RunResult, make_cards
from core.writer import make_writer

load_dotenv(ENV_FILE)

PORT = config.PORTS[config.PROFILE]
HERE = Path(__file__).parent


def clock(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}:{secs:02d}"


def left(seconds: float) -> str:
    """The time left, coarsely: the estimate is too rough for seconds."""
    if seconds < 60:
        return "under a minute"
    return f"about {round(seconds / 60)} min"


ETA_TERMS = 5  # the estimate goes by this many of the latest terms


@dataclass
class Job:
    """The current or the last run, as the page shows it."""

    state: str = "idle"  # idle | running | done | error
    plugin: int = 0
    terms: str = ""  # the choices the run was started with
    source: str = ""
    done: int = 0
    total: int = 0
    term: str = ""
    report: RunReport | None = None
    result: RunResult | None = None
    error: str | None = None
    cancel: threading.Event = field(default_factory=threading.Event)
    started: float = field(default_factory=time.monotonic)
    finished: float | None = None
    mark: float | None = None  # when the term in hand was started
    durations: list[float] = field(default_factory=list)  # of the terms finished
    eta: float | None = None  # seconds left, renewed whenever a term is finished

    def start_term(self, done: int, total: int, term: str, now: float | None = None):
        """A term is about to be made; the one before it, if any, is finished."""
        now = time.monotonic() if now is None else now
        self.done, self.total, self.term = done, total, term
        if done >= 1 and self.mark is not None:
            self.durations.append(now - self.mark)
            # the first term is often slower (warm-up): out of the mean while only
            # one or two terms are done and others exist
            pool = (
                self.durations[1:] if 2 <= len(self.durations) < 3 else self.durations
            )
            latest = pool[-ETA_TERMS:]
            self.eta = sum(latest) / len(latest) * (total - done)
        self.mark = now

    def timing(self, now: float | None = None) -> str:
        """How long the run has gone on and, once a term is done, about how long is left.
        The estimate changes only when a term is finished, so it never climbs between."""
        now = time.monotonic() if now is None else now
        elapsed = (self.finished or now) - self.started
        text = f"Elapsed {clock(elapsed)}"
        if self.state == "running" and self.eta is not None:
            text += f", {left(self.eta)} left"
        return text

    def not_processed(self) -> list[tuple[str, str]]:
        """(term, why) for every term the finished run made no card for."""
        if not self.result:
            return []
        return (
            [(term, f"failed: {reason}") for term, reason in self.result.failed]
            + [(term, "limit reached") for term in self.result.limit_reached]
            + [(term, "cancelled") for term in self.result.cancelled]
        )


_plugins: dict[int, Plugin] = {}
_job = Job()
_lock = threading.Lock()
_marked: dict = {
    "plugin": None,
    "ids": set(),
}  # the cards of the latest run that made any


def get_plugin(idx: int) -> Plugin:
    if idx not in _plugins:
        _plugins[idx] = PLUGINS[idx]()
    return _plugins[idx]


def data_files() -> list[str]:
    return [f.name for f in config.user_files()]


def data_file(name: str) -> Path:
    if name not in data_files():
        raise FileNotFoundError(f"No such file in the data folder: {name}")
    return DATA_FOLDER / name


def run_job(job: Job, terms: str, source: str | None) -> None:
    def report(run_report: RunReport) -> None:
        job.report = run_report

    def progress(done: int, total: int, term: str) -> None:
        job.start_term(done, total, term)

    try:
        if not terms:  # nothing to choose from: the data folder has no files
            raise FileNotFoundError(
                "No terms file chosen. Choose one, or put one into the data folder and choose it."
            )
        job.result = make_cards(
            get_plugin(job.plugin),
            make_writer(),
            data_file(terms),
            data_file(source) if source else None,
            on_report=report,
            on_progress=progress,
            should_cancel=job.cancel.is_set,
            model=config.MODEL,
        )
        job.finished = time.monotonic()
        if job.result.made:  # a run that made nothing leaves the earlier marks
            _marked.update(plugin=job.plugin, ids=set(job.result.made))
        job.state = "done"
    except Exception as e:  # surfaced in the UI
        job.error = str(e) or type(e).__name__
        job.finished = time.monotonic()
        job.state = "error"


app = FastAPI()


class FreshStaticFiles(StaticFiles):
    """Static files the browser must revalidate: Safari otherwise keeps running an old script."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


app.mount("/static", FreshStaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.globals["stage"] = config.PROFILE == "stage"  # ty: ignore[invalid-assignment]


def status_context(job: Job) -> dict:
    return {
        "job": job,
        "not_processed": job.not_processed(),
        "run_pair": PLUGINS[job.plugin].NAME,
        "left": len(job.not_processed()),
        "kept_marks": bool(_marked["ids"]),
    }


def cards_context(idx: int) -> dict:
    """The cards of a language pair; those of the last run are marked new."""
    plugin = get_plugin(idx)
    new = set(_marked["ids"]) if _marked["plugin"] == idx else set()
    return {
        "plugin": idx,
        "fields": plugin.FIELDS,
        "cards": list_cards(plugin, newest_first=True),
        "new": new,
        "pair": plugin.NAME,
    }


def status(request: Request, job: Job, **extra) -> Response:
    """The status of the run. Whenever it says the run is done, the page is told to
    refresh the cards, whichever request it was the answer to."""
    response = templates.TemplateResponse(
        request, "status.html", status_context(job) | extra
    )
    if job.state == "done":
        response.headers["HX-Trigger"] = "run-finished"
    return response


@app.get("/")
def page(request: Request) -> Response:
    job = _job
    idx = job.plugin if job.state != "idle" else 0
    context = {"plugins": [p.NAME for p in PLUGINS]} | files_context()
    return templates.TemplateResponse(
        request, "page.html", context | status_context(job) | cards_context(idx)
    )


def files_context() -> dict:
    return {"files": data_files(), "data_folder": str(DATA_FOLDER)}


@app.get("/files")
def files(request: Request) -> Response:
    """The file choices, read from the data folder again."""
    return templates.TemplateResponse(request, "files.html", files_context())


@app.post("/run")
def start_run(
    request: Request,
    plugin: Annotated[int, Form()],
    terms: Annotated[str, Form()] = "",
    source: Annotated[str, Form()] = "",
) -> Response:
    global _job
    with _lock:
        if _job.state == "running":
            headers = {"HX-Retarget": "#note", "HX-Reswap": "innerHTML"}
            return Response("A run is already in progress", headers=headers)
        _job = job = Job(state="running", plugin=plugin, terms=terms, source=source)
    threading.Thread(
        target=run_job, args=(job, terms, source or None), daemon=True
    ).start()
    return status(request, job, clear_note=True)


@app.get("/status")
def run_status(request: Request) -> Response:
    return status(request, _job)


@app.post("/cancel")
def cancel(request: Request) -> Response:
    job = _job
    if job.state == "running":
        job.cancel.set()
    return status(request, job)


@app.get("/cards")
def cards(request: Request, plugin: int, after_run: bool = False) -> Response:
    if after_run and plugin != _job.plugin:
        return Response(
            status_code=204
        )  # the run was of another language pair: leave the table alone
    context = cards_context(plugin) | {"clear_export": not after_run}
    return templates.TemplateResponse(request, "cards.html", context)


@app.post("/cards/edit")
def edit(
    plugin: Annotated[int, Form()],
    card: Annotated[int, Form()],
    field: Annotated[int, Form()],
    value: Annotated[str, Form()] = "",
) -> Response:
    result = edit_card(get_plugin(plugin), card, field, value)
    return JSONResponse(
        {
            "ok": result.ok,
            "error": result.error,
            "value": result.value,
            "fix": result.fix,
        }
    )


@app.post("/cards/delete")
def delete(
    plugin: Annotated[int, Form()],
    ids: Annotated[list[int] | None, Form()] = None,
) -> Response:
    return JSONResponse({"count": delete_cards(get_plugin(plugin), ids or [])})


@app.post("/export")
def export(
    plugin: Annotated[int, Form()],
    ids: Annotated[list[int] | None, Form()] = None,
) -> Response:
    """The file for the browser to save; no content when nothing was selected."""
    result = export_cards(get_plugin(plugin), ids or [])
    headers = {"X-Count": str(result.count), "X-Suggested-Name": result.suggested_name}
    return Response(
        result.content or b"", media_type="text/tab-separated-values", headers=headers
    )


def make_server(port: int = PORT) -> tuple[uvicorn.Server, socket.socket]:
    """The server and the socket it serves on, already listening. Port 0 picks a free one."""
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    sock = socket.create_server(("127.0.0.1", port))
    return uvicorn.Server(uvicorn.Config(app, log_level="warning")), sock


def main() -> None:
    server, sock = make_server()
    print(f"UI ({config.PROFILE} profile) on http://127.0.0.1:{PORT}")
    server.run(sockets=[sock])


if __name__ == "__main__":
    main()
