SERVER

compile: g++ server.cpp message.cpp game.cpp -o server.o -Wall -lpthread

run: ./server.o

CLIENT

run: python3 client.py
