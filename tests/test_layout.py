"""Principle II: the core does not depend on the web frontend."""

import re
from pathlib import Path

CORE = Path(__file__).parents[1] / "src" / "core"
FRONTEND = re.compile(
    r"^\s*(?:from|import)\s+(web|fastapi|uvicorn|jinja2|starlette)\b", re.M
)


def test_the_core_imports_nothing_from_the_frontend():
    """Principle II: nothing under core/ imports the web package or the web libraries."""
    offenders = [p.name for p in CORE.rglob("*.py") if FRONTEND.search(p.read_text())]
    assert offenders == []
