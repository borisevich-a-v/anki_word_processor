# 013 UX polish, round 2: plan

- **Core.** `RunReport` gets a count of ignored repeats (`read_terms` keeps
  its result; a new helper returns the count too). `describe_error` says "must
  not be empty" for a minimum of one character.
- **Web.** Every response whose state is done carries the run-finished
  trigger (`/status`, `/cancel`, `/run`). The job remembers its terms file,
  source text and pair, and the status prints them. `status.html` prints the
  empty-file and duplicates wording.
- **Frontend.** Report marked stale when choices differ from the job's.
  Delete dialog says "all". Edit: blur with a refused value reverts and
  says so; delete and export wait for a pending save. Focus after delete.
  Message gets a close button and Esc. Enter-runs shortcut removed. Toolbar
  is two lines with a fixed place for the export message; id range in a
  popover; one reserved line for warnings. CSS fixes for wrapping, overflow,
  sticky first column, new-card bar, user-select, contrast.
- **Tests.** One test per new or changed criterion with its id in the
  docstring; bug fixes get tests too.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: counting repeats and wording are in the core. |
| III. Tested offline | Served. |
| IV. No new technology | Served. |
