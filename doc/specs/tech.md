# Technology

The main technology the project uses. Together with the dependencies declared
in [pyproject.toml](../../pyproject.toml) and the checks configured in
[.pre-commit-config.yaml](../../.pre-commit-config.yaml), this is the list the
"no new technology without agreement" rule in [AGENTS.md](../../AGENTS.md)
refers to: anything in
none of the three is new technology and needs the developer's agreement before
it appears in a plan or in code. Unlike the other specs, this one names tools
and libraries; it still says nothing about how the code is organised.

Supporting libraries and the pre-commit checks are not repeated here; those
two files are the one place they are listed.

## Platforms

macOS and Windows. Everything below works on both.

## What the tool runs on

| Technology | Used for |
|---|---|
| Python 3.13, managed with uv | The whole tool. |
| SQLite, with its full-text search (FTS5) | Keeping the cards; searching the source text for contexts. |
| spaCy, with its English, Russian and Chinese models | Dictionary forms of words for context finding. |
| OpenAI API | Writing the cards. The only thing the tool needs the network for. |
| FastAPI, served by uvicorn, with Jinja2 templates and htmx; no build step | The web UI. The server renders the pages; htmx, shipped with the tool, swaps the parts that change. |

## What the checks run on

| Technology | Used for |
|---|---|
| pytest | All tests. |
| Playwright with Chromium | End-to-end tests: driving the web UI in a real browser. |

## Developer conveniences

| Technology | Used for |
|---|---|
| make | Shortcuts for starting the tool and running the checks. Optional: every shortcut is a plain uv command, so nothing depends on it (on Windows it needs GNU make and a POSIX shell). |
