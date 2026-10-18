# 009 Save dialog on export: plan

- Core (`core/export.py`): `export_cards` no longer writes a file. It returns
  the file's content (`bytes`, same format as now) and the suggested name;
  `default_file_name(now)` builds `ankicards_YYYYMMDD_HHMMSS.tsv`. The time is
  a parameter so tests are exact.
- Web (`POST /export`): returns the content with the count and suggested name
  in headers; for no selection it returns the "Nothing selected" message as
  today.
- Frontend (`app.js`): the export button posts the selection, then offers the
  content to the browser's save dialog (`showSaveFilePicker`, suggested
  name), or, without it, as a download under that name. It shows the result
  message (EX-7), or "cancelled" (EX-11). No business logic: format and name
  come from the core.
- Tests: core tests check content and name; e2e tests replace
  `showSaveFilePicker` with a stub (a native dialog cannot be driven) and
  check the fallback with a Playwright download.
- `README.md` updated.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: specs edited first; one open point recorded. |
| II. Core and frontend | Served: core makes content and name, frontend only saves them. |
| III. Tested offline | Served: dialog stubbed. |
| IV. No new technology | Served: browser API only. |
