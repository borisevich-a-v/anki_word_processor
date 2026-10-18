# 018 The lists of files follow the folder: plan

- **Web / frontend only.** The existing `/files` answer is fetched by the page;
  the two drop-downs and the hint are updated in place from it (no logic in the
  page: the server still decides the files and the hint). It runs when a
  drop-down gets the pointer or focus, and when the window becomes visible or
  focused. Nothing is replaced when the files are the same. The Refresh button
  and its htmx attributes go.
- The server's "put one into the data folder and press Refresh files" texts are
  reworded.
- **Core.** No change.
- **Tests.** E2E tests naming MC-24 (in Chromium; the in-place update is also
  tried in WebKit by hand); the three tests that clicked the button now use
  the automatic path.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: presentation only. |
| III. Tested offline | Served. |
| IV. No new technology | Served. |
