# Working in this repository

A local, single-user tool that prepares Anki cards, on macOS and Windows; not a
service ([ADR-0001](docs/adr/0001-local-single-user-tool.md)). Python 3.13,
managed with `uv`.

# Part 1. The repository

## Where things are

| Path | What |
|---|---|
| `src/` | The code. |
| `tests/` | The tests. |
| `doc/specs/`, `.scratch/` | Specs; see Part 2. |

## Rules

- **Core and frontend stay apart.** The core does all the useful work and
  exposes it through a typed API. It never prints, prompts or reads `stdin`; it
  reports through return values and callbacks. The frontend is a web UI that
  collects input, calls the core and renders the result; it has no business
  logic.

## Commands

See the [Makefile](Makefile); `make` alone lists the targets.

## Profiles: prod, stage, tests

What the profiles do for the user is in [doc/specs/setup.md](doc/specs/setup.md);
the logic is in `src/core/config.py`, driven by environment variables:

| | prod (`make run`) | stage (`make stage`, `make stage-real`) | tests |
|---|---|---|---|
| `PROCESS_ANKI_PROFILE` | unset or `prod` | `stage` | unset |
| Data folder and card store | `data/prod/`, `data/prod/internal.db` | `data/stage/`, `data/stage/internal.db` | a temporary folder, set by `PROCESS_ANKI_DATA` and `PROCESS_ANKI_DB` in `tests/conftest.py` |
| Port | 8765 | 8766 | — |
| Card writer | real LLM, fixed prod model | stand-in, no LLM call; real LLM with `PROCESS_ANKI_REAL_LLM=1`, model from `PROCESS_ANKI_MODEL` | prod settings, but no API key and any non-local connection is refused |
| Page | normal | marked as stage | — |

Tests never touch `data/`.

# Part 2. Spec-driven development (SDD)

This project is developed spec-first. The rules here and the ADRs in
`docs/adr/` override habit and existing code.

## Where things are

| Path | What |
|---|---|
| `.scratch/<aspect>/issues/01-<aspect>.md` | Living spec of one aspect (making cards, card library, context finding, export, help): what it does **now**. |
| `doc/specs/setup.md` | Living spec of setup and profiles. |
| `doc/specs/tech.md` | The main technology in use. The one spec that names tools and libraries |
| `.scratch/<feature>/` | One folder per feature in progress: `spec.md` (why, which specs change, how, with a check against the rules), `issues/NN-name.md` (one ticket per step). Work on an existing aspect goes in that aspect's folder, numbered after `01`. |
| `docs/adr/` | Decisions worth keeping beyond one feature. |

## How a change is made

Any change in behaviour goes through these steps, in order.

1. **Spec.** Edit the affected living specs (the `01-<aspect>.md` tickets,
   `setup.md`, `tech.md`) in place so they describe the new behaviour. Write `.scratch/<feature>/spec.md`: why, which specs changed
   and how, and where the specs now differ from today's code.
2. **Plan.** In the same `spec.md`: how it will be built, with a check
   listing any rule in this file or ADR the plan bends, and why.
3. **Tickets.** `.scratch/<feature>/issues/NN-name.md`: small ordered steps,
   tests first. See [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).
4. **Implement.**

A bug fix (the code does not do what the spec says) needs no feature folder.
Small changes that do not alter what the software does for the user do not
need a spec either. Specs stay short and readable by a human: they describe
the functionality, not every detail.

## Rules that are easy to break

- **Do not guess.** Anything unclear in a spec is marked
  `[NEEDS CLARIFICATION]` and asked, not decided silently.
- **Specs say what, not how.** No file names, functions, libraries or UI
  element names in living specs, except the technology list in `tech.md`.
- **Specs do not cover every corner case.** It is not possible to list them
  all in the specs. Do not read a missing case as "anything goes": follow
  the intent of the spec, and ask if it is unclear.
- **One place per fact.** A spec links to another spec instead of restating
  it.
- **No new technology without agreement** (tool, library, framework, external
  service). Ask the developer first; record the agreement in the feature's `spec.md` and add it
  to `doc/specs/tech.md`.
- **A feature may be specified but not built yet.** Check `.scratch/` for
  open tickets and the "Where the specs differ from today's code" table in
  their `spec.md` before assuming the code matches a spec.

## Agent skills

### Issue tracker

Local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
