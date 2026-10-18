# 015 UX polish, round 4

## Why

A fourth tester (real LLM, full run) found: an open editor froze the live list
silently; editing a field of an old card whose exercise lacked underscores was
refused with a message about the exercise only; with no remembered choice the
whole report was dimmed, even a run in progress; selecting the last run said
nothing when it selected none, and a run of no cards removed the green marks;
terms and fields kept surrounding spaces; and small matters (run-again label,
cancel said twice, error message never leaving, tips on a phone, header over an
empty list, progress out of sight, estimate skewed by a slow first term).

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-2 and MC-6: surrounding spaces dropped from terms and fields. MC-10: first term left out of the estimate early on, minutes only, count stays in sight. MC-15: no dimming for a choice not made, a run in progress or actions. MC-17: cancelling said once. MC-23: run again names file and terms left. | written |
| [card-library.md](../../specs/card-library.md) | CL-1: no headings over an empty list. CL-4: another field that must be fixed is named. CL-10: a waiting list says so. CL-11: fields trimmed. CL-13: errors go after about eight seconds. | written |
| [export.md](../../specs/export.md) | EX-4: nothing-to-select is said; a run of no cards keeps earlier marks. | written |

Purely visual, no spec: tips folded behind a summary on a phone (touch-irrelevant
hints hidden); the card list is not a scroller of its own on a phone.

## Decisions taken without asking (low risk)

- Letter case of terms is not touched (see Open).
- A refused edit because of another field highlights that field's cell instead of
  opening a second editor over the first.
- Estimate: the first term is excluded while exactly two are done (with one done it
  is all there is; from three on, the mean of the latest five). Shown as "under a
  minute" or "about N min"; still renewed only when a term finishes.
- The marks kept after a run of no cards are those of the latest run that made
  cards, the ones "Select last run" uses.
- The list is not refreshed over an open editor (safe); a note says how many new
  cards wait, and it refreshes when editing ends.
- Auto-dismiss applies to the card message only, not the export message.

## Open

- [NEEDS CLARIFICATION] Should "Biceps" and "biceps" be the same term (MC-2, MC-4)?
  The specs say exact text; not decided.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| All criteria above | Built in this change. |

No new technology.
