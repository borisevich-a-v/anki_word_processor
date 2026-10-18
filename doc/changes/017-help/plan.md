# 017 Tips move into a help: plan

- **Web / frontend only.** The tips list leaves the page template and goes into a
  `<dialog>` (native, as the delete question already is). A button in the page
  header opens it. A key handler on the document opens/closes it on F1 and
  prevents the browser default. Escape closing comes with `<dialog>`.
- The handler ignores F1 when a field is being edited or another dialog is open.
- The phone-only folding script line and the `#tips` styles are removed.
- **Core.** No change.
- **Tests.** `tests/e2e/test_help.py` naming HP-1 to HP-7; the 015 phone-folding test is
  replaced by a check that no tips are on the page.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: presentation only. |
| III. Tested offline | Served. |
| IV. No new technology | Served: native `<dialog>`, already in use. |
