# 016 Terms are compared ignoring letter case: plan

- **Core.** One function in `core/terms.py` gives the comparison key of a term:
  its case-folded text (`str.casefold`). The terms file reader keeps the first
  line of each key. `Plugin.is_processed` (one shared implementation in the base
  plugin, replacing the two exact-match SQL ones; SQLite's `lower()` is ASCII only,
  so keys are compared in Python) compares keys and can leave out one card, which
  `edit_card` uses so a card never clashes with itself.
- **Store.** No schema change, no unique index: populated stores may already hold
  case variants.
- **Web / frontend.** No change; they only show what the core reports.
- **Tests.** `tests/test_term_case_core.py`, each test naming its criterion.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: all in the core. |
| III. Tested offline | Served. |
| IV. No new technology | Served: standard library only. |
