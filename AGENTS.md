# Working in this repository

A local, single-user tool that prepares Anki cards. Python 3.13, managed with
`uv`.

This project is developed spec-first (spec-driven development, SDD). Read
[doc/constitution.md](doc/constitution.md) before doing anything; it overrides
habit and existing code. What follows is a summary, not a replacement.

## Where things are

| Path | What |
|---|---|
| `doc/constitution.md` | Rules every spec, plan and change must satisfy. |
| `doc/specs/<aspect>.md` | Living specs: what the software does **now**. User scenarios and numbered acceptance criteria (`MC-4`, `EX-6`, ...), no implementation detail. One aspect, one spec. |
| `doc/specs/tech.md` | The main technology in use. The one spec that names tools and libraries; anything not in it, `pyproject.toml` or `.pre-commit-config.yaml` needs agreement first. |
| `doc/changes/NNN-name/` | One folder per change: `change.md` (why, which specs change), `plan.md` (how, with a constitution check), `tasks.md` (ordered steps). |
| `src/` | The code. `core/` is the core (`making_cards`, `context_finding`, `export`, `store`, `languages/`); `web/` is the web frontend; `run.py` starts it. `core/` never imports `web/` (tested). |
| `tests/` | `pytest`. `tests/e2e/` drives the web UI in a browser with Playwright. |

## How a change is made

Any change in behaviour goes through these steps, in order. Do not skip to
code.

1. **Spec.** Edit the affected `doc/specs/*.md` in place so they describe the
   new behaviour, and add a line to each one's History. Write
   `doc/changes/NNN-name/change.md`: why, which specs changed and how, and
   where the specs now differ from today's code. `NNN` is the next free number.
2. **Plan.** `plan.md`: how it will be built, with a constitution check
   listing any principle the plan bends and why.
3. **Tasks.** `tasks.md`: small ordered steps, tests first.
4. **Implement.** Each task leaves `ruff`, `ty` and `pytest` green.

A bug fix (the code does not do what the spec says) needs no change record.
Anything else without a spec behind it does not get written.

## Rules that are easy to break

- **Do not guess.** Anything unclear in a spec is marked
  `[NEEDS CLARIFICATION]` and asked, not decided silently.
- **Specs say what, not how.** No file names, functions, libraries or UI
  element names in `doc/specs/`, except the technology list in `tech.md`.
- **One place per fact.** A spec links to another spec instead of restating
  it.
- **Change records are frozen** once implemented. A correction is a new
  change.
- **No new technology without agreement** (tool, library, framework, external
  service). Ask the developer first; record the agreement in `change.md` and add it
  to `doc/specs/tech.md`.
- **Core and frontend stay apart.** The core never prints, prompts or reads
  `stdin`; it reports through return values and callbacks. The frontend has no
  business logic.
- **Tests are offline.** No network, no LLM calls. Every acceptance criterion
  maps to at least one test; name the criterion id in the test's docstring.
- **A change may be specified but not built yet.** Check the change's folder
  for `plan.md` and `tasks.md` and its "Where the specs differ from today's
  code" table before assuming the code matches a spec.

## Commands

```
uv sync                                # install
uv run playwright install chromium     # once per machine, for tests/e2e
uv run src/run.py                       # start the tool (prints its address)
uv run pytest                          # all tests
uv run pytest tests/e2e --headed       # end-to-end tests with a visible browser
uv run ruff check src tests
uv run ty check src tests
```

Tests use a temporary data folder and card store (see `tests/conftest.py`);
they never touch `data/` or `internal.db`.
