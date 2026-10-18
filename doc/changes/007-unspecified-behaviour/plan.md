# 007 Unspecified behaviour written down: plan

Two small code changes; the rest is tests for behaviour that is already
there.

- `src/ui.py`: starting the tool becomes a function, `main()`, that prints
  the address and serves. It no longer opens the browser (SU-4). A function,
  so that a test can call it.
- `src/config.py`: the `.env` file gets a name, `ENV_FILE`, in the tool's own
  folder, next to the data folder and the card store. `src/ui.py` reads the
  key from that file. Until now the file was looked for from `src/` upwards,
  so a `.env` in `src/` or in a folder above the tool was also read; SU-3
  says "in the tool's own folder", and only that file is read now.
- `README.md`, `AGENTS.md`: the tool prints its address; it does not open in
  the browser.
- What card writing is asked for (the prompts) is not changed.

## Tests

| Criterion | Test |
|---|---|
| MC-1 language | `tests/test_search.py`: the existing test of the language of each pair now names MC-1. |
| MC-18 | `tests/test_making_cards_core.py`: the existing byte order mark test is renamed to MC-18; a new one gives both files a byte order mark and checks it reaches neither the card nor the context. |
| MC-19, field tables | `tests/test_making_cards_core.py`: card writing is given web search; what it is asked for says no links and no citations, and carries the content rules of each pair. `tests/fake_llm.py` records what it was called with. |
| MC-10 starting | `tests/e2e/test_making_cards.py`: a run that has not reached its first term shows that it is starting. |
| MC-20 | `tests/e2e/test_making_cards.py`: the page is reloaded during a run and after it. |
| CF-1, CF-4, CF-5 | `tests/test_search.py`: line breaks and runs of spaces; five and six words in between; a term twice in one passage. |
| EX-10 | `tests/e2e/test_export.py`: Shift never unselects; open-ended ranges; a range replaces the selection. Click-to-toggle and Shift-click are already tested and now name EX-10. |
| EX-4 | `tests/e2e/test_export.py`: a run finishes while the other language pair is shown. |
| SU-1, SU-2, SU-3 | `tests/test_setup.py`: the three locations, read in a fresh process without the tests' overrides; a key from the environment reaches card writing; no key is a run error. |
| SU-4 | `tests/test_setup.py`: starting prints the address and opens no browser. |

Not tested: the last sentence of MC-20 (after a restart the page shows no
run). The run is remembered in memory only, so there is nothing that could
bring it back, and a test would have to restart the tool inside the suite.
That a line of the `.env` file becomes the key is the work of python-dotenv
and is not tested either; the test checks which file is read.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: this change exists to put specs behind code that had none. Specs name five files the user has to know; see change.md. |
| II. Core and frontend | Served: `main()` and reading the key are in the frontend; the core is not touched apart from one constant in `config.py`. |
| III. Tested offline | Bent in two places, listed above under "Not tested". All new tests are offline; the missing-key test fails before anything is sent. |
| IV. No new technology | None added. |
