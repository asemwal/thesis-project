#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <inttypes.h>
#include <sys/select.h>
#include <time.h>
#include <sys/time.h>
#include <getopt.h>

/* BGPmon default port for MRT */
#define PORT 50003

/* BGP message size */
#define BGPSIZE 4096

struct MrtObjStruct {
	u_int32_t 	time;	/* timestamp */
	u_int16_t 	type;	/* type */
	u_int16_t 	subtype;/* subtype */
	u_int32_t 	length;	/* length of MRT message */
};
typedef struct MrtObjStruct MrtObj;

/*
 * Purpose: Print out usage and help information
 * Input: The pointer of the program name
 * Output:  none
 * Mikhail Strizhov @ Sept 20, 2011
 * M. Lawrence Weiku @ May 31, 2012
 */
void
usage(char *arg)
{
	fprintf(stderr, "\n");
	fprintf(stderr, "Usage: %s", arg);
	fprintf(stderr, "\n");
	fprintf(stderr, "        [-f <the MRT filename>] \n");
	fprintf(stderr, "        [-d <hostname>] \n");
	fprintf(stderr, "        [-p <port number>] \n");
	fprintf(stderr, "	    [-l <log file location>] \n");
	fprintf(stderr, "        [-n <messages before a second pause>] \n");
	fprintf(stderr, "        [-s <messages before quitting>] \n");
	fprintf(stderr, "        [-u] [-r] [-q] [-t] \n");

	fprintf(stderr, "Options: \n");
	fprintf(stderr,
		"\t-f <the MRT filename>	:   specify MRT file \n");
	fprintf(stderr,
	   "\t-d <hostname>		:   specity BGPmon hostname \n");
	fprintf(stderr,
		"\t-l <log file>		:   specify location of log file \n");

	fprintf(stderr,
		"\t-n <messages before pause>		:   specify the number of messages to send before pausing for a second\n");
	fprintf(stderr,
		"\t-u			:   keep TCP connection alive after the file is sent  \n");
	fprintf(stderr,
		"\t-r			:   read and send any data that is given, do not do sanity checks  \n");
	fprintf(stderr,
		"\t-q			:   quiet mode. \n");
	fprintf(stderr,
		"\t-t			:   replay mrt file as fast as possible. \n");

	fprintf(stderr, "Example: \n");
	fprintf(stderr,
		"        mrtfeeder -f updates.20011204.1008 -d marshal.netsec.colostate.edu -u \n");

	fprintf(stderr, "\n");
	exit(0);
}

/*
 * Purpose: main function
 * Input: args
 * Output:
 * Author: Mikhail Strizhov @ Sept 19, 2011
 */
