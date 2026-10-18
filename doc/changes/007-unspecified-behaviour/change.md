# 007 Unspecified behaviour written down

## Why

A comparison of the code with the specs on 2026-10-04 found behaviour the
user can see that no spec states. Principle I says code without a spec behind
it is a bug fix or does not get written, so each such behaviour is either
specified or removed. The developer chose on 2026-10-04 which ones to keep
and specify; this change writes them down.

With one exception it does not change what the software does: every rule
below describes today's code, except SU-4. The developer decided on
2026-10-04 that the tool prints the address of its page when it starts and no
longer opens the browser itself.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-1: the source text is in the language of the terms. MC-18 added: terms file and source text are UTF-8, a byte order mark is accepted. MC-19 added: card writing may look a term up on the web; no links or citations on a card. MC-20 added: a run goes on when the page is closed, and the page shows the current or last run until the tool restarts. MC-10: "starting" before the first term. MC-17: "being cancelled" until the run stops. Field tables: language of the English → Russian explanation, length of the Russian → Chinese explanation, underscores in the exercise. | written |
| [context-finding.md](../../specs/context-finding.md) | CF-1: a passage is one line. CF-4: "close together" is at most five other words between the first and the last word of the term. CF-5: no passage twice. CF-9: the language comes from the language pair (links to MC-1). | written |
| [export.md](../../specs/export.md) | EX-10 added: how clicking, Shift-clicking and id ranges select. EX-3: the size of the list is shown. EX-4: a run finishing while another language pair is shown. EX-5, EX-7: the export file names, and the name in the result. | written |
| [setup.md](../../specs/setup.md) | new: data folder (SU-1), card store (SU-2), API key (SU-3), starting (SU-4: the address is printed, no browser is opened) | written |

`setup.md` and EX-5 name files (`data`, `internal.db`, `.env`,
`cards_ru.tsv`, `cards_cn.tsv`). These are names the user has to know to use
the tool, not names of the code's own files, so Principle I's "no
implementation detail" is read as not covering them.

## Left out on purpose

Found in the same comparison and not specified here, by the developer's
choice: which files of the data folder the pickers list; that Chinese has no
dictionary-form search; quoting of fields in the export file; what switching
the language pair does to the selection and the export message; which address
the tool serves on; the model used for card writing. The acceptance criteria TE-1 to TE-4 that `tests/test_tech.py` and
changes 001 and 003 cite are no longer in `tech.md`; that is also not
settled here.

## Open point

CF-9 requires context finding to work on Chinese source text, and MC-1 now
says that no language pair has one. The requirement is kept as it was; whether
it should stay is not decided in this change.

## Where the specs differ from today's code

Except for SU-4 the behaviour is already there. What is missing is the tests
Principle III asks for.

| Spec | Rule | Today's code |
|---|---|---|
| making-cards MC-1 | The source text is in the language of the terms. | Already so. No test names it. |
| making-cards MC-18 | UTF-8 input, byte order mark accepted. | Already so. No test. |
| making-cards MC-19 | Card writing may use the web; no links or citations. | Already so, by what card writing is asked for. No test. |
| making-cards MC-20 | A run survives closing or reloading the page; the page shows the last run. | Already so. No test. |
| making-cards MC-10 | "Starting" before the first term. | Already so. No test. |
| making-cards MC-17 | "Being cancelled" until the run stops. | Already so; an end-to-end test checks it. |
| making-cards, field tables | Explanation language and length; underscores in the exercise. | Already so, by what card writing is asked for; not checked on the card that comes back. No test. |
| context-finding CF-1 | A passage is one line. | Already so. No test. |
| context-finding CF-4 | At most five other words in between. | Already so. The test covers "close together", not the number. |
| context-finding CF-5 | No passage twice. | Already so. No test. |
| export EX-10 | Click, Shift-click, open-ended id range, replacing the selection. | Already so. Shift-click is tested; the rest is not. |
| export EX-4 | Another language pair shown when the run finishes. | Already so. No test. |
| export EX-5, EX-7 | File names; the name in the result. | Already so, and tested. |
| setup SU-1, SU-2, SU-3 | Data folder, card store, API key. | Already so. No test; the tests replace all three on purpose. |
| setup SU-4 | The address is printed; no browser is opened. | The address is printed and the browser is opened. `README.md` and `AGENTS.md` say the tool opens in the browser. No test. |

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps, tests first.
