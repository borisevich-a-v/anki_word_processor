# 008 Source layout

## Why

`src/` was a flat pile of modules. The split between the core and the web
frontend (Principle II) was only a sentence in `AGENTS.md`, module names did not
match the specs they implement, and the "plugins" were just the two built-in
language pairs.

## Specs

No spec changes. The specs describe behaviour and name no files, modules or
commands, and no behaviour changes. `tech.md` is not affected: no technology is
added or removed.

## Where the specs differ from today's code

None.

## What changes

| Before | After |
|---|---|
| `src/process_words.py` | `src/core/making_cards.py` |
| `src/search.py` | `src/core/context_finding.py` |
| `src/export_cards.py` | `src/core/export.py` |
| `src/db.py` | `src/core/store.py` |
| `src/config.py` | `src/core/config.py` |
| `src/plugins/` | `src/core/languages/` (`base.py`, `en_ru.py`, `ru_cn.py`) |
| `src/ui.py`, `templates/`, `static/` | `src/web/app.py`, `src/web/templates/`, `src/web/static/` |
| `uv run src/ui.py` | `uv run src/run.py` |

`SpacyPipeline` moves from context finding to `core/languages/base.py`: it is
language-pair vocabulary, and context finding should depend on languages, not
the other way round.

Not done here (a separate change if wanted): moving each language pair's SQL
into the store; an installable `process_anki` package, which needs a build
backend (new technology, needs agreement).

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps.