int
main(int argc, char **argv)
{
	char 		filename [512];
	filename[0] = '\0';
	char 		logfile  [512] = "mrtfeeder.log";
	char 		hostname [512];
	hostname[0] = '\0';
	int 		port = -1;
	FILE           *FileIn = NULL;
	FILE           *log_file = NULL;
	int 		sd = 0;
	struct sockaddr_in pin;
	struct hostent *hp;

	MrtObj 		mrtPtr;
	char 		bgpmsg   [BGPSIZE];
	int 		num = 0;
	u_int32_t 	mrttime = 0;
	u_int16_t 	type = 0;
	u_int16_t 	subtype = 0;
	u_int32_t 	length = 0;

	u_int32_t 	offset = 0;
	u_int32_t 	sendtime = 0;
	time_t 		curr = 0;
	int 		keepTCP = 0;
	int 		freeRead = 0;
	int 		quiet = 0;
	int 		play_rt = 0;
	struct timeval 	start_time, end_time;
	double 		proc_time;

	int 		pauseNumMsgs = -1;
	int 		pauseSpecified = 0;

	int 		stopAfter = 0;

	char 		c;
	while ((c = getopt(argc, argv, "f:d:urql:tn:s:p:")) != -1) {
		switch (c) {
		case 'r':
			freeRead = 1;
			break;
		case 'u':
			keepTCP = 1;
			break;
		case 'f':
			strcpy(filename, optarg);
			break;
		case 'd':
			strcpy(hostname, optarg);
			break;
		case 'p':
			port = atoi(optarg);
			break;
		case 'q':
			quiet = 1;
			break;
		case 'l':
			strcpy(logfile, optarg);
			break;
		case 't':
			play_rt = 1;
			break;
		case 's':
			stopAfter = atoi(optarg);
			break;
		case 'n':
			pauseNumMsgs = atoi(optarg);
			pauseSpecified = 1;
			break;
		case 'h':
		case '?':
		default:
			usage(argv[0]);
			break;
		}
	}

	if (strlen(filename) == 0) {
		fprintf(stderr, "Filename is NULL\n");
		usage(argv[0]);
		return 1;
	}
	FileIn = fopen(filename, "rb");
	if (FileIn == NULL) {
		perror("fopen");
		fprintf(stderr, "File open failed!\n");
		return 1;
	}
	if (!(log_file = fopen(logfile, "a"))) {
		perror("fopen");
		fprintf(stderr, "Error opening log file.\n");
		return 1;
	}
	if (strlen(hostname) == 0) {
		fprintf(stderr, "Please specify a hostname\n");
		usage(argv[0]);
		return 0;
	}
	if (pauseSpecified && pauseNumMsgs < 0) {
		fprintf(stderr, "Unacceptable value for messages to be sent before a pause: %i\n", pauseNumMsgs);
		return -1;
	}
	if (stopAfter < 0) {
		fprintf(stderr, "Unacceptable value for messages to be sent before a pause: %i\n", pauseNumMsgs);
		return -1;
	}
	/* go find out about the desired host machine  */
	if ((hp = gethostbyname(hostname)) == 0) {
		fprintf(stderr, "Hostname could not be reached\n");
		return 0;
	}
	/* fill in the socket structure with host information  */
	memset(&pin, 0, sizeof(pin));
	pin.sin_family = AF_INET;
	pin.sin_addr.s_addr = ((struct in_addr *) (hp->h_addr))->s_addr;
	if (port == -1) {
		port = PORT;
	}
	pin.sin_port = htons(port);

	/* grab an Internet domain socket  */
	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
		fprintf(stderr, "Socket failed!\n");
		return 0;
	}
	/* connect to PORT on HOST  */
	if (connect(sd, (struct sockaddr *) & pin, sizeof(pin)) == -1) {
		fprintf(stderr, "Connect failed\n");
		return 0;
	}
	gettimeofday(&start_time, NULL);

	/* Read First Message to calculate offset */

	/* Read mrt header into structure */
	num = fread(&mrtPtr, sizeof(MrtObj), 1, FileIn);
	if (num < 0) {
		fprintf(stderr, "MRT header fread failed!\n");
		return 0;
	}
	curr = time(NULL);
	/* sanity checks */
	mrttime = ntohl(mrtPtr.time);
	/* check if time is a range of (0; currenttime) */
	if (mrttime < 0 || mrttime > curr) {
		fprintf(stderr, "Timestamp in MRT file not in range (0;%d)\n",
			(int) curr);
		return 0;
	}
	/* calculate offset */
	offset = (uint32_t) curr - mrttime;

	type = ntohs(mrtPtr.type);
	if (type != 11 &&
	    type != 12 &&
	    type != 13 &&
	    type != 16 &&
	type != 17 && type != 32 && type != 33 && type != 48 && type != 49) {
		fprintf(stderr, "Type is incorrect!\n");
		return 0;
	}
	subtype = ntohs(mrtPtr.subtype);

	length = ntohl(mrtPtr.length);
	if (length < 0 || length > BGPSIZE) {
		fprintf(stderr, "Length of BGPmessage is wrong\n");
		return 0;
	}
	if (!quiet)
		fprintf(stderr, "mrtObj time: %u, type %d, subtype: %d, length %d\n",
			mrttime, type, subtype, length);

	/* Read file contents into buffer */
	num = fread(bgpmsg, length, 1, FileIn);
	if (num < 0) {
		fprintf(stderr, "BGP msg fread failed!\n");
		return 0;
	}
	/* send mrt header */
	send(sd, &mrtPtr, sizeof(mrtPtr), 0);
	/* send bgpmessage */
	send(sd, bgpmsg, length, 0);

	int 		sent_count = 1;
	while (!feof(FileIn) && (stopAfter == 0 || sent_count < stopAfter)) {
		if (!freeRead) {
			/* Read mrt header into structure */
			num = fread(&mrtPtr, sizeof(MrtObj), 1, FileIn);
			if (num < 0) {
				fprintf(stderr, "MRT header fread failed!\n");
				break;
			}
			/* sanity checks */
			curr = time(NULL);
			mrttime = ntohl(mrtPtr.time);
			/* check if time is a range of (0; currenttime) */
			if (mrttime < 0 || mrttime > curr) {
				fprintf(stderr, "Timestamp in MRT file not in range (0;%d)\n",
					(int) curr);
				break;
			}
			type = ntohs(mrtPtr.type);
			if (type != 11 &&
			    type != 12 &&
			    type != 13 &&
			    type != 16 &&
			    type != 17 &&
			    type != 32 && type != 33 && type != 48 && type != 49) {
				fprintf(stderr, "Type is incorrect!\n");
				break;
			}
			subtype = ntohs(mrtPtr.subtype);

			length = ntohl(mrtPtr.length);
			if (length < 0 || length > BGPSIZE) {
				fprintf(stderr, "Length of BGPmessage is wrong: %d\n", length);
				fprintf(stderr,
					"mrtObj time: %d, type %d, subtype: %d, length %d\n",
					mrttime, type, subtype, length);
				break;
			}
			if (!quiet)
				fprintf(stderr,
					"mrtObj time: %d, type %d, subtype: %d, length %d\n",
					mrttime, type, subtype, length);

			/* Read file contents into buffer */
			num = fread(bgpmsg, length, 1, FileIn);
			if (num < 0) {
				fprintf(stderr, "BGP msg fread failed!\n");
				break;
			}
			sendtime = mrttime + offset;
			if (!quiet)
				fprintf(stderr,
					"mrttime: %u, offset: %d, sendtime: %d, curr: %u\n",
				mrttime, offset, sendtime, (uint32_t) curr);
			if ((sendtime > (uint32_t) curr)) {
				if (!quiet)
					fprintf(stderr, "Sleep for %u\n",
						(uint32_t) (sendtime - (uint32_t) curr));
				if (!play_rt)
					sleep(sendtime - (uint32_t) curr);
			}
			/* send mrt header */
			send(sd, &mrtPtr, sizeof(mrtPtr), 0);
			/* send bgpmessage */
			send(sd, bgpmsg, length, 0);
			sent_count++;

			if (pauseSpecified && sent_count % pauseNumMsgs == 0) {
				sleep(1);
			}
		} else {
			num = fread(bgpmsg, BGPSIZE, 1, FileIn);
			if (num < 0) {
				fprintf(stderr, "Unable to read file\n");
				return 1;
			}
			send(sd, bgpmsg, num, 0);
		}
	}			/* end feof  */

	gettimeofday(&end_time, NULL);
	proc_time = (end_time.tv_sec - start_time.tv_sec);
	proc_time += (end_time.tv_usec - start_time.tv_usec) / 1000000.0;

	/* close file */
	fclose(FileIn);

	/* write to log */
	fprintf(log_file, "%s,%d,%f\n", filename, sent_count, proc_time);
	fclose(log_file);

	fprintf(stderr, "The MRT file %s is successfully sent to %s\n", filename,
		hostname);

	/* check keepTCP flag   */
	if (keepTCP == 1) {
		char 		exitstring[] = "exit\n";
		char 		text     [20];
		while (1) {
			fputs("Enter 'exit' command to terminate TCP session: ", stdout);
			fflush(stdout);
			fgets(text, sizeof(text), stdin);
			if (strcmp(text, exitstring) == 0) {
				break;
			}
		}
	}
	close(sd);

	return 0;
}
