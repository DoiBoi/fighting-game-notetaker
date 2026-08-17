import time

import keyboard
import pygame

# Code is from Gemini, will require tweaking
class Input:
    def __init__(self) -> None:
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
        else:
            self.controller = None

    def readInput(self):
        try:
            while True:
                # --- 1. HANDLE KEYBOARD INPUTS ---
                # Check for individual hotkeys globally (works even if terminal isn't focused)
                if keyboard.is_pressed("space"):
                    print("⌨️ Keyboard Action: Spacebar pressed!")
                    time.sleep(0.1)  # Debounce delay

                if keyboard.is_pressed("w"):
                    print("⌨️ Keyboard Action: Moving forward (W)!")

                # --- 2. HANDLE CONTROLLER INPUTS ---
                if self.controller:
                    pygame.event.pump()  # Update controller states

                    # Check primary action button (usually index 0: Xbox A / PS X)
                    if self.controller.get_button(0):
                        print("🎮 Controller Action: Button 0 pressed!")
                        time.sleep(0.1)

                    # Check analog stick movement (with a 0.2 deadzone filter)
                    left_stick_y = self.controller.get_axis(1)
                    if abs(left_stick_y) > 0.2:
                        print(
                            f"🎮 Controller Action: Joystick moved Y-axis to {left_stick_y:.2f}"
                        )

                # --- 3. CPU PE RFORMANCE LIMITER ---
                time.sleep(1/60)  # Prevents your CPU from spiking to 100%

        except KeyboardInterrupt:
            print("\nExiting script. Goodbye!")
        finally:
            pygame.quit()

if __name__ == "__main__":
    input = Input()
    input.readInput()
