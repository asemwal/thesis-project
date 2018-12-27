/*
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
 *      OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 *      File: mrtfeedtest.c
 *      Authors:  Dan Massey, Mikhail Strizhov
 *      Date: Nov 7, 2011
 *      Accepts a connection from an MRT sender,  logs the MRT data to a
 *      file,  and notes any errors in te MRT data.   Useful for testing
 *      the validity of data coming from an MRT sender.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

#include "server.h"
#include "file.h"
#include "readMRT.h"
#include "defs.h"

/* define 5 main global variables  */
int 		serv_fd;	/* server socket descriptor */
int 		accept_fd;	/* new connection socket descriptor */
FILE           *mrtData;	/* MRT data file pointer */
FILE           *mrtSummary;	/* MRT header file pointer */
int 		conn_state;	/* connection state */

/*
 * Purpose: Print out usage and help information
 * Input: The pointer of the program name
 * Output:  none
 * Mikhail Strizhov @ Nov 3, 2011
 */
void 
usage(char *arg)
{
	fprintf(stderr, "\n");
	fprintf(stderr, "Usage: %s", arg);
	fprintf(stderr, "\n");
	fprintf(stderr, "        -p <port number> \n");
	fprintf(stderr, "        -f <MRT output filename> \n");

	fprintf(stderr, "Example: \n");
	fprintf(stderr, "        mrtfeedtest -p 7777 -f mrtdatafile\n");
	fprintf(stderr, "\n");
	exit(EXIT_SUCCESS);
}

/*
 * Purpose: SIGINT signal function, cleanly close the program
 * Input:  signal value
 * Output:  none
 * Mikhail Strizhov @ Nov 7, 2011
 */
void 
closeTester(int sig)
{
	/* check if server' state is CONNECTED */
	if (conn_state == CONNECTED) {
		/* close client's socket descriptors */
		if (close(accept_fd) == -1)
			fprintf(stderr, "Unable to close clients connection\n");
		/* close MRT binary and MRT summary files */
		if (mrtData != NULL && fclose(mrtData) == EOF)
			fprintf(stderr, "Unable to close MRT binary file\n");
		if (mrtSummary != NULL && fclose(mrtSummary) == EOF)
			fprintf(stderr, "Unable to close MRT summary file\n");
		/* set the state to LISTEN and set file pointers to NULL */
		conn_state = LISTEN;
		mrtData = NULL;
		mrtSummary = NULL;
	}
	/* if current connection closed,  return to listening */
	if (sig == CONTINUE_LISTENING)
		return;

	/* an error or signal occurred,  close the listener and exit */
	if (conn_state == LISTEN) {
		if (close(serv_fd) == -1)
			fprintf(stderr, "Unable to close server\n");
	}
	if (sig == MRT_DATA_FILE_ERROR)
		fprintf(stderr, "File open for MRT data failed.\n");
	else if (sig == MRT_SUMMARY_FILE_ERROR)
		fprintf(stderr, "File open for MRT header summary failed.\n");
	else if (sig == ACCEPT_ERROR)
		fprintf(stderr, "Error accepting connection.\n");
	else
		/* must have been some signal that triggered this, close */
		fprintf(stderr, "Testing complete, view files for results.\n");

	exit(EXIT_SUCCESS);
}

/*
 * Purpose: Parse the command line and establish a listener.
 *          Then accept a connection from an MRT sender,  store and validate the date recvd
 * Input: port number and filename from the command line
 * Output:  exits with 0 on success,  -1 on error
 * Mikhail Strizhov, Dan Massey @ Nov 3, 2011
 */
int 
main(int argc, char *argv[])
{
	/* init connection state */
	conn_state = UNCONNECTED;

	/* setup signal handler */
	struct sigaction sa;	/* signal handler structure */
	sa.sa_handler = closeTester;
	sa.sa_flags = 0;
	sigemptyset(&sa.sa_mask);
	if (sigaction(SIGINT, &sa, NULL) == -1) {
		fprintf(stderr, "Signal handler function failed\n");
		exit(EXIT_FAILURE);
	}
	/* parse the command line arguments to get port and output file  */
	char           *portnumber = NULL;
	char           *filename = NULL;
	char 		c;
	while ((c = getopt(argc, argv, "p:f:")) != -1) {
		switch (c) {
		case 'p':
			portnumber = argv[2];
			break;
		case 'f':
			filename = argv[4];
			break;
		case 'h':
		case '?':
		default:
			usage(argv[0]);
			break;
		}
	}
	if (argc < 5 || argc > 5) {
		usage(argv[0]);
	}
	if (portnumber == NULL) {
		fprintf(stderr, "You must specify a port number. \n");
		usage(argv[0]);
	}
	if (filename == NULL) {
		fprintf(stderr, "You must specify a filename. \n");
		usage(argv[0]);
	}
	if (strlen(filename) > MAXNAME) {
		fprintf(stderr, "File name is bigger than the limit %d characters", MAXNAME);
		usage(argv[0]);
	}
	/* have port number,  set up a socket listening on that port  */
	if ((serv_fd = setUpConnection(portnumber)) == -1) {
		fprintf(stderr, "Failed to setup a listener to receive MRT data. \n");
		exit(EXIT_FAILURE);
	}
	conn_state = LISTEN;

	/* until program stopped,  accept a connection  */
	/* then create two ouptput files,  read and validate MRT data from that connection  */
	while (1) {

		/* accept a new connection */
		if ((accept_fd = acceptConnection(serv_fd)) == -1) {
			fprintf(stderr, "Failed to accept connection from MRT data source. \n");
			closeTester(ACCEPT_ERROR);
		}
		/* client is connected, switch the state */
		conn_state = CONNECTED;

		/* open a new output file for MRT data */
		if ((mrtData = openFile(filename, DATA)) == NULL)
			closeTester(MRT_DATA_FILE_ERROR);
		/* open a new output file for MRT header summaries */
		if ((mrtSummary = openFile(filename, SUMMARY)) == NULL)
			closeTester(MRT_SUMMARY_FILE_ERROR);


		/* read and validate MRT data from this connection */
		if (readMRTdata(accept_fd, mrtData, mrtSummary) == -1)
			fprintf(stderr, "Error reading data from this connection. Closing connection...\n");

		/* cleanly close the program  */
		closeTester(CONTINUE_LISTENING);

	}
	exit(EXIT_SUCCESS);
}
