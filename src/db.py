import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).parents[1] / "internal.db"


class Database:
    def __init__(self, path: Path = _DB_PATH):
        self._con = sqlite3.connect(path, autocommit=True)

    def execute(self, sql: str, params: tuple = ()) -> None:
        self._con.execute(sql, params)

    def fetchone(self, sql: str, params: tuple = ()) -> tuple | None:
        return self._con.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list[tuple]:
        return self._con.execute(sql, params).fetchall()


db = Database()
