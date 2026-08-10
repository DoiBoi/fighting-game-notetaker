import json
import re
import sys
from collections import defaultdict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = f"fighting-game-notetaker/0.0.1 requests/{sys.version}"

class CargoQueryAgent:
    def __init__(self, url: str) -> None:
        self.url = url
        self.tables = defaultdict(list)

    def sendRequest(self, params: dict) -> dict:
        params["format"] = "json"
        params["limit"] = str(params.get("limit", 500))
        params["offset"] = str(params.get("offset", 0))
        url = f"{self.url}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(req) as res:
                body = res.read().decode("utf-8")
        except HTTPError as e:
            raise RuntimeError(f"cargoquery failed: HTTP {e.code}") from e
        except URLError as e:
            raise RuntimeError(f"cargoquery failed: {e.reason}") from e

        data = json.loads(body)
        return data

    def fetchTables(self) -> list | None:
        return self.sendRequest({"action": "cargotables"}).get("cargotables")

    def fetchFields(self, params: dict) -> list | None:
        return self.sendRequest(
            {"action": "cargofields", "table": params.get("table", "")}
        ).get("cargofields")

    def getFields(self, tables: list[str]) -> dict:
        for table in tables:
            self.tables[table].append(self.fetchFields({"table": table}))

        return self.tables

    def fetchData(self, params: dict) -> dict | None:
        params["action"] = "cargoquery"
        return self.sendRequest(params).get("cargoquery", {})

    def stripMarkup(self, value: str) -> str:
        """Strip HTML / wiki markup from the source."""
        value = re.sub(r"<[^>]*>", "", value)
        value = re.sub(r"'''?", "", value)
        value = value.replace("&nbsp;", " ")
        return value.strip()

    def textOrNull(self, raw) -> str | None:
        """Normalize an arbitrary text column to a clean string or None."""
        text = self.stripMarkup(str(raw) if raw is not None else "")
        if not text or text == "-" or "{{{" in text:
            return None
        return text
