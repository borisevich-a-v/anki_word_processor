# 012 UX polish: plan

- **Core.** `making_cards`: a failed term's reason goes through the same
  wording as a refused edit (the `_reason` of `card_library` becomes public
  as `describe_error` and is used by both); other errors keep their text.
  `make_cards` refuses the same file as terms and source (MC-22).
- **Web.** `Job` gets a start time; the status shows elapsed and remaining
  time (MC-10). `status.html`: counts, `<details>` for the lists (kept open
  across polls with `hx-preserve`), failed terms with copy and run again,
  Cancel inside the status. `GET /files` re-reads the folder (MC-24).
  Cards shown on opening a page are never checked; only the table fetched
  when a run finishes selects the new ones (EX-4). `edit` accepts an empty
  value.
- **Frontend.** Page scrolls normally; table has a bounded height with a
  sticky header; responsive toolbar. Remembered choices in `localStorage`,
  no preselected terms file, warning for the same file twice. Edit: pencil
  hint, textarea, saves on blur and Tab, Escape abandons, errors stay.
  Delete question is a modal `<dialog>`; Delete is apart from Export; counts
  on both buttons. Toasts for card messages, a result line beside Export.
  Rows focusable with Space, Enter, Delete and arrows. Heading names the pair.
- **Tests.** New tests for each new criterion named in its docstring; the
  existing ones adapted where behaviour changed.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served. |
| II. Core and frontend | Served: wording of reasons and the same-file rule are in the core; the page only shows and asks. |
| III. Tested offline | Served. |
| IV. No new technology | Served: browser built-ins and existing htmx only. |
