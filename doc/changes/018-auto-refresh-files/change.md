# 018 The lists of files follow the folder

## Why

The user had to press a button to see files added to the data folder after the
page was opened. Owner request: re-read the files whenever a drop-down is
clicked, so the button is not needed.

## Specs

| Spec | Change | Status |
|---|---|---|
| [making-cards.md](../../specs/making-cards.md) | MC-24: the lists of files are re-read by themselves, on return to the page and when the user goes to choose a file; choices are kept; a removed chosen file is unchosen. The button is gone. | written |
| [help.md](../../specs/help.md) | None (it says nothing about the button's name); the help text drops the button. | n/a |

## Decisions taken without asking (low risk)

- The "Refresh files" button is removed: with automatic reading it does nothing
  more. Texts that told the user to press it now say the file will show up.
- A web page cannot read a folder, and a drop-down's menu is drawn by the
  browser, so "every click" is done as: when the pointer or keyboard goes into
  either drop-down, and when the browser window is shown again (coming back from
  the file manager). The first click after adding a file may show the old
  list for a moment; the lists are then updated in place, and the next open shows
  the new file. Lists are only touched when the files changed.
- A chosen file that is no longer in the folder leaves the choice empty, like
  a fresh page; it is not kept as a phantom option.

## Open

None.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| MC-24 | Built in this change. |

No new technology.
