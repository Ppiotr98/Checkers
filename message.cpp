#include <iostream>
#include <string>

#include "message.h"

Message::Message(int clientAddress, std::string dataString)
{
    userID = clientAddress;

    tag = stoi(dataString.substr(0, dataString.find(";")));
    dataString.erase(0, dataString.find(";") + 1);

    message = dataString.substr(0, dataString.find(";"));
    dataString.erase(0, dataString.find(";") + 1);

    size = (std::to_string(clientAddress)).length() + 1 + dataString.length();
}

Message::Message(int newUser, int newTag, std::string newMessage)
: userID(newUser), tag(newTag), message(newMessage)
{
    size = std::to_string(userID).length() + std::to_string(tag).length() + message.length() + 2;
}

std::string Message::getString()
{
    return std::to_string(userID) + ";" + std::to_string(tag) + ";" + message;
}