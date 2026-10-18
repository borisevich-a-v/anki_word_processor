# 002 Pre-run report

## Why

Two things, both about knowing what a run will do with the terms file.

**Report before processing.** Terms that already have a card were skipped
silently, and terms beyond the limit were only named in the summary after the
run, which can be many minutes later. The user could not tell up front whether
a file was mostly done, or how much of it this run would cover. The run now
opens with a report that lists both groups. Processing starts on its own after
the report; because the user may then see that the run is not what they
wanted, a run can now be cancelled at any point, keeping the cards already
made.

**"Word" was ambiguous.** The specs said "word" both for the thing a card
teaches, which can be a phrase, and for a single word of text ("fifty words",
"whole words"). The thing a card teaches is now called a **term**; "word"
means one single word only. The definition lives in making-cards.md.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-15 and MC-17 added; MC-11 lists cancelled terms; MC-4 no longer says "without being reported"; MC-13 covers the report; word → term throughout, including the "words file" (now "terms file") and the "word" card field (now "term") | written |
| [context-finding.md](../../specs/context-finding.md) | word/phrase → term; no behaviour change | written |

export.md is not affected.

## Where the specs differ from today's code

| Spec | Rule | Today's code |
|---|---|---|
| making-cards MC-15 | A report is shown before the first term is processed. | Nothing is shown until progress starts; existing terms are never shown. |
| making-cards MC-15 | With nothing left to process, the report says so. | The run finishes with "Processed 0". |
| making-cards MC-17 | A run can be cancelled; unprocessed terms are reported as cancelled. | A run cannot be stopped from the UI. |
| naming | The UI says "term" and "terms file". | The UI says "word" and "words file". |

Renaming identifiers in code and the card's stored field is for the plan to
decide; the specs only fix the wording the user sees.

## Depends on

001-baseline: the report is delivered through the typed core API that 001
introduces. This change is planned after 001's plan exists.

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps, tests first.
