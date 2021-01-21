#ifndef GAME_H
#define GAME_H

#include <string>

enum Status
{
    ENDED = 0,
    ONGOING = 1,
    WAITING = 2
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

    Player(int newID, std::string newNick);
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

Player* getPlayer(std::vector <Player> players, int playerID);
Player* getOpponent(std::vector <Player> players, 
        std::vector <Game> games, int playerID);

#endif //GAME_H