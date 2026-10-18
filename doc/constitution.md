# process_anki Constitution

Rules that every spec, plan and change in this project must satisfy. Specs say
*what* and *why*; plans say *how*; this file says what is never up for
negotiation in either.

## Product scope

A local, single-user tool that helps prepare Anki cards.
Runs on macOS and Windows. Not a service, not multi-user, no accounts, no deployment.

## Core principles

### I. Spec before code

Behaviour is described in living specs, one file per aspect of the software:
`doc/specs/<aspect>.md` (for example `context-finding.md`). A spec states what
the software does now: user scenarios and acceptance criteria, no implementation
detail. Each aspect is described in exactly one spec; other specs link to it
instead of restating it.

Behaviour changes through change records: `doc/changes/NNN-name/change.md` says
why, and which specs change and how; `plan.md` and `tasks.md` sit next to it. The
change edits the affected specs in place, and each spec ends with a History list
of the changes that touched it. Change records are never edited after they are
implemented; a correction is a new change.

Code that has no spec behind it is a bug fix or it does not get written.
Anything unclear is marked `[NEEDS CLARIFICATION]`, never guessed.

### II. Core and frontend

The software has two parts. The core does all the useful work and exposes it
through a typed API. The frontend is a web UI that only collects input, calls
the core and renders the result; it contains no business logic. The core knows
nothing about the frontend: it never prints, prompts or reads from `stdin`, and
it reports progress and outcomes through return values and callbacks.

### III. Tested offline

Every acceptance criterion in a spec maps to at least one test. Tests run
without network or LLM calls. `ruff`, `ty` and `pytest` pass before every
commit.

### IV. No new technology without agreement

Adding a tool, library, framework, external service or any other technology
the project does not already use must be agreed with the developer before it
appears in a plan or in code. The plan names what it wants to add and why the
existing stack is not enough; work on that part waits for the answer.

## Workflow

1. Change the spec: edit the affected `doc/specs/<aspect>.md` files in place,
   with open questions resolved. As part of the same step, `change.md` records
   why and which specs changed, and each edited spec gets a History entry.
2. `plan.md`: how, including a constitution check that lists any principle the
   plan bends and why.
3. `tasks.md`: small ordered steps, tests first.
4. Implement; each task leaves the checks green.

## Governance

This document overrides habit and existing code. Existing code that violates it
is debt to be removed by a spec, not a precedent. Amendments are made by editing
this file with a version bump and a one-line reason in the commit message.

**Version**: 0.1.0 | **Ratified**: 2026-10-03 | **Last amended**: 2026-10-03
