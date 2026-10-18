# 010 Card library: plan

- **Ids (CL-2).** Each card table gets an explicit `id INTEGER PRIMARY KEY
  AUTOINCREMENT` column. `core/store.py` gets `ensure_table`, used by both
  language modules: it creates the table, or migrates an old one (no `id`
  column) in one transaction, keeping every card's current row number as its
  id so nothing the user sees changes. Before migrating a table that has cards
  the database file is copied next to itself (`internal.db.bak`). Inserts name
  their columns, since the table now has one more.
- **Core.** New `core/card_library.py`: `list_cards` (moved from
  `export.py`), `edit_card(plugin, id, field, value)` returning ok or the
  reason, `delete_cards(plugin, ids)` returning how many went. An edit builds
  the card with the plugin's model (field rules, MC-7), and checks the term
  against the other cards (`is_processed`) when it changed. Reasons name the
  field as the user knows it (`Plugin.FIELDS`).
- **Web.** `POST /cards/edit` and `POST /cards/delete`, both answering JSON
  for the script; no logic beyond calling the core.
- **Frontend.** Double-click a field cell to edit it in place: Enter saves,
  Escape or leaving the cell abandons (CL-5), a refused edit keeps the editor
  open with the reason. (Double-click leaves the selection as it was, since
  its two clicks toggle a card twice.) A "Delete selected" button shows an
  in-page question with the count (the viewer's `confirm()` is not used) and
  a Delete and a Keep choice; any change of selection withdraws the question.
- **Tests.** `tests/test_card_library_core.py` (new; EX-1/EX-2 tests move
  here as CL-1/CL-2, migration test), `tests/e2e/test_card_library.py` (new;
  the list tests stay in `test_export.py` and cite CL-1/CL-2). Tests that insert into card tables
  name columns.
- `README.md`: one sentence.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: rules and storage in the core, the page only edits and asks. |
| III. Tested offline | Served. |
| IV. No new technology | Served: SQLite features already used. |
