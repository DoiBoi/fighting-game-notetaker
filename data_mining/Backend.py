from pathlib import Path
import sqlite3
from dataclasses import dataclass
from functools import reduce

BACKEND = Path("../data/data.db").resolve()

@dataclass
class Column:
    name: str
    type: str


class Backend:

    def dict_factory(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    def __init__(self, name: str) -> None:
        self.name = name
        self.conn = sqlite3.connect(BACKEND)
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "PRAGMA journal_mode = WAL;"
        )  # Fast concurrent reads/writes
        self.cursor.execute("PRAGMA synchronous = NORMAL;")  # Balances safety and speed
        self.conn.commit()
        self.columns = {}


    def closeConnection(self) -> None:
        self.conn.close()

    def initTable(self, ddl: list[Column], compKey="") -> None:
        self.columns = [item.name for item in ddl]
        print(ddl)
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.name} (
                {reduce(lambda acc, curr: acc + f"{curr.name} {curr.type},\n", ddl, "")}
                {compKey}
            ) WITHOUT ROWID
            """)
        self.conn.commit()

    def getDBColumn(self) -> None:
        self.cursor.execute("SELECT name FROM pragma_table_info(?)", (self.name,))

        self.columns = [row["name"] for row in self.cursor.fetchall()]

    def pushData(self, payload: list[dict]) -> None:
        if not self.columns:
            self.getDBColumn()
        self.cursor.executemany(
            f"""
            INSERT OR REPLACE INTO {self.name} ({", ".join(self.columns)})
            VALUES ({", ".join(f":{c}" for c in self.columns)});
        """,
            payload,
        )
        self.conn.commit()

    def fetchData(self, columns="*", where = "true") -> list[dict]:
        self.cursor.execute(f"SELECT {columns} FROM {self.name} WHERE {where}")
        return self.cursor.fetchall()

    def removeTable(self) -> None:
        self.cursor.execute(f"DROP TABLE {self.name}")
