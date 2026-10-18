# 017 Tips move into a help

## Why

The usage tips sit on the page all the time, taking room above the card list.
Owner request: remove them from the page, add a help button with the F1 hotkey,
and show the tips there.

## Specs

| Spec | Change | Status |
|---|---|---|
| [help.md](../../specs/help.md) | New spec, HP-1 to HP-7: a help button and F1 open a help with a how-to for the whole flow; it replaces the tips on the page. | written |
| [card-library.md](../../specs/card-library.md) | None in behaviour; History line only (the tips left the page). | written |

Tips were never in a spec (015 called it purely visual); now that they are
behind a control with a hotkey, help is an aspect of its own and gets its own spec.

## Decisions taken without asking (low risk)

- The old tips' wording is kept inside a fuller how-to written from the other specs (making cards, export, setup); the how-to adds no new behaviour.
- Help is a modal question-style dialog, like the delete question, so it covers
  the page until closed.
- F1 while a field is being edited or the delete question is open does nothing
  (the page must not be disturbed, as CL-11 and CL-7 require). The button is
  unreachable then anyway, being behind the dialog or leaving the edit by blur.
- The phone rule of 015 (tips folded behind a summary) is gone: there is
  nothing on the page to fold.

## Open

None.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| HP-1 to HP-7 | Built in this change. |

No new technology.
