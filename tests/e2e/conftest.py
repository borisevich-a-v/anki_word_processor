"""Fixtures for tests that drive the web UI in a browser.

The real server runs in this process on a free port. Card writing is replaced
by FakeLLM (core/fake_llm.py); data files and cards live in the temp folder set up in
tests/conftest.py.
"""

import threading
from collections.abc import Callable, Iterator

import pytest
from playwright.sync_api import Page

from web import app as ui
from core.store import db
from core.fake_llm import FakeLLM

EN_RU = "cards_ru"


@pytest.fixture(scope="session")
def server() -> Iterator[str]:
    server, sock = ui.make_server(0)
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [sock]}, daemon=True
    )
    thread.start()
    yield f"http://127.0.0.1:{sock.getsockname()[1]}"
    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture
def llm(monkeypatch: pytest.MonkeyPatch) -> Iterator[FakeLLM]:
    fake = FakeLLM()
    monkeypatch.setattr(ui, "make_writer", lambda: fake)
    yield fake
    fake.release()


@pytest.fixture(autouse=True)
def clean(llm: FakeLLM) -> Iterator[None]:
    """Every test starts with no run, and leaves none going."""
    ui._job = ui.Job()
    ui._marked.update(plugin=None, ids=set())
    yield
    llm.release()
    for thread in threading.enumerate():
        if "run_job" in thread.name:
            thread.join(timeout=30)


@pytest.fixture
def seed_cards() -> Callable[..., list[int]]:
    """seed_cards("one", "two") stores English → Russian cards; returns their ids."""

    def seed(*terms: str) -> list[int]:
        for term in terms:
            db.execute(
                f"INSERT INTO {EN_RU} (word, phonetic_transcription, russian_translation,"
                " explanation, level, example, exercise) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    term,
                    f"/{term}/",
                    f"перевод {term}",
                    f"meaning of {term}",
                    "B2",
                    f"An example with {term}",
                    f"An example with _{term}_",
                ),
            )
        return [r[0] for r in db.fetchall(f"SELECT id FROM {EN_RU} ORDER BY id")]

    return seed


@pytest.fixture
def app(page: Page, server: str) -> Callable[[], Page]:
    """Opens the tool. Call it after the data files and cards are in place."""

    def open_app() -> Page:
        page.goto(server)
        page.locator("#plugin option").first.wait_for(state="attached")
        return page

    return open_app
