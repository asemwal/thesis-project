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
 *  File: server.c
 *      Authors: Dan Massey
 *      Based on the sample TCP server from Beej's Guide:  http://beej.us/guide
 *  Date: Nov 4, 2011
 */

#include "server.h"

/*
 * Purpose: Get an IPv4 or IPv6 address
 * Input: The sockaddr that may be v4 or v6
 * Output:  The IP address
 * From Beej's Guide @ Nov 3, 2011
 */
void           *
get_in_addr(struct sockaddr * sa)
{
	if (sa->sa_family == AF_INET) {
		return &(((struct sockaddr_in *) sa)->sin_addr);
	}
	return &(((struct sockaddr_in6 *) sa)->sin6_addr);
}

/*
 * Purpose: setup a TCP socket to accept connections from the MRT sender
 * Input: The port to listen for connections
 * Output:   returns the socket or -1 on error
 * Modified from Beej's Guide @ Nov 3, 2011
 */
int 
setUpConnection(char *port)
{
	int 		sockfd;	/* listen on sock_fd */
	struct addrinfo hints, *servinfo, *p;
	int 		yes = 1;
	int 		rv;

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;	/* use my IP */

	if ((rv = getaddrinfo(NULL, port, &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return -1;
	}
	/* loop through all the results and bind to the first we can */
	for (p = servinfo; p != NULL; p = p->ai_next) {
		if ((sockfd = socket(p->ai_family, p->ai_socktype,
				     p->ai_protocol)) == -1) {
			perror("server: socket");
			continue;
		}
		if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes,
			       sizeof(int)) == -1) {
			perror("setsockopt");
			return -1;
		}
		if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
			close(sockfd);
			perror("server: bind");
			continue;
		}
		break;
	}

	if (p == NULL) {
		fprintf(stderr, "MRT server: failed to bind\n");
		return -1;
	}
	freeaddrinfo(servinfo);	/* all done with this structure */

	if (listen(sockfd, BACKLOG) == -1) {
		perror("listen");
		return -1;
	}
	return sockfd;
}

/*
 * Purpose: accept a connection from the MRT sender
 * Input: The socket to listen for connections
 * Output:   returns the socket to MRT sender or -1 on error
 * Modified from Beej's Guide @ Nov 3, 2011
 */
int 
acceptConnection(int sockfd)
{
	struct sockaddr_storage their_addr;	/* connector's address
						 * information */
	socklen_t 	sin_size;
	int 		new_fd;
	char 		s        [INET6_ADDRSTRLEN];

	printf("MRT server: waiting for a connection...\n");

	sin_size = sizeof their_addr;
	new_fd = accept(sockfd, (struct sockaddr *) & their_addr, &sin_size);
	if (new_fd == -1) {
		perror("accept");
		return -1;
	}
	inet_ntop(their_addr.ss_family, get_in_addr((struct sockaddr *) & their_addr), s, sizeof s);

	printf("MRT server: got connection from %s\n", s);

	return (new_fd);
}
