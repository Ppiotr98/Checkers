#include <random>

#include "game.h"

Player::Player()
{

}

Player::Player(int newID, std::string newNick)
: id(newID), nick(newNick)
{

}

Game::Game()
{
   
}

Game::Game(int newID, Player* player)
: id(newID), status(WAITING)
{
    //player assigned to random pawns color
    srand(time(NULL));
    bool choice = std::rand() % 2;
    if(choice)
    {
        //player will play with white
        whitePlayer = player;
        blackPlayer = nullptr;
    }
    else
    {
        //player will play with black
        blackPlayer = player;
        whitePlayer = nullptr;
    }
}

Player* getPlayer(std::vector <Player> players, int playerID)
{
    for(std::vector<Player>::size_type i = 0; i < players.size(); i++)
    {
        //its our player
        if(players[i].id == playerID)
        {
            return &players[i];
        }
    }

    //player with this id dosn't exist
    return nullptr;
}

Player* getOpponent(std::vector <Player> players, 
        std::vector <Game> games, int playerID)
{
    //find our player
    Player* ourPlayer = getPlayer(players, playerID);

    //player doesn't exist
    if (ourPlayer == nullptr)
    {
        return nullptr;
    }

    //find game
    Game* playerGame = &games[ourPlayer->gameID];

    //opponent doesn't exist
    if (playerGame->whitePlayer == nullptr
            || playerGame->blackPlayer == nullptr)
    {
        return nullptr;
    }

    //our player is playing white
    //return black player
    if(playerGame->whitePlayer->id == playerID)
    {
        return playerGame->blackPlayer;
    }
    //our player is playing black
    //return white player
    else if(playerGame->blackPlayer->id == playerID)
    {
        return playerGame->whitePlayer;
    }

    //player with this id dosn't exist
    return nullptr;
}