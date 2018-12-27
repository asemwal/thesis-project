/*
 *
 * 	Copyright (c) 2014 Colorado State University
 *
 *	Permission is hereby granted, free of charge, to any person
 *	obtaining a copy of this software and associated documentation
 *	files (the "Software"), to deal in the Software without
 *	restriction, including without limitation the rights to use,
 *	copy, modify, merge, publish, distribute, sublicense, and/or
 *	sell copies of the Software, and to permit persons to whom
 *	the Software is furnished to do so, subject to the following
 *	conditions:
 *
 *	The above copyright notice and this permission notice shall be
 *	included in all copies or substantial portions of the Software.
 *
 *	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 *	OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *	NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 *	HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 *	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 *	OTHER DEALINGS IN THE SOFTWARE.\
 *
 *
 *  File: translator.c
 *  Authors: Darshan Wash <darshan.wash@gmail.com>, dsp <dsp@2f30.org>
 *  Date: Sep. 2014
 *
 *  The purpose of the translator is to convert MRT files to XML.
 *  While doing the translation it brands the XML with values provided
 *  by the user.
 *  It also checks for messages that arrived out of order (time travelers)
 */

#include "translator.h"

void
usage(char *arg)
{
	fprintf(stderr, "\n");
	fprintf(stderr, "Usage: %s", arg);
	fprintf(stderr, "\n");
	fprintf(stderr, "        -f <mrt filename> \n");
	fprintf(stderr, "        [-i <monitor IP address>] \n");
	fprintf(stderr, "        [-v <monitor IP address version (4 or 6), "
		"default: 4>] \n");
	fprintf(stderr, "        [-p <monitor port number, default: 179>] \n");
	fprintf(stderr, "        [-g <geolocation file>] \n");
	fprintf(stderr, "        [-n <monitor AS number>] \n");
	fprintf(stderr, "        [-t toggle time traveler detection] \n");
	fprintf(stderr, "        [-l <logfile> log to file instead of syslog] \n");
}

/* This functions writes to log_fd (a global open fd) */
void
log_local(const char *fmt,...)
{
	va_list 	arglist;
	va_start(arglist, fmt);
	vfprintf(log_fd, fmt, arglist);
	fflush(log_fd);
	va_end(arglist);
}

int
main(int argc, char **argv)
{
	char 		c       , error = 0;
	int 		syslog = DEFAULT_USE_SYSLOG;
	int 		loglevel = DEFAULT_LOG_LEVEL;
	int 		logfacility = DEFAULT_LOG_FACILITY;
	int 		ret = 0;
	MRTheader 	mrtHeader;
	int 		num;
	u_int16_t 	type = 0;
	log_fd = NULL;
	FileIn = NULL;		/* the file pointers for input and log */
	monitor_addr_type = 4;	/* ipv4 is the default */
	monitor_port = 179;	/* default collector port */
	monitor_asn = 0;	/* default ASN */
	ttraveler_flag = 0;	/* to toggle time traveler detection in
				 * updates */
	file_flag = 0;
	strcpy(monitor_addr, "0.0.0.0");
	xml_buf[XMLBUFSIZ - 1] = '\0';	/* just in case, although BMF2XML
					 * uses stncpy */

	trans_log = log_err;	/* by default our logging func will do syslog */
	while ((c = getopt(argc, argv, "f:i:v:n:p:tl:hg:?")) != -1) {
		switch (c) {
		case 'f':
			file_flag = 1;
			strncpy(mrt_file, optarg, FILENAME_MAX_CHARS);
			break;
		case 'i':
			strncpy(monitor_addr, optarg, ADDR_MAX_CHARS);
			break;
		case 'v':
			monitor_addr_type = atoi(optarg);
			break;
		case 't':
			ttraveler_flag = 1;
			LIST_INIT(&seenl.head);
			break;
		case 'n':
			monitor_asn = atol(optarg);
			break;
		case 'g':
			if(geodb_init(&geolist, optarg)) {
				perror("failed to init geodb");
				return 1;
			}
			break;
		case 'p':
			monitor_port = atoi(optarg);
			break;
		case 'l':
			log_fd = fopen(optarg, "a");
			if (log_fd == NULL) {
				trans_log("failed to open log file");
				return EXIT_FAILURE;	/* from here on we goto
							 * exit to fclose */
			}
			trans_log = log_local;
			break;
		case 'h':
		case '?':
		default:
			usage(argv[0]);
			error = 1;
			goto exit;
		}
	}
	/* initilaze log module only if we don't use our local log */
	if (trans_log == log_err && init_log(argv[0], syslog, loglevel, logfacility)) {
		fprintf(stderr, "Failed to initialize log functions!\n");
		error = 1;
		goto exit;
	}
	if (!trans_is_valid_IP(monitor_addr, monitor_addr_type)) {
		trans_log("main: Invalid monitor IP address: %s in file %s", monitor_addr, mrt_file);
		error = 1;
		goto exit;
	}
	if (!file_flag) {
		usage(argv[0]);
		error = 1;
		goto exit;
	}
	FileIn = fopen(mrt_file, "rb");
	if (FileIn == NULL) {
		trans_log("File open failed!\n");
		error = 1;
		goto exit;
	}
	num = fread(&mrtHeader, sizeof(MRTheader), 1, FileIn);
	if (num <= 0) {
		trans_log("failed to read MRT header from file\n");
		error = 1;
		goto exit;
	}
	type = ntohs(mrtHeader.type);
	mrtHeader.type = type;
	if (type != 11 && type != 12 && type != 13 && type != 16 && type != 17 \
	    &&type != 32 && type != 33 && type != 48 && type != 49) {
		trans_log("MRT type is incorrect!\n");
		error = 1;
		goto exit;
	}
	rewind(FileIn);
	/* get start time */
	ret = gettimeofday(&tstart, NULL);
	if (ret == -1) {
		perror("clock_gettime failed");
		goto exit;
	}
	if (type == TABLE_DUMP || type == TABLE_DUMP_V2) {
		ret = trans_process_table_dump_file();
		if (ret == EXIT_FAILURE) {
			error = 1;
			goto exit;
		}
	} else {
		ret = trans_process_update_file();
		if (ret == EXIT_FAILURE) {
			error = 1;
			goto exit;
		}
	}
	ret = gettimeofday(&tend, NULL);
	if (ret == -1) {
		perror("gettimeofday failed");
		goto exit;
	}
	if (tend.tv_sec <= tstart.tv_sec) {
		trans_log("Rate [unable to calculate]");
	} else {
		rate = (double) (counter / (tend.tv_sec - tstart.tv_sec));
		trans_log("Rate [%.2f msgs/second]", rate);
	}
	trans_log("\t Processed [%zu msgs]\t Violating RFC size [%zu]\n", counter, largercounter);
	if (ttraveler_flag == 1)
		free_seen_list(&seenl);
exit:
	if (FileIn != NULL)
		fclose(FileIn);
	if (log_fd != NULL)
		fclose(log_fd);
	return (error == 1) ? EXIT_FAILURE : EXIT_SUCCESS;
}
