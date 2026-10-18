# 009 Save dialog on export

## Why

Export wrote to a fixed file in the data folder, replacing the previous one.
The developer asked on 2026-10-04 that the user is asked where to save the
cards and may choose the name, defaulting to `ankicards_<datetime>`.

## Decisions (developer, 2026-10-04)

- The place is chosen in the browser's own save dialog, not in a text field.
- Default name: `ankicards_YYYYMMDD_HHMMSS.tsv`.
- Whether to replace an existing file is decided in that dialog.

## Specs

| Spec | Change | Status |
|---|---|---|
| [export.md](../../specs/export.md) | EX-5 rewritten (place and name chosen by the user, default name). EX-11 added (dialog left without saving). EX-7, EX-8 adjusted. | written |
| [setup.md](../../specs/setup.md) | SU-1: export files no longer go to the data folder. | written |

## Decision on the fallback

Browsers without the save-file API (Firefox, Safari) cannot show a place
dialog to a web page. The developer accepted on 2026-10-04 that they download
the file under the suggested name instead; EX-5 says so.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| EX-5, EX-7, EX-11, SU-1 | The core writes `cards_ru.tsv` / `cards_cn.tsv` into the data folder. Built in this change. |

No new technology: the save dialog is a standard browser API used from the
existing script.
