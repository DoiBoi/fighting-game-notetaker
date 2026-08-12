from Backend import Backend, Column
from CargoQuery import CargoQueryAgent

API = "https://srk.shib.live/api.php"
PERPAGE = 500


class StreetFighter6:
    def __init__(self) -> None:
        self.cargoQuery = CargoQueryAgent(API)
        self.fields = self.cargoQuery.getFields(["SF6_CharacterData", "SF6_FrameData"])

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

    def fetchData(self, table: str) -> list:
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
        sf6Frame = Backend("sf6_frame_data")
        sf6Character = Backend("sf6_chara")

        if init:
            sf6Character.initTable(
                [
                    Column(name=item, type="TEXT")
                    for item in list(self.fields.get("SF6_CharacterData", [])[0].keys())
                ],
                "PRIMARY KEY (chara)"
            )
            sf6Frame.initTable(
                [
                    Column(name=item, type="TEXT")
                    for item in list(self.fields.get("SF6_FrameData", [])[0].keys())
                    if item != "chara"
                ] + [
                    Column(name="chara", type="TEXT REFERENCES sf6_chara(chara) ON DELETE CASCADE")
                ],
                "PRIMARY KEY (moveId)"
            )

        sf6Character.pushData(self.fetchData("SF6_CharacterData"))
        sf6Frame.pushData(self.fetchData("SF6_FrameData"))

        sf6Character.closeConnection()
        sf6Frame.closeConnection()

if __name__ == "__main__":
    streetFighter6 = StreetFighter6()
    streetFighter6.populateDatabase()
