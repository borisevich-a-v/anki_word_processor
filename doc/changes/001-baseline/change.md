# 001 Baseline

## Why

The code was written before the constitution. Nothing in it has a spec behind
it, so no later change has anything to edit. This change writes down what the
software does today and brings the code up to the constitution (typed core
API, no printing in the core, a test per acceptance criterion).

It does not add features. Where current behaviour looks wrong, the spec records
it as an open question; the answer is decided there before the plan is written.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | new | written |
| [context-finding.md](../../specs/context-finding.md) | new | written |
| [export.md](../../specs/export.md) | new | written |

The web UI and card storage have no spec of their own: the UI is described by
the scenarios of these three, and storage only matters through them.

## Where the specs differ from today's code

Decided while writing the specs. The plan must cover each one.

| Spec | Rule | Today's code |
|---|---|---|
| export EX-6 | The export file is UTF-8. | Written in the system default encoding, which on Windows is not UTF-8. |
| export EX-6 | The file tells Anki it is tab-separated. | No such marker. |
| export | No filtering of the card list. | The UI has a filter box. |
| export EX-1 | The card list shows the fields of the chosen language pair. | Always shows the English → Russian column headings. |
| context-finding CF-1 | A context is about fifty words. | About 110 words; cached source texts hold the long passages. |
| context-finding CF-8, making-cards MC-3 | Phrases with commas, semicolons and dashes are processed. | Lines with `,` `;` `\|` or tab are rejected. |
| context-finding CF-9 | Dictionary forms follow the language of the source text. | English → Russian uses the Russian model, Russian → Chinese the Chinese model; the source texts are English and Russian. |
| context-finding CF-9 | Chinese source text is handled word by word. | Text is split on spaces, so Chinese text is not split into words at all. |
| making-cards MC-2 | An empty line is not a term. | An empty line is processed as a term. |
| making-cards MC-2 | A term repeated in the file counts once. | A term that appears twice gets two cards. |
| making-cards MC-16 | The card carries the term exactly as in the terms file. | The term field is whatever card writing returned, so a term returned in another form or case is made again on every run. |
| making-cards MC-1, MC-14 | The source text is optional; without it the example is made up. | A source text is required. |

## Files in this change

- `plan.md`: how, with the constitution check and the core API.
- `tasks.md`: ordered steps, tests first.
