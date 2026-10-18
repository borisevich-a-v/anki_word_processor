# 019 Newest card first

## Why

The list showed the oldest card first, so the cards of the last run, the ones
the user has just made and wants to look through, were at the bottom. Owner
request: show the newest first.

## Specs

| Spec | Change | Status |
|---|---|---|
| [card-library.md](../../specs/card-library.md) | CL-1: the list is newest first instead of oldest first. | written |
| [export.md](../../specs/export.md) | None. The exported file stays in id order (EX-6), and a range of ids (EX-4) is about ids, not about the order of the list. | n/a |

## Decisions taken without asking (low risk)

- Only the order of the list changes; ids, selection, editing and export are
  as before.

## Open

None.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| CL-1 | Built in this change. |

No new technology.
