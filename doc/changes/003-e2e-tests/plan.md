# 003 End-to-end tests: plan

## Approach

The tests run the real server from `src/ui.py` inside the pytest process, on a
free port, and drive the page with Playwright's Chromium. Running in-process
lets a test replace the LLM client and look at the card store directly.

```
pytest ── Playwright ── Chromium ── http://127.0.0.1:<free port> ── ui.Handler
   │                                                                   │
   └── fake LLM, temp data folder, temp card store ────────────────────┘
```

## Changes to the code

Three seams, no behaviour change when the tool is started the usual way.

1. **Locations in one place.** `config.py` gets `DATA_FOLDER` and `DB_PATH`.
   Their defaults are today's paths. The environment variables
   `PROCESS_ANKI_DATA` and `PROCESS_ANKI_DB` override them. `ui.py`,
   `main.py`, `export_cards.py`, `search.py` and `db.py` read them from
   `config` instead of each computing its own.
2. **Server factory.** `ui.py` gets `make_server(port)`; the `__main__` block
   calls it with `PORT`. Tests call it with port 0.
3. **LLM client.** `ui.run_job` already builds the client by calling the name
   `OpenAI` in `ui`'s namespace; tests replace that name. No code change.

## Test layout

```
tests/
  conftest.py        sets PROCESS_ANKI_DATA / PROCESS_ANKI_DB to a temp
                     folder before any src module is imported (also keeps
                     test_search.py out of the real data/.cache)
  e2e/
    conftest.py      fixtures: server, clean state per test, fake LLM,
                     helpers to write data files and seed cards
    test_making_cards.py
    test_export.py
```

Each test is named after the criterion it checks and carries its id in the
docstring.

### Fixtures

- `server` (session): `make_server(0)` in a daemon thread; yields the URL.
- `clean` (per test, automatic): empties the temp data folder, deletes all
  cards, resets the job status, and at the end releases a held run and waits
  for it to finish.
- `llm` (per test): the fake client, installed as `ui.OpenAI`.
- `data` (per test): writes files into the temp data folder.
- `seed_cards` (per test): inserts English → Russian cards straight into the
  store, for export tests that do not need a run.
- `app` (per test): opens the page and returns it.

### Fake LLM

`responses.parse(...)` reads the term from the prompt and returns a valid card
of the requested type. Terms control it:

- a term starting with `fail-` raises, as an unreachable LLM would;
- a term starting with `bad-` gives a card that breaks a field rule;
- `llm.hold()` makes calls wait until `llm.release()`, so a test can look at a
  run while it is in progress.

It records every prompt, so a test can check that the context reached card
writing.

## Running

```
uv sync
uv run playwright install chromium     # once per machine
uv run pytest                          # everything
uv run pytest tests/e2e --headed       # watch the browser
```

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | The two environment variables are how TE-2 is met. They are a test seam, not a feature: they are not shown to the user and the specs still say files come from "the tool's data folder". tech.md names tools, which Principle I says specs do not; see the note below. |
| II. Core and frontend | Not affected. The tests go through the frontend only, except for seeding and reading the store and the data folder. |
| III. Tested offline | Served: no network beyond localhost, no LLM calls. |
| IV. No new technology without agreement | Playwright agreed, see change.md, and listed in tech.md. |

Note on Principle I: it describes a spec as scenarios and criteria with no
implementation detail. tech.md is a list of technology by design. Whether the
constitution should say so is for the developer to decide; this plan does not
amend it.

## Risks

- **Timing.** The page polls the status once a second. Tests wait for what
  they expect to appear with Playwright's retrying assertions and never sleep.
- **spaCy models load at import**, a few seconds once per test session.
- **001 and 002 rework the page.** The tests find elements by the ids the
  page already has; those changes update the tests they break.
