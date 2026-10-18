# 014 UX polish, round 3: plan

- **Core.** The English → Russian card validates the exercise (a pair of
  underscores around text); `describe_error` words that rule plainly. The
  prompt asks for the underscores explicitly. The fake writer gets underscores
  in its exercise, a term prefix that breaks the rule, and a hold that lets a
  number of calls through first (for slow-run tests).
- **Web.** The job keeps the durations of finished terms and an estimate renewed
  when a term finishes. The status says how many terms are done on the page
  element; cancelling renders a disabled button and a busy bar. "Run again" posts
  the job's own pair, terms and source. The cards answer no longer selects.
  Empty-file and blank-line markup trimmed.
- **Frontend.** The page refreshes the table when the done count changes, unless
  an editor is open (then after it closes), keeping selection, focus and scroll.
  The delete question names the cards. The export message clears on selection,
  edit and delete changes, and is shorter. Message at the top. Stacked card layout
  under 640 px. Reserved lines only while they have text. Cap on the old-results
  note width.
- **Tests.** One test per changed criterion naming its id; existing tests that
  expected a selected run or the old wording are updated.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: the rule is in the core; the estimate stays where it was, in the web layer that shows it. |
| III. Tested offline | Served; the fake writer is the only writer. |
| IV. No new technology | Served. |
