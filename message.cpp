#include <iostream>
#include <string>
#include <unistd.h>

#include "message.h"

Message::Message(int newUser, std::string dataString)
{
    userID = newUser;

    tag = stoi(dataString.substr(0, dataString.find(";")));
    dataString.erase(0, dataString.find(";") + 1);

    message = dataString;

    size = dataString.length();
}

Message::Message(int newUser, int newTag, std::string newMessage)
: userID(newUser), tag(newTag), message(newMessage)
{
    size = std::to_string(tag).length() + 1 + message.length();
}

std::string Message::getString()
{
    return std::to_string(tag) + ";" + message;
}

void Message::sendto(int reciverSocket)
{
    write(reciverSocket, getString().c_str(), size);
}