# 002 Pre-run report: plan

Built together with 001, on its core API.

## Approach

- **Report.** `make_cards` reads the files, works out a `RunReport` (terms in
  the file, terms to process, terms that already have a card, terms over the
  limit) and hands it to `on_report` before the first term. With nothing to
  process it returns right after the report; the source text is not even
  indexed.
- **Cancel.** `make_cards` asks `should_cancel()` before each term. When it
  says yes, the remaining terms go to `RunResult.cancelled` and the run
  returns. The term being worked on at that moment is always finished and gets
  its card, which is one of the two outcomes MC-17 allows.
- **Web UI.** The job state keeps the report and a cancel flag. The page shows
  the report above the progress line and leaves it there next to the summary;
  a Cancel button is visible while a run is going. Lists of terms are shown
  one term per line, because a term may contain commas. The summary lists
  every term not processed with "failed: reason", "limit reached" or
  "cancelled". A refused second run (MC-12) is shown in its own line, so the
  progress of the running one stays visible.
- **Naming.** The page says "term", "terms file" and "language pair". In code
  the new API says "term"; the stored field and the card model keep the name
  `word`, so existing cards need no migration.

## Tests

Core: MC-15 (report content, report before the first term, nothing left),
MC-17 and MC-11 cancelled in `tests/test_making_cards_core.py`. Browser: the
report during and after a run, the empty report, cancel and the next run, the
wording of the page.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served. What is to be processed, what exists and what is over the limit is decided in the core; the page formats it. |
| III. Tested offline | Served. |
| IV. No new technology | Nothing added. |

## Risks

- A cancel takes effect when the current term is finished. With a slow answer
  from card writing the user waits for it; the page says "Cancelling…"
  meanwhile.
