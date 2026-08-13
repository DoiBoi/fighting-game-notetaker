from pathlib import Path
import time
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
        value = re.sub(r"<[^>]*>", "", value)
        value = re.sub(r"'''?", "", value)
        value = value.replace("&nbsp;", " ")
        return value.strip()

    def textOrNull(self, raw) -> str | None:
        text = self.stripMarkup(str(raw) if raw is not None else "")
        if not text or text == "-" or "{{{" in text:
            return None
        return text

    def fetchImageURLs(self, titles: list[dict]) -> dict:
        lookup = {}
        results = {}
        for image in titles:
            for chara, filename in image.items():
                key = f"{chara}/{filename}"
                results[key] = None
                wiki_title = f"File:{filename.replace('_', ' ')}"
                lookup[wiki_title] = key

        data = self.sendRequest({
            "action": "query",
            "titles": "|".join(lookup.keys()),
            "prop": "imageinfo",
            "iiprop": "url",
            "formatversion": "2",
        })

        for page in data.get("query", {}).get("pages", []):
            title = page.get("title")
            if not title or "missing" in page or not page.get("imageinfo"):
                continue
            orig_key = lookup.get(title)
            if orig_key:
                results[orig_key] = page["imageinfo"][0].get("url")

        return results

    def downloadImages(self, images: dict[str, str], outDir: Path) -> None:
        outDir.mkdir(parents=True, exist_ok=True)

        downloaded, skipped, failed = 0, 0, 0
        for filename, url in images.items():
            dest = (outDir / filename).resolve()

            if outDir.resolve() not in dest.parents:
                print(f"Skipping unsafe path: {filename}")
                failed += 1
                continue

            if dest.exists():
                skipped += 1
                continue

            if not url:
                skipped += 1
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                req = Request(url, headers={"User-Agent": USER_AGENT})
                with urlopen(req, timeout=60) as resp:
                    dest.write_bytes(resp.read())
                downloaded += 1
            except (HTTPError, URLError) as e:
                print(f"Failed to download {filename}: {e}")
                failed += 1

            time.sleep(0.2)

        print(f"Downloaded {downloaded}, skipped {skipped} (already existed), failed {failed}")
