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
        response = sock.recv(128)
        response = response.decode("utf-8")
        if response == "":
            continue

        print("New message from server: " + response)

        #TODO
        # server messages handling

if __name__ == "__main__":
    # wait for the server
    sleep(1)

    # connect with server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 7777))
    
    # thread receiving and handling messages from server
    thread = Thread(target=fetch_new_messages, daemon=True)
    thread.start()

    # example how to send a message to the server
    message = str(TAG_HOST_GAME) + ";" + "random_nick"
    for _ in range(3):
        sock.send(bytes(message, "utf-8"))
        sleep(.05)

    while True:
        continue