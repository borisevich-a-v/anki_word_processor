# 005 FastAPI and htmx for the web UI: plan

## Server

`src/ui.py` becomes a FastAPI app. The run state (`Job`, `run_job`, the lock,
the worker thread) stays as it is; only how requests reach it changes.

| Route | Returns |
|---|---|
| `GET /` | The whole page, with the current run and the cards already in it. |
| `POST /run` | Starts a run and returns the run status. When a run is already going, returns the refusal message and points it at the note line instead. |
| `GET /status` | The run status: report, progress, summary or error. |
| `POST /cancel` | Asks the run to stop and returns the run status. |
| `GET /cards` | The card table of a language pair. |
| `POST /export` | Exports the ticked cards and returns the result line. |
| `/static` | htmx and the page's own script. |

The JSON endpoints under `/api` go away: nothing but the old page used them.

`make_server(port)` returns the uvicorn server together with a socket that is
already listening, so that the browser can be opened, and the tests can learn
the port, before the server starts serving.

## Page

Templates in `src/templates/`: `page.html` (the whole page), `status.html`
(run status), `cards.html` (card table), `export.html` (result line). Jinja2
escapes every value.

- **Run status.** While a run is going, the status block asks for itself
  again every half second. The answer for a finished run no longer asks, and
  tells the card table to reload.
- **Cancel button.** It sits outside the block that is replaced every half
  second, so a click cannot land on a button that is being swapped out. It is
  shown by a style rule while the status block is marked as running.
- **Card table.** Reloaded when the language pair changes and when a run of
  the shown pair finishes. Cards of the last run come ticked and marked new.
- **Selection.** Stays in the browser, as ticked checkboxes in the table. A
  short script in `src/static/app.js` does what needs no server: toggling a
  row, a stretch with shift, a range of ids, all, none, last run, and the
  count. Export posts the ticked checkboxes.

htmx is kept in `src/static/htmx.min.js`, so the tool needs no network to show
its page (tech.md: card writing is the only thing that does).

## Tests

The end-to-end tests keep their assertions. Element ids are kept so the tests
find the same things. `tests/e2e/conftest.py` starts the new server. No new
test: no criterion changed.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: tech.md edited first. No behaviour changes, so no other spec is touched. |
| II. Core and frontend | Served. `ui.py`, the templates and the script are the frontend; they call `make_cards`, `list_cards` and `export_cards` as before. Which cards are ticked is frontend state, not business logic. |
| III. Tested offline | Served: htmx is a local file; the existing end-to-end tests cover the page. |
| IV. No new technology without agreement | FastAPI and htmx agreed on 2026-10-04; uvicorn, Jinja2 and python-multipart come with that choice. All five are listed in change.md. |
