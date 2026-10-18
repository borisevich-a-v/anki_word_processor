# 011 Stage profile: plan

- Core (`core/config.py`): `PROFILE` read from `PROCESS_ANKI_PROFILE`
  (default `prod`, other values than `prod`/`stage` raise). `DATA_FOLDER` =
  `data/<profile>`, `DB_PATH` = `data/<profile>/internal.db`; created on
  import. `PROCESS_ANKI_DATA` / `PROCESS_ANKI_DB` stay as overrides, for the
  tests only.
- Core: the fake writer moves from `tests/fake_llm.py` to `core/fake_llm.py`
  (tests import it from there). `core/writer.py` (new): `make_writer()`
  returns the OpenAI client for `prod`, the fake for `stage`, or the real one
  with the model from `PROCESS_ANKI_MODEL` when `PROCESS_ANKI_REAL_LLM=1`.
  `making_cards` takes the model as a parameter instead of the hard-coded
  `gpt-5-mini` (prod keeps that value).
- Web: `web/app.py` takes the writer from the core, uses port 8766 for stage,
  prints the profile, passes the profile to the templates; the page shows a
  banner and a title prefix for stage. No logic: it only renders what the core
  reports.
- The card store lies in the data folder, so `config.user_files()` hides it
  (and its journal) from the file lists and the context cache cleanup.
- `README.md`: how to start stage and move existing files into `data/prod/`.
- Tests: unit tests for config (profile, folders, bad value), writer choice,
  prod ignoring the stage variables; e2e test that stage shows the marker and
  makes cards without a key.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: specs and open point recorded first. |
| II. Core and frontend | Served: writer choice is in the core; frontend only shows the marker. |
| III. Tested offline | Served: the fake is used. Real-LLM mode is not tested. |
| IV. No new technology | Served. |
