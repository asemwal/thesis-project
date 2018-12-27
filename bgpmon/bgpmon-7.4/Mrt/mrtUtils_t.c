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
 *  File: mrtUtils_t.c
 *  Authors: Catherine Olschanowsky
 *  Date: Aug. 30, 2011
 */
#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include "mrtUtils_t.h"

/* a few global variables to play with across tests */
#define TEST_DIR "test/unit_test_input/mrt"

/* The suite initialization function.
 * Returns zero on success, non-zero otherwise.
 */
int
init_mrtUtils(void)
{
	return 0;
}

/* The suite cleanup function.
 * Returns zero on success, non-zero otherwise.
 */
int
clean_mrtUtils(void)
{
	return 0;
}



void
help_load_test_MRT(MRTheader * mrtHeader1, uint8_t * rawMessage1)
{

	/* start out by reading an MRT message from a file */
	uint8_t 	tmp    [4] = {0x4e, 0x78, 0x39, 0xf0};
	uint32_t 	timestamp;
	memmove(&timestamp, tmp, 4);
	timestamp = ntohl(timestamp);

	/* read the header and the raw message */
	char           *dir = TEST_DIR;
	char 		filename [256];
	sprintf(filename, "%s/mrt.16.4", dir);

	/* open the file and read in the entire message to the buffer */
	FILE           *testfile = fopen(filename, "r");
	if (!testfile) {
		CU_ASSERT(1 == 0);
		return;
	}
	int 		hdrSize = fread(mrtHeader1, 1, MRT_HEADER_LENGTH, testfile);
	CU_ASSERT(hdrSize == MRT_HEADER_LENGTH);
	memcpy(rawMessage1, mrtHeader1, MRT_HEADER_LENGTH);
	mrtHeader1->timestamp = ntohl(mrtHeader1->timestamp);
	CU_ASSERT(timestamp == mrtHeader1->timestamp);
	if (timestamp != mrtHeader1->timestamp) {
		fprintf(stderr, "t is%x h.t is %x\n", timestamp, mrtHeader1->timestamp);
	}
	mrtHeader1->type = ntohs(mrtHeader1->type);
	CU_ASSERT(16 == mrtHeader1->type);
	mrtHeader1->subtype = ntohs(mrtHeader1->subtype);
	CU_ASSERT(4 == mrtHeader1->subtype);
	mrtHeader1->length = ntohl(mrtHeader1->length);
	CU_ASSERT(63 == mrtHeader1->length);
	int 		msgSize = fread((rawMessage1 + MRT_HEADER_LENGTH), 1, mrtHeader1->length, testfile);
	CU_ASSERT(msgSize == mrtHeader1->length);
	fclose(testfile);
}
