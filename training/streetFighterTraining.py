import os
import re
import sys
import time
from functools import reduce

import keyboard
from util.gamepad import FRAMES_PER_SECOND, Gamepad

# Adds other files in this directory to run
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_mining.Backend import Backend

# Maybe create a config file somewhere in the future
frame = Backend("sf6_frame_data")
character = Backend("sf6_chara")


SF6_REGEX = r"\([^)]*\)|((?:j\.)?\[?~?(?:\d[A-Z]+|\d|[A-Z]+)\]?(?:\{?\d+F\}?)?)"


class Character:
    def __init__(self, character="") -> None:
        fetchedMoves = frame.fetchData(
            "moveId, input, chara, name, startup, active", f'chara = "{character}"'
        )
        self.moves = []
        self.specialMoves = []
        self.allMoves = fetchedMoves
        for move in fetchedMoves:
            if "(" not in move.get("name", "") and "(" not in move.get("input", ""):
                self.moves.append(move)
            else:
                self.specialMoves.append(move)
        self.gamepad = Gamepad

    def getInputs(self) -> list:
        return [move.get("input") for move in self.moves]

    def getIncludedMoves(self) -> list:
        return self.moves

    def getExcludedMoves(self) -> list:
        return self.specialMoves

    def getAllMoves(self) -> list:
        return self.allMoves

    def getSpecificMove(self, input, tag="") -> dict:
        move = next(
            (
                move
                for move in self.allMoves
                if move["input"] == input and tag in move["name"]
            ),
            {},
        )
        if not move:
            move = next((move for move in self.allMoves if move["input"] == input), {})
        return move

    def parseFrames(self, item) -> int:
        match = re.search(r"\d+", item.get("startup", ""))
        startUpFrames = int(match.group()) if match is not None else 0
        if item.get("active", "") is not None:
            activeFrames = reduce(
                lambda acc, curr: acc + int(curr),
                re.findall(r"\d+", item.get("active", "")),
                0,
            )
        else:
            activeFrames = 0
        return startUpFrames + activeFrames



def main():
    gamepad = Gamepad(SF6_REGEX)
    characters = character.fetchData("chara")
    # moves = Character(chara.get("chara", ""))
    moves = Character("C.Viper")
    for move in moves.getAllMoves():
        print(
            f"Preparing to execute {move.get('name', '')}: {move.get('input', '')}, press enter to proceed, esc to skip"
        )
        while True:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "enter":
                    print("Action confirmed!")
                    action = "execute"
                    break
                elif event.name == "esc":
                    print("Action skipped.")
                    action = "skip"
                    break
        if action == "skip":
            continue
        print(f"Executing {move.get('name', '')}: {move.get('input', '')}")
        prev_input = ""
        input = move.get("input", "")
        inputs = input.split("~")
        match = re.search(r"\(.+\)", move.get("name", ""))
        tag = match.group() if match is not None else ""
        for i in range(len(inputs)):
            item = inputs[i]
            move = moves.getSpecificMove(prev_input, tag)
            print(f"Pausing for {moves.parseFrames(move)} frames")
            time.sleep(moves.parseFrames(move) / FRAMES_PER_SECOND)
            gamepad.executeSequence(item)
            prev_input += item if prev_input == "" else f"~{item}"




if __name__ == "__main__":
    sys.exit(main())
    # moves = Character("Jamie")
    # gamepad = Gamepad(SF6_REGEX)
    # move = moves.getSpecificMove("4HP~HP~HK")
