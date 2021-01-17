from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import Thread, Lock
from time import sleep
import socket
import emoji

from tags import *

# receiving and handling messages from server
def fetch_new_messages():
    while True:
        response = sock.recv(12)
        response = response.decode("utf-8")
        if response == "":
            continue

        print("New message from server: " + response)

        #TODO
        # server messages handling

        sleep(.05)

if __name__ == "__main__":
    # connect with server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 7777))

    # thread receiving and handling messages from server
    thread = Thread(target=fetch_new_messages, daemon=True)
    thread.start()

    # example how to send a message to the server
    message = str(TAG_JOIN_RANDOM_GAME) + ";" + "a1"
    for _ in range(3):
        sock.send(bytes(message, "utf-8"))
        sleep(.05)

    while True:
        continue