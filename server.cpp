#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#include "message.h"

#define buf_size 128

//connection descriptor
//holding clients socket and address
struct Descriptor {
    int socket;
    struct sockaddr_in address;
};

//receiving and handling messages from client
void *serve_single_client(void *arg) 
{
    //create client descriptor
    struct Descriptor* clientDescriptor = (struct Descriptor*)arg;

    printf("new connection from: %s:%d\n", 
            inet_ntoa(clientDescriptor->address.sin_addr), 
            clientDescriptor->address.sin_port);

    while(1) 
    {
        //recive message string
        char buf[buf_size] = "";
        int bytesRead = read(clientDescriptor->socket, buf, buf_size);
        if (bytesRead < 0)
        {
            perror("read() ERROR");
            exit(1);
        }
        else if (bytesRead == 0)
        {
            continue;
        }

        //create message object
        Message recivedMessage(clientDescriptor->address.sin_port, buf);
        printf("New message from: %d tag: %d message: %s\n", 
                recivedMessage.userID, recivedMessage.tag, recivedMessage.message.c_str());

        switch (recivedMessage.tag)
        {
        case TAG_JOIN_RANDOM_GAME:
            //TODO
            break;

        case TAG_JOIN_GAME:
            //TODO
            break;

        case TAG_HOST_GAME:
            //TODO
            break;

        case TAG_PAWN_MOVED:
        {
            Message response(0, TAG_PAWN_MOVED, recivedMessage.message);
            write(clientDescriptor->socket, response.getString().c_str(), response.size);
            break;
        }

        case TAG_SURRENDER:
            //TODO
            break;

        case TAG_OFFER_DRAW:
            //TODO
            break;

        case TAG_ACCEPT_DRAW:
            //TODO
            break;
        
        default:
            break;
        }
    }
}

int main() 
{
    //create address for communication purposes
    struct sockaddr_in addr;
    addr.sin_family = PF_INET;
    addr.sin_port = htons(7777);
    addr.sin_addr.s_addr = INADDR_ANY;

    //create socket
    //all messages are transmited using sockets
    int sock = socket(PF_INET, SOCK_STREAM, 0);

    //set the port on which we'll be listening
    bind(sock, (struct sockaddr*) &addr, sizeof(addr));

    //create listening socket
    //10 connections max
    listen(sock, 10);
    
    while(1) 
    {
        //create client descriptor
        struct Descriptor* clientDescriptor = new Descriptor;

        //accept connection from client
        socklen_t addrLen = sizeof(clientDescriptor->address);
        clientDescriptor->socket = accept(sock, 
                (struct sockaddr*) &clientDescriptor->address,
                &addrLen);

        //thread receiving and handling messages from client
        pthread_t tid;
        pthread_create(&tid, NULL, serve_single_client, clientDescriptor);
        
        //example how to send a message to the client
        /*
        int t = TAG_JOIN_RANDOM_GAME;
        std::string str = "a1";
        Message mes(0, t, str);

        for(int i = 0; i < 3; i++)
        {
            write(clientDescriptor->socket, mes.getString().c_str(), mes.size);
            sleep(0.2);
        }
        */

        pthread_detach(tid);
    }

    close(sock);
}