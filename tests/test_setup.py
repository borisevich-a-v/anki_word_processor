"""setup.md."""

import os
import subprocess
import sys
import webbrowser
from pathlib import Path

from core import config
from core.fake_llm import FakeLLM
from core.writer import make_writer
from web import app as ui
from core.languages import En2RuPlugin

REPO = Path(__file__).parents[1]


def _config_in_a_fresh_process(**env_vars: str) -> subprocess.CompletedProcess:
    """Loads core.config without the tests' overrides, as the tool starts."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("PROCESS_ANKI_")}
    env["PROCESS_ANKI_DATA"] = ""  # empty counts as not set
    env |= env_vars
    code = (
        "from core import config; "
        "print(config.PROFILE, config.DATA_FOLDER, config.DB_PATH, config.ENV_FILE, "
        "config.FAKE_LLM, config.MODEL, config.PORTS[config.PROFILE], sep='\\n')"
    )
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO / "src",
        env=env,
        capture_output=True,
        text=True,
    )


def test_locations_are_in_the_tools_own_folder():
    """SU-1, SU-2, SU-3, SU-5: unset, the profile is prod; its data folder and card
    store are in data/prod, the key file is .env in the tool's own folder."""
    out = _config_in_a_fresh_process().stdout.splitlines()
    assert out[0] == "prod"
    assert [Path(line) for line in out[1:4]] == [
        REPO / "data" / "prod",
        REPO / "data" / "prod" / "internal.db",
        REPO / ".env",
    ]
    assert out[4:] == ["False", "gpt-6-terra", "8765"]


def test_stage_has_its_own_folder_store_and_port():
    """SU-1, SU-2, SU-5, SU-6, SU-7: stage keeps nothing of prod, writes with the
    stand-in, and listens on another port."""
    out = _config_in_a_fresh_process(PROCESS_ANKI_PROFILE="stage").stdout.splitlines()
    assert out[0] == "stage"
    assert [Path(line) for line in out[1:3]] == [
        REPO / "data" / "stage",
        REPO / "data" / "stage" / "internal.db",
    ]
    assert out[4:] == ["True", "gpt-5-nano", "8766"]


def test_stage_with_the_real_llm_uses_the_named_model_or_the_cheap_one():
    """SU-6: PROCESS_ANKI_REAL_LLM=1 turns the stand-in off; PROCESS_ANKI_MODEL names the model."""
    real = {"PROCESS_ANKI_PROFILE": "stage", "PROCESS_ANKI_REAL_LLM": "1"}
    assert _config_in_a_fresh_process(**real).stdout.splitlines()[4:6] == [
        "False",
        "gpt-5-nano",
    ]
    named = _config_in_a_fresh_process(**real, PROCESS_ANKI_MODEL="gpt-x")
    assert named.stdout.splitlines()[4:6] == ["False", "gpt-x"]


def test_prod_ignores_the_stage_variables():
    """SU-6: prod always uses the real LLM and its own model."""
    out = _config_in_a_fresh_process(
        PROCESS_ANKI_REAL_LLM="1", PROCESS_ANKI_MODEL="gpt-x"
    ).stdout.splitlines()
    assert out[4:6] == ["False", "gpt-6-terra"]


def test_another_profile_name_does_not_start():
    """SU-5: any value other than prod and stage is an error."""
    result = _config_in_a_fresh_process(PROCESS_ANKI_PROFILE="test")
    assert result.returncode != 0
    assert "PROCESS_ANKI_PROFILE" in result.stderr


def test_card_store_is_not_offered_as_a_file(data):
    """SU-1: the card store lies in the data folder but is not a terms file or source text."""
    data("terms.txt", "one\n")
    config.DB_PATH.touch()
    (config.DATA_FOLDER / "internal.db-journal").touch()

    assert ui.data_files() == ["terms.txt"]


def test_stage_writes_cards_without_a_key_and_prod_needs_one(monkeypatch):
    """SU-3, SU-6: the stand-in needs no key; the real writer is built from OPENAI_API_KEY."""
    monkeypatch.setattr(config, "FAKE_LLM", True)
    assert isinstance(make_writer(), FakeLLM)
    monkeypatch.setattr(config, "FAKE_LLM", False)
    monkeypatch.setenv("OPENAI_API_KEY", "a-key")
    assert not isinstance(make_writer(), FakeLLM)


def test_key_from_the_environment_reaches_card_writing(data, monkeypatch):
    """SU-3: card writing uses the key in OPENAI_API_KEY."""
    monkeypatch.setenv("OPENAI_API_KEY", "key-from-the-environment")
    keys = []
    monkeypatch.setattr(
        ui, "make_cards", lambda plugin, llm, *a, **kw: keys.append(llm.api_key)
    )
    data("terms.txt", "astray\n")

    ui.run_job(ui.Job(state="running"), "terms.txt", None)

    assert keys == ["key-from-the-environment"]


def test_no_key_is_a_run_error(data):
    """SU-3, MC-13: without a key the run cannot proceed and the user gets the error."""
    data("terms.txt", "astray\n")
    job = ui.Job(state="running")

    ui.run_job(job, "terms.txt", None)

    assert job.state == "error"
    assert job.error and "OPENAI_API_KEY" in job.error
    assert job.report is None and job.result is None
    assert not En2RuPlugin().is_processed("astray")


def test_starting_prints_the_address_and_opens_no_browser(monkeypatch, capsys):
    """SU-4: the address of the page is printed; no browser is opened."""
    opened, served = [], []

    class Server:
        def run(self, sockets):
            served.append(sockets)

    for name in ("open", "open_new", "open_new_tab"):
        monkeypatch.setattr(webbrowser, name, lambda *a, **kw: opened.append(a))
    monkeypatch.setattr(ui, "make_server", lambda: (Server(), "socket"))

    ui.main()

    out = capsys.readouterr().out
    assert f"http://127.0.0.1:{ui.PORT}" in out
    assert f"{config.PROFILE} profile" in out
    assert served == [["socket"]]
    assert opened == []
