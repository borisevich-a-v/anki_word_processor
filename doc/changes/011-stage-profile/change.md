# 011 Stage profile

## Why

The tool is buggy and the developer wants a copy to try things in and to
reproduce bugs, without risking the real cards and without paying for LLM
calls. Asked on 2026-10-04.

## Decisions (developer, 2026-10-04)

- The profile is chosen with an environment variable, not a command-line flag.
- Data and card store are organised per profile: `data/prod/` and
  `data/stage/`, each with its own `internal.db`. The existing real files
  move to `data/prod/` once, by hand; the tool does not migrate them.
- The stage profile writes cards with a fake writer by default. The real LLM
  is opt-in with `PROCESS_ANKI_REAL_LLM=1`, and `PROCESS_ANKI_MODEL` may name
  the model; unset, `gpt-5-nano` (decided 2026-10-04).
- The stage profile runs on another port and shows a TEST/STAGE marker.

## Specs

| Spec | Change | Status |
|---|---|---|
| [setup.md](../../specs/setup.md) | SU-1 and SU-2 rewritten (folder per profile). SU-3 adds that stage needs no key. SU-5 (profiles), SU-6 (stage card writer), SU-7 (marker, separate address) added. | written |

## Open

- The profile is called `stage` (as the folder); the developer first said
  "test". Say if another name is wanted.
- Not covered: the stage address is fixed (SU-7 says only "another"). Say if
  it should be configurable.

## Where the specs differ from today's code

| Spec | Today's code |
|---|---|
| SU-1, SU-2 | Data is in `data/`, the store is `internal.db` in the tool's folder. Built in this change. |
| SU-5, SU-6, SU-7 | No profiles; the fake writer exists only in `tests/`; one fixed port. Built in this change. |

No new technology.
