from Backend import Backend, Column
from CargoQuery import CargoQueryAgent

API = "https://srk.shib.live/api.php"

if __name__ == "__main__":
    cargoQuery = CargoQueryAgent(API)
    fields = cargoQuery.getFields(['SF6_CharacterData', 'SF6_FrameData'])
    sf6_fields = list(fields.get('SF6_FrameData', [])[0].keys())
    print(",".join(sf6_fields))
    # print(cargoQuery.fetchData({
    #     "tables": "SF6_FrameData",
    #     "fields": ",".join(sf6_fields)
    # }))



    # streetFighter.initTable([
    #     Column(name="character", type="TEXT"),
    #     Column(name="move_name", type="TEXT"),
    #     Column(name="input", type="TEXT")
    # ],"PRIMARY KEY (character, move_name)")

    # streetFighter.pushData([{
    #     "character": "ryu",
    #     "move_name": "shoryuken",
    #     "input": "623P"
    # }])
    # streetFighter.closeConnection()
