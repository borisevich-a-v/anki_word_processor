# 014 UX polish, round 3

## Why

A third tester used the tool with the real LLM (a run of about 15 minutes,
about 20 s a card). Findings: the time left climbed and fell during a term; the
table showed no card until the run ended; some exercises lacked the underscores
around the translation and were saved anyway; "Run again" took the form's
current choices instead of the report's; cancelling a long term looked like
nothing happened; a finished run selected its cards, arming Delete; the delete
question named no card; the error message covered the rows below the edit; the
export message lingered; the phone layout showed three columns of a wide table;
and several small layout gaps.

## Owner decisions recorded

- Card fields cannot contain line breaks; a line break is replaced by a space.
  Closes the [NEEDS CLARIFICATION] of making-cards.md; now stated in CL-11.
- "Cards made: 0" stays shown even when every term already has a card. Closes
  the open question of change 013; now stated in MC-11.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-7 and the exercise row: the exercise must have its translation between underscores. MC-10: estimate renewed only when a term finishes, from the latest terms. MC-11: count also when none. MC-15: empty file gets no counts. MC-17: the term in hand is shown, cancel cannot be repeated. MC-23: run again uses the report's own choices. | written |
| [card-library.md](../../specs/card-library.md) | CL-11: one line per field. CL-7: question in the singular for one and names the cards. CL-10: the list follows the run card by card. CL-13: a message never covers the editing. | written |
| [export.md](../../specs/export.md) | EX-4: a run selects nothing. EX-7: short result, gone when selection or cards change. | written |

Bug fix, no spec change (code did not do what the specs say): the exercise
rule (MC-7, the table already said "set between underscores" but nothing
checked it). Purely visual fixes that change no specified behaviour: stacked
card layout on a phone, no reserved blank lines, width of the old-results note,
message position.

## Decisions taken without asking (low risk)

- A card whose exercise lacks underscores fails with a plain reason; there is
  no automatic retry (the design has none). "Run again" makes it.
- "Between underscores" means some text between a pair of underscores; it is
  not compared with the translation field, which the model words differently.
- The estimate is the mean of the last five terms times the terms left, and is
  kept as it is until the next term finishes (it does not count down).
- Cards of a running run appear in the table without the green mark; the mark
  comes when the run finishes.
- A refresh that would replace an open editor waits until the editor closes.
- "Run again" is not disabled when the report is old: its label names the file
  and pair it will use.
- The message sits at the top of the window.

## Open

- [NEEDS CLARIFICATION] Language of the explanation on English → Russian cards
  (spec says English or Russian; testers saw both mixed). Not decided.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| All criteria above | Built in this change. |

No new technology.
