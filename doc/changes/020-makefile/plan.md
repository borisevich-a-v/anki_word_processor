# 020 Makefile: plan

- `Makefile` at the repository root. Each target runs commands already
  documented in `README.md` and `AGENTS.md`: `install` (dependencies and the
  Playwright browser), `run` (prod), `stage` (fake writer), `stage-real`
  (real LLM, `MODEL=` optional), `lint` (the pre-commit checks on all
  files; edits files), `unit` (all tests but e2e), `e2e` (`HEADED=1` shows the browser), and `check` (`lint`, `unit`,
  `e2e` in that order). `make` alone lists the
  targets.
- `.pre-commit-config.yaml`: ruff and ruff format become local `uv run`
  hooks (ruff with `--fix`), so they use the project's ruff version; the
  hook is installed with `uv run pre-commit install`.
- No code or tests change; the commands it wraps are already covered.

## Constitution check

| Principle | Status |
|---|---|
| I. Spec before code | Served: `tech.md` updated first. |
| II. Core and frontend | Not affected. |
| III. Tested offline | Not affected; the test targets run the offline suite. |
| IV. No new technology | Bent with agreement: make, requested by the developer. Optional, so the uv commands keep working without it (Windows). |
