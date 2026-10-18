# Technology

The main technology the project uses. Together with the dependencies declared
in [pyproject.toml](../../pyproject.toml) and the checks configured in
[.pre-commit-config.yaml](../../.pre-commit-config.yaml), this is the list
Principle IV of the [constitution](../constitution.md) refers to: anything in
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


## History

- 003-e2e-tests: spec written; lists the technology in use and adds
  Playwright.
- 004-remove-cli: click and the command-line entry point removed; the web UI
  is the only way to use the tool.
- 2026-10-04: unused whoosh dependency removed; the list cut down to the main
  technology, with supporting libraries left to `pyproject.toml` and the
  pre-commit checks to `.pre-commit-config.yaml`.
- 005-fastapi-htmx: the web UI moves from the built-in HTTP server and
  hand-written JavaScript to FastAPI and htmx.
- 020-makefile: make added as an optional shortcut for the usual commands.
