import re
import time
from pickle import FRAME

from vgamepad import DS4_BUTTONS, DS4_DPAD_DIRECTIONS, VDS4Gamepad

# move this into a config file in the future
DIRECTION_MAPPING = {
    "1": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHWEST,
    "2": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
    "3": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHEAST,
    "4": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
    "5": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE,
    "6": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
    "7": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHWEST,
    "8": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
    "9": DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHEAST,
}

INPUT_MAPPING = {
    "LP": [DS4_BUTTONS.DS4_BUTTON_SQUARE],
    "MP": [DS4_BUTTONS.DS4_BUTTON_TRIANGLE],
    "HP": [DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT],
    "LK": [DS4_BUTTONS.DS4_BUTTON_CROSS],
    "MK": [DS4_BUTTONS.DS4_BUTTON_CIRCLE],
    "HK": [DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT],
    "PPP": [
        DS4_BUTTONS.DS4_BUTTON_SQUARE,
        DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
        DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
    ],
    "KKK": [
        DS4_BUTTONS.DS4_BUTTON_CROSS,
        DS4_BUTTONS.DS4_BUTTON_CIRCLE,
        DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT,
    ],
    "PP": [DS4_BUTTONS.DS4_BUTTON_SQUARE, DS4_BUTTONS.DS4_BUTTON_TRIANGLE],
    "KK": [DS4_BUTTONS.DS4_BUTTON_CROSS, DS4_BUTTONS.DS4_BUTTON_CIRCLE],
    "P": [DS4_BUTTONS.DS4_BUTTON_SQUARE],
    "K": [DS4_BUTTONS.DS4_BUTTON_CROSS],
}


FRAMES_PER_SECOND = 60
CHARGE_TIME = 40

class Gamepad:
    def __init__(self, regexTokens) -> None:
        print("Initializing gamepad")
        self.regex = regexTokens
        time.sleep(5)

    gamepad = VDS4Gamepad()

    def pressDirection(self, digit: str):
        print(f"Pressing input: {digit}")
        self.gamepad.directional_pad(DIRECTION_MAPPING[digit])

    def pressButton(self, attack: str):
        print(f"Pressing attack: {attack}")
        for input in INPUT_MAPPING[attack]:
            self.gamepad.press_button(input)

    def getButtons(self, input: str):
        ret = []
        for atk in INPUT_MAPPING:
            if atk in input:
                ret.append(atk)
                input = input.replace(atk, "")
        return ret

    def executeSequence(self, input: str):
        matches = re.findall(self.regex, input)
        print(matches)
        lastDirection = ""
        for match in matches:
            self.gamepad.reset()
            wait = 2
            if "[" in match:
                wait = CHARGE_TIME
            if "j." in match:
                direction = "9"
                if "[4]" in match:
                    self.pressDirection("4")
                    self.gamepad.update()
                    time.sleep(10 / FRAMES_PER_SECOND)
                    direction = "7"
                    wait -= 10
                self.pressDirection(direction)
                self.gamepad.update()
                time.sleep(2 / FRAMES_PER_SECOND)
            if "{" in match:
                frame_match = re.search(r"\{(\d+)F\}", match)
                frame = int(frame_match.group(1)) if frame_match else 2
                match = re.sub(r"\{\d+F\}", '', match)
                wait = frame
            buttons = [k for k in DIRECTION_MAPPING if k in match]
            for button in buttons:
                if button == lastDirection:
                    self.pressDirection("5")
                    self.gamepad.update()
                    time.sleep(wait / FRAMES_PER_SECOND)
                self.pressDirection(button)
                lastDirection = button
            buttons = self.getButtons(match)
            for button in buttons:
                self.pressButton(button)
            self.gamepad.update()
            print(f"holding for {wait} frames")
            time.sleep(wait / FRAMES_PER_SECOND)
        self.gamepad.reset()
        self.gamepad.update()


if __name__ == "__main__":
    gp = Gamepad(r"\([^)]*\)|((?:j\.)?\[?~?(?:\d[A-Z]+|\d|[A-Z]+)\]?(?:\{?\d+F\}?)?)")
    gp.executeSequence("4PPPKKK[5]{592F}2PPPKKK")
