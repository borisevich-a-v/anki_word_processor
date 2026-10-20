"""Point the tool at a throwaway data folder and card store, and keep it offline.

This runs before any module from src is imported, which is when the store is
opened and the data folder is fixed.
"""

import os
import shutil
import socket
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

_tmp = Path(tempfile.mkdtemp(prefix="process_anki_tests_"))
(_tmp / "data").mkdir()
os.environ["PROCESS_ANKI_DATA"] = str(_tmp / "data")
os.environ["PROCESS_ANKI_DB"] = str(_tmp / "internal.db")

_LOCAL = ("127.0.0.1", "::1", "localhost")
_connect = socket.socket.connect


def _local_connect(self: socket.socket, address, /):
    if self.family in (socket.AF_INET, socket.AF_INET6) and address[0] not in _LOCAL:
        raise OSError(f"tests are offline, refused to connect to {address}")
    return _connect(self, address)


socket.socket.connect = _local_connect


@pytest.fixture(autouse=True)
def clean_store(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every test starts with an empty data folder, no cards and no API key."""
    from core import config
    from core.store import db
    from core.languages import PLUGINS

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    shutil.rmtree(config.DATA_FOLDER)
    config.DATA_FOLDER.mkdir()
    for plugin in PLUGINS:
        db.execute(f"DELETE FROM {plugin.TABLE_NAME}")
    yield


@pytest.fixture
def data():
    """data("terms.txt", "one\\ntwo\\n") writes a file into the data folder."""
    from core import config

    def write(name: str, content: str | bytes) -> Path:
        path = config.DATA_FOLDER / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    return write
