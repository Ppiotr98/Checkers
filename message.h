#include <string>

#ifndef TAG_JOIN_RANDOM_GAME
//JOIN_RANDOM_GAME button clicked
#define TAG_JOIN_RANDOM_GAME 100
#endif

#ifndef TAG_JOIN_GAME
//JOIN_GAME button clicked and game ip passed
#define TAG_JOIN_GAME 101
#endif

#ifndef TAG_HOST_GAME
//HOST_GAME button clicked
#define TAG_HOST_GAME 102
#endif

#ifndef TAG_PAWN_MOVED
//pawn moved
#define TAG_PAWN_MOVED 103
#endif

#ifndef TAG_SURRENDER
//SURRENDER button clicked
#define TAG_SURRENDER 104
#endif

#ifndef TAG_OFFER_DRAW
//OFFER_DRAW button clicked
#define TAG_OFFER_DRAW 105
#endif

#ifndef TAG_ACCEPT_DRAW
//ACCEPT_DRAW button clicked
#define TAG_ACCEPT_DRAW 106
#endif

#ifndef TAG_GAME_STARTED
//game started
#define TAG_GAME_STARTED 107
#endif

#ifndef TAG_GAME_HOSTED
//game hosted and ip generated
#define TAG_GAME_HOSTED 108
#endif

#ifndef TAG_WRONG_IP
//wrong game ip passed
#define TAG_WRONG_IP 109
#endif

#ifndef TAG_DRAW_ACCEPTED
//opponent accepted draw
#define TAG_DRAW_ACCEPTED 110
#endif

#ifndef MESSAGE_H
#define MESSAGE_H

class Message
{
public:
    int userID;
    int tag;
    std::string message;
    
    //length of message
    int size;

    Message(int newUser, std::string dataString);
    Message(int newUser, int newTag, std::string newMessage);

    //return <tag>;<message> string
    std::string getString();
};


#endif //MESSAGE_H