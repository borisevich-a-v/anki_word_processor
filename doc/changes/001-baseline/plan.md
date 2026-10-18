# 001 Baseline: plan

## Approach

The core is rebuilt around three typed entry points, one per spec. The web UI
calls only these and renders what they return. Nothing in the core prints.

| Spec | Module | API |
|---|---|---|
| context-finding | `search.py` | `SourceText(language, text).find(term) -> list[str]` |
| making-cards | `process_words.py` | `make_cards(plugin, llm, terms_file, source_file=None, *, on_report, on_progress, should_cancel) -> RunResult`; `read_terms(file) -> list[str]` |
| export | `export_cards.py` | `list_cards(plugin) -> list[tuple]`; `export_cards(plugin, ids) -> ExportResult` |

`RunResult` holds the ids of the cards made and the terms not processed
(`failed` with reason, `limit_reached`, `cancelled`). `on_report` and
`should_cancel` belong to 002 and are built together with this change, because
both changes rewrite the same function.

## How each difference is closed

| Rule | How |
|---|---|
| EX-6 UTF-8, Anki marker | The file is opened as UTF-8 and starts with the line `#separator:tab`. |
| export: no filter | The filter box is removed from the page. |
| EX-1 headings | Each language pair names its fields; the page builds the table head from them and shows every field. |
| CF-1 fifty words | A passage is the ten-word stretch with 20 words before and 20 after, cut from the original text; at the edges, the first or last fifty words. Cached texts get a new cache key, so old long passages are never read. |
| CF-8, MC-3 punctuation | No term is rejected. A term is reduced to its letters-and-digits words before it is searched, so no punctuation reaches the full-text query. |
| CF-9 language of the source | Each language pair names the language of its source text (English for English → Russian, Russian for Russian → Chinese); dictionary forms use that model. |
| CF-9 Chinese | Words of a Chinese text are the tokens of the Chinese model; passages are cut by word positions in the original text, so no spaces are added. Chinese has no dictionary forms, so only the exact search applies. |
| CF-7 one source per run | Every run builds its own `SourceText` with its own in-memory index; there is no shared index to clear. |
| CF-5 | Results are ordered by position in the text and cut to five; identical passages (neighbouring stretches at the edges of the text) are returned once. |
| MC-2 empty lines, repeats | `read_terms` drops lines that are empty or only spaces and keeps the first of identical lines. Lines are compared as written, with nothing trimmed. |
| MC-16 term on the card | After card writing the term field is replaced by the term from the file and the card is validated again. |
| MC-1, MC-14 optional source | `source_file` may be `None`. With no contexts, the request to card writing says to make the example up. |
| MC-13 | Both files are read before the report is made, so an unreadable file is an error and nothing else. Files are read as UTF-8 on both platforms. |
| EX-4 | `RunResult.made` carries the ids of the new cards; the page selects exactly those instead of comparing card lists. |
| EX-8 | `export_cards` writes nothing when no card is selected and returns a count of 0. |

## Checks that were already red

`tests/test_search.py` imported a function that no longer existed; `ruff`
reported an unused import; `ty` reported errors in `ui.py`. All three are fixed
here: the search tests are rewritten against CF-1 to CF-9, and the job state in
`ui.py` becomes a typed class.

## Tests

Core tests, one or more per criterion, id in the docstring:
`tests/test_search.py` (CF), `tests/test_making_cards_core.py` (MC),
`tests/test_export_core.py` (EX), `tests/test_tech.py` (TE-1, TE-2). The
end-to-end tests of 003 are updated for the new page and gain the criteria 003
left to this change. The stand-in for card writing moves to
`tests/fake_llm.py`, shared by both kinds of test; it returns the term in upper
case, so every run checks MC-16.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. No spec is edited; the code is brought to the specs. |
| II. Core and frontend | Served. All printing is removed from the core; progress, report and outcome go through callbacks and return values. The page only renders. |
| III. Tested offline | Served. The test session refuses connections that leave the machine and removes the API key. |
| IV. No new technology | Nothing added. |

## Risks

- **Existing cards.** Cards made before MC-16 may carry the term in the form
  card writing returned. Such a term is not recognised as done and is made
  once more.
- **Chinese word boundaries** come from the model and depend on the
  surrounding text; a term is found only where the model cuts the text the
  same way.
