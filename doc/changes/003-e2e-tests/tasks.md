# 003 End-to-end tests: tasks

0. [x] `doc/specs/tech.md`.
1. [x] Add `pytest-playwright` to the dev dependencies; install Chromium.
2. [x] `config.py`: `DATA_FOLDER`, `DB_PATH` with environment overrides; use
   them in `db.py`, `search.py`, `export_cards.py`, `ui.py`, `main.py`.
3. [x] `ui.py`: `make_server(port)`.
4. [x] `tests/conftest.py`: point the tool at a temp folder.
5. [x] `tests/e2e/conftest.py`: server, clean state, fake LLM, data and card
   helpers.
6. [x] `tests/e2e/test_making_cards.py`: MC-1, MC-4 to MC-13 as listed in
   change.md.
7. [x] `tests/e2e/test_export.py`: EX-1 to EX-8 as listed in change.md.
8. [ ] `ruff`, `ty`, `pytest` green. The new tests pass and the new files are
   clean, but the checks were already failing before this change and still
   are: `tests/test_search.py` imports `insert_text_chunk`, which `search.py`
   no longer has, so that file is not collected; `ruff` reports an unused
   import in `process_words.py`; `ty` reports two errors in `ui.py`.
