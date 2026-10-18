# 013 UX polish, round 2

## Why

A second tester used the tool after 012. Asked 2026-10-04. Besides layout
defects (long text overflowing, mid-word header breaks, sideways page scroll
on narrow screens, layout jumps), the findings were: a stale table after a
run, a report that does not say what it is about, selection hiding which cards
are new, an editor left open over other actions, lost focus after a delete,
an export message far from Export, and accidental runs started by Enter in a
choice.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-15: report names file and pair, counts ignored repeats, says "no terms" for an empty file, is marked as old once choices change. MC-11: no count for an empty file. | written |
| [card-library.md](../../specs/card-library.md) | CL-7: the question says when it is every card. CL-11: leaving a refused edit abandons it; nothing starts over an open edit. CL-12: focus after delete. CL-13: messages can be closed. | written |
| [export.md](../../specs/export.md) | EX-4: new cards stay marked when selected. EX-7: result right beside Export. | written |

Bug fixes without a record entry (code did not do what the specs say): the
card table not refreshing when a finished run is answered by cancel (EX-4);
"at least 1 characters" wording (CL-4, MC-8). Purely visual fixes (overflow,
header wrapping, narrow layout, reserved warning line, range popover, text
selection by Shift-click, contrast, aligned buttons) change no specified
behaviour.

## Decisions taken without asking (low risk)

- The Enter-starts-a-run shortcut in the choices is dropped, not moved to
  Ctrl+Enter: it was never specified and cost money when pressed by accident.
- A run with no terms at all gets no "Cards made" line; a run whose terms all
  have cards keeps "Cards made: 0".
- "Earlier choices" means any of the pair, terms file and source text.
- Error messages have no timeout; they close with a button, a click or Esc.

## Open

- [NEEDS CLARIFICATION] Should "Cards made: 0" also go when every term already
  has a card (the report already says so)?

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| All criteria above | Built in this change. |

No new technology.
