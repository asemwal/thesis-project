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
 *  File: file.c
 *      Authors: Dan Massey
 *      opens an timestamped output file for storing MRT results
 *  Date: Nov 7, 2011
 */

#include "defs.h"
#include "file.h"

/*
 * Purpose: create a unique file that can be used to store data
 * Input: the base name for the file and a filetype which can be
 *        either DATA for storing MRT binary data or SUMMARY for
 *        storing MRT header summary information
 * Output:  the file descriptor or NULL on error
 * Mikhail Strizhov @ Nov 3, 2011
 */
FILE           *
openFile(char *filename, int filetype)
{
	FILE           *fp = NULL;
	char 		timestamp[TIMESTAMP_SIZE];
	char 		newfile  [MAXNAME + TIMESTAMP_SIZE + SUFFIX_SIZE];

	/* get the local timestamp to the filename  */
	time_t 		rawtime = time(NULL);
	struct tm      *Tm;
	Tm = localtime(&rawtime);
	if (sprintf(timestamp, "%4d:%02d:%02d:%02d:%02d:%02d",
	       Tm->tm_year + 1900, Tm->tm_mon + 1, Tm->tm_mday, Tm->tm_hour,
		    Tm->tm_min, Tm->tm_sec) < 0) {
		fprintf(stderr, "Could not create filename buffer %s\n", filename);
		return NULL;
	}
	/* check filename length */
	if (strlen(filename) > MAXNAME) {
		fprintf(stderr, "File name is bigger than the limit %d characters", MAXNAME);
		return NULL;
	}
	/* add timestamp and suffix to the filename */
	if (filetype == DATA) {
		if (sprintf(newfile, "%s-%s%s", filename, timestamp, BIN_SUFFIX) < 0) {
			fprintf(stderr, "Could not create filename buffer %s\n", filename);
			return NULL;
		}
	} else {
		if (sprintf(newfile, "%s-%s%s", filename, timestamp, TXT_SUFFIX) < 0) {
			fprintf(stderr, "Could not create filename buffer %s\n", filename);
			return NULL;
		}
	}

	/* open file */
	if ((fp = fopen(newfile, "w")) == NULL) {
		fprintf(stderr, "Cannot open %s file.\n", filename);
		return NULL;
	}
	return fp;
}
