import os
from pathlib import Path

_ROOT = Path(__file__).parents[2]

MAX_CARDS_TO_PROCESS = 100
# terms files and source texts; a byte order mark at the start is accepted
TEXT_ENCODING = "utf-8-sig"

PROFILES = ("prod", "stage")
PROFILE = os.environ.get("PROCESS_ANKI_PROFILE") or "prod"
if PROFILE not in PROFILES:
    raise SystemExit(
        f"PROCESS_ANKI_PROFILE must be one of {', '.join(PROFILES)}, not {PROFILE!r}"
    )

# The environment overrides exist for the tests, which must not touch real data.
DATA_FOLDER = Path(os.environ.get("PROCESS_ANKI_DATA") or _ROOT / "data" / PROFILE)
DB_NAME = "internal.db"
DB_PATH = Path(os.environ.get("PROCESS_ANKI_DB") or DATA_FOLDER / DB_NAME)
ENV_FILE = _ROOT / ".env"  # the API key, when it is not in the environment

# The stage profile writes cards with a stand-in unless told to use the real LLM.
FAKE_LLM = PROFILE == "stage" and os.environ.get("PROCESS_ANKI_REAL_LLM") != "1"
STAGE_MODEL = "gpt-5-nano"
PROD_MODEL = "gpt-6-terra"
MODEL = (
    PROD_MODEL
    if PROFILE == "prod"
    else os.environ.get("PROCESS_ANKI_MODEL") or STAGE_MODEL
)
PORTS = {"prod": 8765, "stage": 8766}

DATA_FOLDER.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def user_files() -> list[Path]:
    """The terms files and source texts in the data folder: not hidden, not the card store."""
    return sorted(
        f
        for f in DATA_FOLDER.iterdir()
        if f.is_file() and not f.name.startswith(".") and not f.name.startswith(DB_NAME)
    )
