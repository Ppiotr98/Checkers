SERVER

compile: g++ server.cpp message.cpp -o server.o -Wall -lpthread

run: ./server.o

CLIENT

run: python3 klient.py
