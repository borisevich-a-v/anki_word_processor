# 012 UX polish

## Why

A tester used the tool and found it hard to use: the page locks its height
and squeezes the card table, the run report prints every term, failure
reasons are raw error dumps, the first file is preselected as the terms file,
the selection of the last run survives a reload, editing cards is
undiscoverable and loses what the user typed, messages never go away, the
keyboard is hardly usable, and the narrow layout is poor. Asked 2026-10-04.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-21 (choices remembered, nothing preselected), MC-22 (not the same file twice), MC-23 (copy failed terms, run again), MC-24 (first use) added. MC-8 reasons in plain words; MC-15 and MC-11 counts with names on request; MC-10 elapsed and remaining time, cancel next to progress. | written |
| [card-library.md](../../specs/card-library.md) | CL-1 names the pair and hints at editing; CL-5 Escape only; CL-11 (saving an edit on leaving, Tab, long text), CL-12 (keyboard), CL-13 (messages) added; CL-7 a question to answer first, apart from export. | written |
| [export.md](../../specs/export.md) | EX-4 nothing selected when the page is opened later; EX-3 count on the buttons; EX-5, EX-7, EX-11 where and how the result is shown. | written |

Purely visual fixes (page scrolls normally, sticky table header, responsive
toolbar, promoting "select last run" and "select all" over the id range,
focus styles) change no specified behaviour and have no criterion.

## Decisions taken without asking (low risk)

- "Retry failed" is "Run again": the same run started with one action. Terms
  with a card are skipped (MC-4), so it makes exactly the failed, cancelled
  and limit-left terms. No core change.
- The remembered choices live in the browser, per address (so stage and prod
  do not mix).
- A field stays on one line: the editor is a box that shows long text in full,
  Enter saves.

## Open

- [NEEDS CLARIFICATION] May a card field hold line breaks? Not supported now.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| All criteria above | Built in this change. |

No new technology (`<dialog>`, `<details>`, `localStorage` are browser built-ins; `hx-preserve` is htmx).
