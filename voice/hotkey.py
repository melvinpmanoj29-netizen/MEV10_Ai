import keyboard
import time

from voice.voice_manager import voice_chat


listening_requested = False
running = True


def on_end():
    global listening_requested

    if not listening_requested:
        listening_requested = True


def on_esc():
    global running

    running = False


print("=== MEV10 Voice Assistant ===")
print("Press END to talk to MEV10.")
print("Press ESC to exit.\n")


keyboard.add_hotkey("end", on_end)
keyboard.add_hotkey("esc", on_esc)


try:

    while running:

        if listening_requested:

            listening_requested = False

            print("\n🔥 END pressed — MEV10 is listening...\n")

            voice_chat()

            print("\n✅ MEV10 is ready. Press END to talk again.\n")

        time.sleep(0.05)


finally:

    keyboard.unhook_all()

    print("\nMEV10 stopped.")