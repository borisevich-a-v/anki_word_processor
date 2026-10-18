import shutil
import sqlite3
import threading
from pathlib import Path

from core import config


class Database:
    def __init__(self, path: Path = config.DB_PATH):
        self.path = path
        self._lock = threading.RLock()
        self._con = sqlite3.connect(path, autocommit=True, check_same_thread=False)

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Returns the rowid of the inserted row, if the statement inserted one."""
        with self._lock:
            return self._con.execute(sql, params).lastrowid or 0

    def script(self, sql: str) -> None:
        """Runs several statements; with BEGIN ... COMMIT in it they succeed or fail together."""
        with self._lock:
            self._con.executescript(sql)

    def fetchone(self, sql: str, params: tuple = ()) -> tuple | None:
        with self._lock:
            return self._con.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list[tuple]:
        with self._lock:
            return self._con.execute(sql, params).fetchall()

    def ensure_cards_table(self, name: str, columns: list[str]) -> None:
        """A card table: an `id` that is never reused or renumbered, then the card's columns.

        A table made before ids were explicit used the row number as id; it is
        rebuilt with those same numbers as ids, after a copy of the database file.
        """
        cols = ", ".join(columns)
        table = f"id INTEGER PRIMARY KEY AUTOINCREMENT, {cols}"
        if not self.fetchone(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ):
            self.execute(f"CREATE TABLE {name} ({table})")
        elif "id" not in [c[1] for c in self.fetchall(f"PRAGMA table_info({name})")]:
            if self.fetchone(f"SELECT 1 FROM {name}"):
                shutil.copy(self.path, self.path.with_name(self.path.name + ".bak"))
            self.script(
                f"""BEGIN;
                DROP TABLE IF EXISTS {name}_new;
                CREATE TABLE {name}_new ({table});
                INSERT INTO {name}_new (id, {cols}) SELECT rowid, {cols} FROM {name};
                DROP TABLE {name};
                ALTER TABLE {name}_new RENAME TO {name};
                COMMIT;"""
            )


db = Database()
