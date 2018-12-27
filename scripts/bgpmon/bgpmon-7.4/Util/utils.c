/*
 * 	Copyright (c) 2010 Colorado State University
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
 *	OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 *  File: utils.c
 * 	Authors:  Kevin Burnett, Dan Massey
 *  Date: July 21, 2008
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* needed for function inet_pton */
#include <arpa/inet.h>

#include "utils.h"
#include "log.h"
#include "bgpmon_defaults.h"


/*
 * sleepWithBreaks
 * Input: overall sleep time, thread status to update
 * Output: none
 * sleep for the required time, but wake up and update thread status
 * occasionally
 */
void
sleepWithBreaks(int seconds, time_t * threadStatus, int *shutdown)
{
	int 		i;
	int 		num_of_sleeps = seconds / THREAD_CHECK_INTERVAL;
	for (i = 0; i < num_of_sleeps; i++) {
		sleep(THREAD_CHECK_INTERVAL);
		/* after sleep update thread time */
		*threadStatus = time(NULL);
		/* check if BGPmon is closing */
		if (*shutdown != FALSE) {
			return;
		}
	}
	sleep(seconds % THREAD_CHECK_INTERVAL);
	/* after sleep update thread time */
	*threadStatus = time(NULL);
}

void 
bin2hexstr(const void *mem, int length, char *str, int max)
{
	char           *src = (char *) mem;
	unsigned 	i    , j;

	/* make sure to give the empty string in case the user doesn't check */
	str[0] = '\0';
	if (length <= 0) {
		return;
	}
	char           *t = str;
	/* create a string with 16 digits per line */
	for (i = 0; i < length; i += 16, src += 16) {
		/* for each line */
		for (j = 0; j < 16; j++) {
			/* if we still have data add it to the string */
			if (i + j < length) {
				/* add one digit to the string */
				if (strlen(str) + 2 < max) {
					t += sprintf(t, "%02X", src[j] & 0xff);
				} else {
					return;
				}
			} else {
				if (strlen(str) + 2 < max) {
					t += sprintf(t, "  ");
				} else {
					return;
				}
			}
			if (strlen(str) + 1 < max) {
				/* add a dash between pairs */
				t += sprintf(t, j % 2 ? " " : "-");
			} else {
				return;
			}
		}
		/* add a newline between lines */
		if (strlen(str) + 1 < max) {
			t += sprintf(t, "\n");
		} else {
			return;
		}
	}
	return;
}
