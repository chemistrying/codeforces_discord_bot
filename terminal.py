import subprocess
import signal
import os

print("Hi this is your goddamn terminal for the goddamn bot.")
s = ""
while s != "quit":
    s = input()
    if s == "start":
        p = subprocess.Popen("py -3 C:\\Users\\toto4\\Desktop\\discord_bot\\main.py")
        while s != "end":
            s = input()
        p.kill()
        print("Bot killed.")

    