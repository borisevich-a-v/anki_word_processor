# 001 Baseline: tasks

1. [x] `tests/test_search.py`: rewrite against CF-1 to CF-9 (English, Russian,
   Chinese).
2. [x] `search.py`: `SourceText`; fifty-word passages; punctuation; language of
   the source; Chinese; versioned cache.
3. [x] Language pairs: field names for the user, language of the source text,
   `save_card` returns the id; no printing.
4. [x] `tests/test_making_cards_core.py`: MC-2 to MC-11, MC-13, MC-14, MC-16
   and the field rules of both pairs.
5. [x] `process_words.py`: `read_terms`, `make_cards`, `RunResult`; UTF-8
   input; no printing.
6. [x] `tests/test_export_core.py`: EX-1, EX-2, EX-5 to EX-9.
7. [x] `export_cards.py`: UTF-8, Anki marker, `ExportResult`, nothing written
   for an empty selection.
8. [x] `ui.py`: typed job state; optional source text; table head from the
   language pair; filter box removed; selection from the ids of the run.
9. [x] `tests/e2e`: update for the new page; add MC-1 and MC-14 without a
   source text, MC-2, MC-3, MC-16, EX-1 for Russian → Chinese, EX-6 marker,
   EX-9.
10. [x] `tests/conftest.py`, `tests/test_tech.py`: offline guard, no API key
    (TE-1, TE-2).
11. [x] `ruff`, `ty`, `pytest` green.
