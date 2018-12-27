/*
 *
 *      Copyright (c) 2011 Colorado State University
 *
 *      Permission is hereby granted, free of charge, to any person
 *      obtaining a copy of this software and associated documentation
 *      files (the "Software"), to deal in the Software without
 *      restriction, including without limitation the rights to use,
 *      copy, modify, merge, publish, distribute, sublicense, and/or
 *      sell copies of the Software, and to permit persons to whom
 *      the Software is furnished to do so, subject to the following
 *      conditions:
 *
 *      The above copyright notice and this permission notice shall be
 *      included in all copies or substantial portions of the Software.
 *
 *      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *      EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 *      OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *      NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 *      HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 *      WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *      FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 *      OTHER DEALINGS IN THE SOFTWARE.\
 *
 *
 *  File: server.h
 *      Authors: Dan Massey
 *      Based on the sample TCP server from Beej's Guide:  http://beej.us/guide
 *  Date: Nov 4, 2011
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>

#define BACKLOG 10     // how many pending connections queue will hold

/*----------------------------------------------------------------------------------------
 * Purpose: setup a TCP socket to accept connections from the MRT sender
 * Input: The port to listen for connections
 * Output:   returns the socket or -1 on error
 * Modified from Beej's Guide @ Nov 3, 2011
 * -------------------------------------------------------------------------------------*/
int setUpConnection(char *port);

/*----------------------------------------------------------------------------------------
 * Purpose: accept a connection from the MRT sender
 * Input: The socket to listen for connections
 * Output:   returns the socket to MRT sender or -1 on error
 * Modified from Beej's Guide @ Nov 3, 2011
 * -------------------------------------------------------------------------------------*/
int acceptConnection(int sockfd);
