# Shortcuts for running the tool and its checks. `make` alone lists them.
# Every target is a plain `uv run ...` command; see README.md and AGENTS.md.

MODEL ?=
HEADED ?=

.DEFAULT_GOAL := help
.PHONY: help install run stage stage-real lint unit e2e check

help:
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

install: ## Install dependencies and Chromium for the end-to-end tests
	uv sync
	uv run playwright install chromium

run: ## Start the tool with real data (port 8765)
	uv run src/run.py

stage: ## Start the stage profile with the fake card writer (port 8766)
	PROCESS_ANKI_PROFILE=stage uv run src/run.py

stage-real: ## Start the stage profile with the real LLM; MODEL=<model> picks it
	PROCESS_ANKI_PROFILE=stage PROCESS_ANKI_REAL_LLM=1 $(if $(MODEL),PROCESS_ANKI_MODEL=$(MODEL)) uv run src/run.py

lint: ## Run the pre-commit checks on all files: ruff fix and format, ty, file hygiene (edits files)
	uv run pre-commit run --all-files

unit: ## Unit tests (everything except the end-to-end tests)
	uv run pytest --ignore=tests/e2e

e2e: ## End-to-end tests in a browser; HEADED=1 shows the browser
	uv run pytest tests/e2e $(if $(HEADED),--headed)

check: lint unit e2e ## lint, then unit and end-to-end tests
