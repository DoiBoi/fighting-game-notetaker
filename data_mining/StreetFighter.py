from functools import reduce
from pathlib import Path

from Backend import Backend, Column
from CargoQuery import CargoQueryAgent

API = "https://srk.shib.live/api.php"
PERPAGE = 500
IMAGEBATCHSIZE = 50


class StreetFighter6:
    def __init__(self) -> None:
        self.cargoQuery = CargoQueryAgent(API)
        self.fields = self.cargoQuery.getFields(["SF6_CharacterData", "SF6_FrameData"])
        self.sf6Frame = Backend("sf6_frame_data")
        self.sf6Character = Backend("sf6_chara")

    def close(self) -> None:
        self.sf6Character.closeConnection()
        self.sf6Frame.closeConnection()

    def getCancelArray(self, str: str) -> str:
        return ", ".join(str.split(" "))

    def getBlockArray(self, str: str) -> str:
        return ", ".join(list(str))

    def processItem(self, obj: dict) -> dict:
        if "title" in obj:
            title_data = obj.pop("title")
            obj.update(title_data)
        obj = {key: self.cargoQuery.textOrNull(value) for key, value in obj.items()}
        if obj.get("cancel", None):
            obj["cancel"] = self.getCancelArray(obj["cancel"])
        if obj.get("guard", None):
            obj["guard"] = self.getBlockArray(obj["guard"])
        return obj

    def fetchSFData(self, table: str) -> list:
        sf6Fields = list(self.fields.get(table, [])[0].keys())
        payload = []
        offset = 0
        while True:
            print(f"Offset: {offset}")
            data = self.cargoQuery.fetchData(
                {
                    "tables": table,
                    "fields": ",".join(sf6Fields),
                    "limit": PERPAGE,
                    "offset": offset,
                }
            )
            if not data:
                break
            data = [self.processItem(item) for item in data]
            offset += PERPAGE
            payload.extend(data)
        return payload

    def populateDatabase(self, init=False) -> None:
        if not self.sf6Character and self.sf6Frame:
            self.sf6Frame = Backend("sf6_frame_data")
            self.sf6Character = Backend("sf6_chara")

        if init:
            self.sf6Character.initTable(
                [
                    Column(name=item, type="TEXT")
                    for item in list(self.fields.get("SF6_CharacterData", [])[0].keys())
                ],
                "PRIMARY KEY (chara)",
            )
            self.sf6Frame.initTable(
                [
                    Column(name=item, type="TEXT")
                    for item in list(self.fields.get("SF6_FrameData", [])[0].keys())
                    if item != "chara"
                ]
                + [
                    Column(
                        name="chara",
                        type="TEXT REFERENCES sf6_chara(chara) ON DELETE CASCADE",
                    )
                ],
                "PRIMARY KEY (moveId)",
            )

        self.sf6Character.pushData(self.fetchSFData("SF6_CharacterData"))
        self.sf6Frame.pushData(self.fetchSFData("SF6_FrameData"))

    def downloadImages(self) -> None:
        titles = self.sf6Frame.fetchData("images, chara")
        titles = [
            {item.get("chara"): img.strip()}
            for item in titles
            for img in item.get("images", "").split(",")
            if img.strip()
        ]

        for i in range(0, len(titles), IMAGEBATCHSIZE):
            batch = titles[i: i+IMAGEBATCHSIZE]
            batchItem = self.cargoQuery.fetchImageURLs(batch)
            self.cargoQuery.downloadImages(batchItem, Path("./data/images"))


if __name__ == "__main__":
    streetFighter6 = StreetFighter6()
    streetFighter6.downloadImages()
