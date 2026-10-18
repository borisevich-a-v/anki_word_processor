# 005 FastAPI and htmx for the web UI

## Why

The web UI is one Python file: a hand-written request handler on the built-in
HTTP server, and a page whose HTML, CSS and JavaScript sit in a string. Every
part of the page is built in the browser from JSON by hand-written JavaScript.
That was enough to start with, and it is the part of the tool that is hardest
to extend. The developer asked on 2026-10-04 for a more capable UI framework
and chose FastAPI with htmx.

This change does not change what the software does. Every acceptance
criterion reads as before, and the end-to-end tests check the same things.

## Specs

| Spec | Change | Status |
|---|---|---|
| [tech.md](../../specs/tech.md) | the web UI row now names FastAPI, uvicorn, Jinja2 and htmx instead of the built-in HTTP server and plain JavaScript | written |

No other spec changes.

## New technology (Principle IV)

| Addition | Why the existing stack is not enough | Agreed |
|---|---|---|
| FastAPI | The built-in HTTP server has no routing, no input validation and no templates; all three were written by hand. | Yes, by the developer on 2026-10-04, chosen over Alpine.js, NiceGUI, Streamlit and React or Vue with Vite. |
| htmx 2.0.11, shipped with the tool as one file | Lets the server-rendered page update in parts without hand-written request code in the browser. | Yes, same decision. |
| uvicorn | FastAPI needs a server to run on. | Follows from FastAPI. |
| Jinja2 | Server-side templates for the pages FastAPI returns. | Follows from FastAPI with htmx. |
| python-multipart | FastAPI needs it to read the forms htmx posts. | Follows from FastAPI with htmx. |

## Where the specs differ from today's code

| Spec | Rule | Today's code |
|---|---|---|
| tech | The web UI runs on FastAPI and htmx. | `src/ui.py` uses the built-in HTTP server and builds the page in the browser from JSON. |

## Files in this change

- `plan.md`: how, with the constitution check.
- `tasks.md`: ordered steps.
