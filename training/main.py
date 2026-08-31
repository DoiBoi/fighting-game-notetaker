import os
import queue
import re
import sys
import threading
import time
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import keyboard

from data_mining.Backend import Backend
from training.streetFighterTraining import SF6_REGEX, Character
from training.util.gamepad import FRAMES_PER_SECOND, Gamepad

frame = Backend("sf6_frame_data")
character = Backend("sf6_chara")


class Overlay:
    def __init__(self, alpha: float = 0.85, width: int = 380, height: int = 140):
        self.root = tk.Tk()
        self.root.title("SF6 Trainer")

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", alpha)

        self.root.geometry(f"{width}x{height}+40+40")
        self.root.configure(bg="#101010")

        self.move_var = tk.StringVar(value="Waiting for move...")
        self.status_var = tk.StringVar(value="")

        title = tk.Label(
            self.root,
            text="SF6 Training Overlay",
            fg="#e0e0e0",
            bg="#101010",
            font=("Segoe UI", 10, "bold"),
        )
        title.pack(pady=(8, 2))

        move_label = tk.Label(
            self.root,
            textvariable=self.move_var,
            fg="#ffffff",
            bg="#101010",
            font=("Consolas", 14),
            wraplength=width - 20,
            justify="center",
        )
        move_label.pack(pady=4)

        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            fg="#8fbf8f",
            bg="#101010",
            font=("Segoe UI", 9),
        )
        status_label.pack(pady=(0, 4))

        hint = tk.Label(
            self.root,
            text="Enter = execute   Esc = skip   drag to move",
            fg="#808080",
            bg="#101010",
            font=("Segoe UI", 8),
        )
        hint.pack(pady=(0, 6))
        # Make the borderless window draggable
        for widget in (self.root, title, move_label, hint):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)

        self._drag_offset = (0, 0)

        # Queue for thread-safe UI updates from the worker thread
        self.queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
        self.root.after(50, self._poll_queue)

    def _start_drag(self, event):
        self._drag_offset = (event.x, event.y)

    def _on_drag(self, event):
        x = self.root.winfo_pointerx() - self._drag_offset[0]
        y = self.root.winfo_pointery() - self._drag_offset[1]
        self.root.geometry(f"+{x}+{y}")

    def _poll_queue(self):
        try:
            while True:
                kind, text = self.queue.get_nowait()
                if kind == "move":
                    self.move_var.set(text)
                    self.status_var.set("")
                elif kind == "status":
                    self.status_var.set(text)
                elif kind == "close":
                    self.root.destroy()
                    return
        except queue.Empty:
            pass
        self.root.after(50, self._poll_queue)

    def set_move(self, text: str):
        self.queue.put(("move", text))

    def set_status(self, text: str):
        self.queue.put(("status", text))

    def close(self):
        self.queue.put(("close", ""))

    def run_mainloop(self):
        self.root.mainloop()


def training_worker(overlay: Overlay, moves_by_character: dict[str,Character]):
    gamepad = Gamepad(SF6_REGEX)

    for chara_name, moves in moves_by_character.items():
        all_moves = moves.getAllMoves()
        overlay.set_status(f"Character: {chara_name}")


        for move in all_moves:
            name = move.get("name", "")
            inp = move.get("input", "")
            overlay.set_move(f"[{chara_name}] {name}\n{inp}")

            action = {"value": None}
            done = threading.Event()

            def on_enter(_event=None):
                action["value"] = "execute"
                done.set()

            def on_esc(_event=None):
                action["value"] = "skip"
                done.set()

            keyboard.add_hotkey("enter", on_enter)
            keyboard.add_hotkey("esc", on_esc)

            done.wait()
            keyboard.remove_hotkey(on_enter)
            keyboard.remove_hotkey(on_esc)

            if action["value"] == "skip":
                overlay.set_status("Skipped")
                continue

            overlay.set_status("Executing...")
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
            overlay.set_status("Done")

    overlay.set_status("All characters complete")
    overlay.close()


def main():
    chara_rows = character.fetchData("chara")
    chara_names = [row.get("chara", "") for row in chara_rows if row.get("chara")]

    moves_by_character = {}
    for chara_name in chara_names:
        moves_by_character[chara_name] = Character(chara_name)

    overlay = Overlay(alpha=0.85)

    worker = threading.Thread(
        target=training_worker, args=(overlay, moves_by_character), daemon=True
    )
    worker.start()

    # Tkinter's mainloop must run on the main thread
    overlay.run_mainloop()


if __name__ == "__main__":
    sys.exit(main())
