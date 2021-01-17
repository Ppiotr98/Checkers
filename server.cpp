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
        Message message(clientDescriptor->address.sin_port, buf);
        printf("New message from: %d tag: %d message: %s\n", 
                message.userID, message.tag, message.message.c_str());

        //TODO
        //client messages handling
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
        int serverID = addr.sin_port;
        int t = TAG_JOIN_RANDOM_GAME;
        std::string str = "a1";
        Message mes(serverID, t, str);
        const char* buf = mes.getString().c_str();

        for(int i = 0; i < 3; i++)
            write(clientDescriptor->socket, buf, mes.size);

        pthread_detach(tid);
    }

    close(sock);
}