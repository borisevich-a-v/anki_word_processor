# 015 UX polish, round 4: plan

- **Core.** Terms file lines are trimmed; card models strip surrounding spaces;
  `edit_card` trims, returns the stored value and, when another field of the card
  breaks its rule, says to fix that field and which one.
- **Web.** The estimate and its coarse wording; the marks of the latest run that
  made cards are kept on the server; the status carries total, made and terms
  left; the cards answer drops the heading row when empty; the edit answer carries
  the value and the field to fix.
- **Frontend.** Paused-list note and catch-up on close; stale mark only for a made
  choice and never while running or over actions; errors go in 8 s; a note when
  selecting the last run selects nothing; sticky Cards title with the count; tips
  folded on narrow screens.
- **Tests.** Core and e2e tests per criterion naming its id
  (`tests/test_ux_round4_core.py`, `tests/e2e/test_ux_round4.py`); older tests
  updated for the new wording.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: trimming and the edit rule are in the core. |
| III. Tested offline | Served. |
| IV. No new technology | Served. |
