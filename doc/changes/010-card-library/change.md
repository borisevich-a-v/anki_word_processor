# 010 Card library: edit and delete cards in the UI

## Why

Cards written by the model sometimes need a correction, or are not wanted at
all. The developer asked on 2026-10-04 that cards can be edited and deleted
directly in the UI, and that the division of specs be reconsidered: `export.md`
was also the home of the card list and ids, which are not about exporting.

## Decisions (developer, 2026-10-04)

- New spec `card-library.md` owns the card list, ids, editing and deleting.
  `export.md` keeps selecting and writing the file; `making-cards.md` stays
  about runs and the field rules.
- Every field, the term included, can be edited. An edit must obey the field
  rules of its language pair and may not duplicate another card's term.
- Delete works on the selected cards and asks for confirmation with the count.
- Editing and deleting are allowed while a run is going (CL-10).

## Specs

| Spec | Change | Status |
|---|---|---|
| [card-library.md](../../specs/card-library.md) | new. CL-1, CL-2 (from EX-1, EX-2; CL-2 now also covers deleted cards). CL-3 to CL-6 editing. CL-7 to CL-9 deleting. CL-10 during a run. | written |
| [export.md](../../specs/export.md) | EX-1, EX-2 removed (moved). Intro and scenario link to the library. Other criteria keep their ids. | written |
| [making-cards.md](../../specs/making-cards.md) | MC-9: cards are kept unless the user deletes them. Links to the library. | written |

Tests that cite EX-1 or EX-2 cite CL-1 or CL-2 from now on. Earlier change
records keep the old ids; they are frozen.


## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| CL-3 to CL-10 | No editing or deleting. Built in this change. |
| CL-2 | Ids are the SQLite row numbers. Deleting the newest card would let the next card take its id, and a database `VACUUM` may renumber rows. The card tables need ids that are never reused or renumbered, which means moving existing cards into new tables. |

No new technology.
