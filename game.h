#ifndef GAME_H
#define GAME_H

#include <string>

#define NOGAME -1

enum Status
{
    ENDED = 0,
    ONGOING = 1,
    WAITING = 2
};

enum Color
{
    WHITE = 0,
    BLACK = 1
};

class Player
{
public:
    int id;
    std::string nick;

    //if player is playing holds game id
    //if player is not playing equals -1
    int gameID;

    //socket of players client
    //used to address messages
    int clientSocket;

    Player(int newID, std::string newNick, int newSocket);
    Player();
};

class Game
{
public:
    int id;
    Status status;

    Player* whitePlayer;
    Player* blackPlayer;

    Game(int newID, Player* player);
    Game();
};

Player* getPlayer(Player* players, int playersCount, int playerID);
Player* getOpponent(Player* players, int playersCount, 
        Game* games, int gamesCount, int playerID);
Game* findGame(Game* games, int gamesCount);

#endif //GAME_H