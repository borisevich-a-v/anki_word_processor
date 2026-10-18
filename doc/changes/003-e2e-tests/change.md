# 003 End-to-end tests

## Why

The web UI has no tests. Everything the user does in it (starting a run,
watching progress, selecting cards, exporting) is checked by hand, and the only
automated tests cover context finding. Principle III asks for a test per
acceptance criterion; for the criteria that are about what the user sees and
clicks, that test has to drive the real page in a real browser.

This change adds end-to-end tests: they start the tool, open it in a browser
and act as the user would. They run offline, with card writing replaced by a
stand-in, against a throwaway data folder and card store, so the user's own
cards and files are never touched.

It does not change what the software does. It does add technology, and the
project had no place where its technology was written down, so this change
also starts that list.

## Specs

| Spec | Change | Status |
|---|---|---|
| [tech.md](../../specs/tech.md) | new: the technology in use, with Playwright added, and what is required of the tests (TE-1 to TE-4) | written |

The other specs do not change. The tests check criteria they already state.

## New technology (Principle IV)

| Addition | Why the existing stack is not enough | Agreed |
|---|---|---|
| Playwright, through `pytest-playwright` (dev dependency), with its Chromium browser | pytest alone cannot open a page, click, or see what is rendered. | Yes, by the developer on 2026-10-03, chosen over Selenium and Cypress. |

## Which criteria are covered

Only criteria that today's code already meets get a test here. A criterion
that 001 or 002 lists under "Where the specs differ from today's code" gets its
end-to-end test in that change, when the behaviour exists.

| Spec | Covered here | Left to |
|---|---|---|
| making-cards | MC-1 (with a source text), MC-4, MC-5, MC-6, MC-7, MC-8, MC-9, MC-10, MC-11 (failed, limit reached), MC-12, MC-13 | 001: MC-1 and MC-14 without a source text, MC-2, MC-3, MC-16. 002: MC-15, MC-17, MC-11 cancelled |
| export | EX-1 (English → Russian), EX-2, EX-3, EX-4, EX-5, EX-6 (tab-separated, id order, no id), EX-7, EX-8 | 001: EX-1 headings for Russian → Chinese, EX-6 UTF-8 and the Anki marker, EX-9 |
| tech | TE-1, TE-2, TE-3 by how the suite is built | TE-4: the suite has only been run on macOS so far |
| context-finding | none; it has no UI of its own and is covered by `tests/test_search.py` | |

The filter box and the command-line entry point (`src/main.py`) get no tests:
the first is not in any spec and 001 removes it, the second is not a frontend
under Principle II.

## Depends on

Nothing. 001 and 002 will change the page; the tests they break are updated
in those changes.

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps.
