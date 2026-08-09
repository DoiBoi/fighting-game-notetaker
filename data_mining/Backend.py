import sqlite3
from dataclasses import dataclass
from functools import reduce

BACKEND = "../data/data.db"

@dataclass
class Column:
    name: str
    type: str

class Backend:
    def __init__(self, name: str) -> None:
        self.name = name
        self.conn = sqlite3.connect(BACKEND)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode = WAL;")  # Fast concurrent reads/writes
        self.cursor.execute("PRAGMA synchronous = NORMAL;")  # Balances safety and speed
        self.conn.commit()

    def closeConnection(self) -> None:
        self.conn.close()

    def initTable(self, ddl: list[Column]) -> None:
        self.columns = [item.name for item in ddl]
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name} (
                {reduce(lambda acc, curr: acc + f"{curr.name} {curr.type}\n",ddl, "")}
            ) WITHOUT ROWID
            """
        )
        self.conn.commit()

    def pushData(self, payload: dict) -> None:
        self.cursor.executemany(f"""
            INSERT OR REPLACE INTO {self.name} ({reduce(lambda acc, curr: acc + f"{curr}, ",self.columns, "")})
            VALUES ({reduce(lambda acc, curr: acc + f":{curr}, ", payload.keys(), "")});
        """, payload)
        self.conn.commit()

    def fetchData(self) -> list[dict]:
        self.cursor.execute(f"SELECT * FROM {self.name}")
        return self.cursor.fetchall()
