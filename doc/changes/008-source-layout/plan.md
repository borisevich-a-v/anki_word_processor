# 008 Source layout: plan

- `src` stays the import root (`pythonpath = ["src"]` for pytest; the launcher's
  own folder for the tool), so no packaging or build backend is needed.
- `src/run.py` is a three-line launcher calling `web.app.main`.
- `core/` imports nothing from `web/`; a test checks it.
- Test files are renamed after the modules they cover; imports follow.
- `AGENTS.md` and `README.md` are updated to the new paths and command.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: no behaviour changes, so no spec text changes; recorded here. |
| II. Core and frontend | Served: the boundary becomes two folders and a test. |
| III. Tested offline | Not affected. |
| IV. No new technology | Served: no packaging backend added. |
