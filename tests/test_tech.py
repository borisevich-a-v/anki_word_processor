"""tech.md: what is required of the tests themselves."""

import os
import socket
from pathlib import Path

import pytest

from core import config

REPO = Path(__file__).parents[1]


def test_tests_are_offline_and_have_no_api_key():
    """TE-1: nothing outside this machine can be reached, and there is no API key to use."""
    assert "OPENAI_API_KEY" not in os.environ
    with socket.socket() as s, pytest.raises(OSError, match="tests are offline"):
        s.connect(("192.0.2.1", 443))


def test_tests_use_their_own_data_folder_and_card_store():
    """TE-2: the data folder and card store of a test run are not the user's."""
    assert REPO not in config.DATA_FOLDER.parents
    assert REPO not in config.DB_PATH.parents
    assert config.DATA_FOLDER != REPO / "data"
