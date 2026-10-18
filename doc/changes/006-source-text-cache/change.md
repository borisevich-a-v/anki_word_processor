# 006 Source text cache

## Why

A prepared source text has been kept between runs since before the specs
existed, and no spec said so (see "Extra" in `SPEC_ALIGNMENT_REPORT.md`).
Nothing was ever removed: every edit of a source text and every change of
what is kept left the old data behind for good. On 2026-10-04 the kept data
was 12 files, 32 MB, none of which could be read again.

The developer decided on 2026-10-04 to keep the cache and to have the tool
remove what it no longer needs.

## Specs

| Spec | Change | Status |
|---|---|---|
| [context-finding.md](../../specs/context-finding.md) | CF-10 added: a prepared text is kept for later runs; what belongs to no text now in the data folder is removed. | written |

## Where the specs differ from today's code

| Spec | Rule | Today's code |
|---|---|---|
| context-finding CF-10 | An unchanged text is not prepared again. | Already so. No test. |
| context-finding CF-10 | What was kept for a changed or removed text, or by an earlier version, is removed when a text is prepared. | Never removed. |

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps.
