# 004 Remove the command line

## Why

The developer decided on 2026-10-03 that the tool is used through the web UI
only. The command-line entry point had no spec, printed and prompted outside
the web UI (Principle II names the web UI as the frontend), and would have had
to be rewritten for the core API of 001.

## Specs

| Spec | Change | Status |
|---|---|---|
| [tech.md](../../specs/tech.md) | click and "the command-line entry point" removed from the technology in use | written |

No other spec mentioned the command line.

## Where the specs differ from today's code

| Spec | Rule | Today's code |
|---|---|---|
| tech | click is not used. | `src/main.py` uses it; it is a declared dependency; `run.bat` starts `src/main.py`. |

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps.
