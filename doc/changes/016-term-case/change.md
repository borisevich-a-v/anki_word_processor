# 016 Terms are compared ignoring letter case

## Why

015 left open whether "Biceps" and "biceps" are the same term. Owner decision:
they are. Terms are compared case-insensitively. Trimming of surrounding spaces
stays as in 015.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-2: lines that differ only in case are one term; the first spelling is kept, later ones count as ignored repeats. MC-4: a card has the term whatever the case; cards keep their spelling; existing case-variant cards stay. Open question on letter case closed. | written |
| [card-library.md](../../specs/card-library.md) | CL-4: a term may not equal another card's term in any case; changing only the case of a card's own term is allowed. | written |
| [context-finding.md](../../specs/context-finding.md) | None in behaviour (CF-3 already ignores case); History line only. | written |
| [export.md](../../specs/export.md) | None: export compares no terms; cards are written as stored. | n/a |

## Decisions taken without asking (low risk)

- "Same letter case" means Unicode case folding (so "Straße" and "STRASSE", Russian
  "Ёж" and "ёж" match), not ASCII lowercasing. No other normalisation (accents,
  composed or decomposed forms) is applied.
- Of case variants in a terms file the first line wins and is the spelling that
  is processed and written on the card (MC-16); the others are counted in "repeated
  lines ignored".
- A term that has a card in any case is "existing" and is not made again; the
  existing card keeps its spelling and is not edited.
- Editing a card's term to a different case of its own term is allowed; to a case
  variant of another card's term is refused with "Another card has this term".
- No uniqueness constraint is added to the card store. Cards already in the store
  that differ only in case (e.g. "biceps" and "Biceps") are left alone; nothing
  fails because of them. A migration to merge them is NOT done; the owner decides
  whether to delete one of each pair by hand in the card list.

## Open

None.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| MC-2, MC-4, CL-4 | Built in this change. |

No new technology.
