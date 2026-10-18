# 004 Remove the command line: plan

- Delete `src/main.py`.
- Remove `click` from the dependencies.
- `run.bat` starts the web UI (`uv run src/ui.py`) instead. It no longer
  writes a log file: the web UI shows everything the run reports.

No test changes: the command line had none.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: tech.md edited first. |
| II. Core and frontend | Served: the one frontend left is the web UI. |
| III. Tested offline | Not affected. |
| IV. No new technology | Technology is removed, none added. |
