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
 *  File: backlogUtils_t.c
 *  Authors: M. Lawrence Weikum
 *  Date: April 2014
 */
#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include "backlogUtil_t.h"
#include "../XML/xmlinternal.h"

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

/* */
void
testMRT_backlog_init()
{
	Backlog 	bl;
	CU_ASSERT(0 == backlog_init(&bl));

	/* now check to be sure that everything we need in there has actually been allocated */
	CU_ASSERT(NULL != bl.buffer);
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(0 == bl.end_pos);
	CU_ASSERT(START_BACKLOG_SIZE == bl.size);
	CU_ASSERT(START_BACKLOG_SIZE == bl.start_size);
	CU_ASSERT(0 == backlog_destroy(&bl));
	return;
}

/* this version of the test is not using any locks, because the test driver  */
/* only has a single thread */
void
testMRT_backlog_write()
{
	Backlog 	bl;
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	MRTheader 	mrtHeader;
	help_load_test_MRT(&mrtHeader, rawMessage);

	CU_ASSERT(0 == backlog_init(&bl));
	/* now write that message to the backlog */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));
	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);
	/* a subsequent write shouldn't really be any different, but just to be sure... */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));
	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT((MRT_HEADER_LENGTH + mrtHeader.length) * 2 == bl.end_pos);

	CU_ASSERT(0 == backlog_destroy(&bl));

	/* next test a write on a very small buffer so that we can see it wrap  */
	/* around a grow */
	/* this is guaranteed to be too small ( no room for the header ) */
	CU_ASSERT(0 == backlog_init_size(&bl, mrtHeader.length));
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT((mrtHeader.length * 2) == bl.size);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);
	CU_ASSERT(0 == backlog_destroy(&bl));

	/* now test writing when we have to wrap around -- need enough space, but */
	/* move the start_pos and end_pos toward the end of the buffer */
	CU_ASSERT(0 == backlog_init_size(&bl, 3 * (MRT_HEADER_LENGTH + mrtHeader.length)));
	/* trick it into thinking it is not empty and put the pointer toward the end */
	bl.start_pos = 2 * (MRT_HEADER_LENGTH + mrtHeader.length) + MRT_HEADER_LENGTH;
	bl.end_pos = bl.start_pos + 2;
	uint32_t 	message_size = (MRT_HEADER_LENGTH + mrtHeader.length);
	uint32_t 	prev_end = bl.end_pos;
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));
	CU_ASSERT((2 * (MRT_HEADER_LENGTH + mrtHeader.length) + MRT_HEADER_LENGTH) == bl.start_pos);
	CU_ASSERT((3 * (MRT_HEADER_LENGTH + mrtHeader.length)) == bl.size);
	CU_ASSERT((message_size - (bl.size - prev_end)) == bl.end_pos);
	CU_ASSERT(bl.start_pos > bl.end_pos);

	/* now that wrapping has happened try to write one more and make sure it works */
	prev_end = bl.end_pos;
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));
	CU_ASSERT((2 * (MRT_HEADER_LENGTH + mrtHeader.length) + MRT_HEADER_LENGTH) == bl.start_pos);
	CU_ASSERT((3 * (MRT_HEADER_LENGTH + mrtHeader.length)) == bl.size);
	CU_ASSERT((prev_end + message_size) == bl.end_pos);

	CU_ASSERT(0 == backlog_destroy(&bl));

}

void
testMRT_backlog_read()
{
	Backlog 	bl;
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	uint8_t 	rawMessage_r[MAX_MRT_LENGTH];
	MRTheader 	mrtHeader, mrtHeader_r;

	CU_ASSERT(0 == backlog_init(&bl));
	/* try to read from an empty backlog */
	CU_ASSERT(1 == backlog_read_MRT(&bl, &mrtHeader, rawMessage, MAX_MRT_LENGTH));

	/* now write that message to the backlog */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));

	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);

	/* now read the message */
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r, MAX_MRT_LENGTH));

	/* check that the messages are correct */
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));

	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));
}

void
testMRT_backlog_fastforward()
{
	Backlog 	bl;
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	uint8_t 	rawMessage_r[MAX_MRT_LENGTH];
	MRTheader 	mrtHeader, mrtHeader_r;
	CU_ASSERT(0 == backlog_init(&bl));

	/* case 1 */
	/* add 2 messages to the backlog */
	/* reset the starting position to the middle of the  */
	/* header of the first and then fastforward */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* manipulate the starting position */
	bl.start_pos += 4;

	/* run fast forward, read the message, verify the message */
	CU_ASSERT(0 == MRT_backlog_fastforward_BGP(&bl));
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* case 2 */
	/* add 2 messages to the backlog */
	/* shift the messages so that the first one wraps */
	/* in the header  */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the message in the buffer */
	uint32_t 	new_start = bl.size - 4;
	CU_ASSERT(&bl.buffer[new_start] == memmove(&bl.buffer[new_start],
					      &bl.buffer[bl.start_pos], 4));
	CU_ASSERT(&bl.buffer[0] == memmove(&bl.buffer[bl.start_pos],
					   &bl.buffer[bl.start_pos + 4],
				 MRT_HEADER_LENGTH + mrtHeader.length - 4));
	/* the start position is now 4 bytes before the end */
	bl.start_pos = bl.size - 4;
	/* end end position is the length of the message+header-4 */
	bl.end_pos = MRT_HEADER_LENGTH + mrtHeader.length - 4;
	/* write another message */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the starting pos 2 bytes */
	bl.start_pos += 2;

	/* run fast forward, read the message, verify the message */
	CU_ASSERT(0 == MRT_backlog_fastforward_BGP(&bl));
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* case 3 */
	/* shift the messages so that the first one wraps in the */
	/* body  */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the message in the buffer */
	new_start = bl.size - (MRT_HEADER_LENGTH + 4);
	CU_ASSERT(&bl.buffer[new_start] == memmove(&bl.buffer[new_start],
			&bl.buffer[bl.start_pos], (MRT_HEADER_LENGTH + 4)));
	CU_ASSERT(&bl.buffer[0] == memmove(&bl.buffer[bl.start_pos],
			 &bl.buffer[bl.start_pos + (MRT_HEADER_LENGTH + 4)],
				 MRT_HEADER_LENGTH + mrtHeader.length - 4));
	/* the start position is now 4 bytes before the end */
	bl.start_pos = new_start;
	/* end end position is the length of the message+header-4 */
	bl.end_pos = MRT_HEADER_LENGTH + mrtHeader.length - (MRT_HEADER_LENGTH + 4);
	/* write another message */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the starting pos 2 bytes */
	bl.start_pos += 2;

	/* run fast forward, read the message, verify the message */
	CU_ASSERT(0 == MRT_backlog_fastforward_BGP(&bl));
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* case 4 */
	/* shift the messages so that the second message wraps in the header */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the message in the buffer */
	new_start = bl.size - (MRT_HEADER_LENGTH + mrtHeader.length + 4);
	CU_ASSERT(&bl.buffer[new_start] == memmove(&bl.buffer[new_start],
						   &bl.buffer[bl.start_pos],
				     MRT_HEADER_LENGTH + mrtHeader.length));
	bl.start_pos = new_start;
	/* end end position is the length of the message+header-4 */
	bl.end_pos = new_start + MRT_HEADER_LENGTH + mrtHeader.length;
	/* write another message */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));

	/* run fast forward, read the message, verify the message */
	CU_ASSERT(0 == MRT_backlog_fastforward_BGP(&bl));
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r,
			      mrtHeader.length));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));
}

void
testMRT_backlog_wrap()
{

	Backlog 	bl;
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	uint8_t 	rawMessage_r[MAX_MRT_LENGTH];
	MRTheader 	mrtHeader, mrtHeader_r;

	/* test header wrap */
	CU_ASSERT(0 == backlog_init(&bl));
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));

	/* move the message in the buffer */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);
	uint32_t 	new_start = bl.size - 4;
	CU_ASSERT(&bl.buffer[new_start] == memmove(&bl.buffer[new_start],
					      &bl.buffer[bl.start_pos], 4));
	CU_ASSERT(&bl.buffer[0] == memmove(&bl.buffer[bl.start_pos],
					   &bl.buffer[bl.start_pos + 4],
				 MRT_HEADER_LENGTH + mrtHeader.length - 4));
	bl.start_pos = bl.size - 4;
	bl.end_pos = bl.end_pos - 4;

	/* now read the message */
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));

	/* check that the messages are correct */
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* test body wrap */
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage,
				     MRT_HEADER_LENGTH + mrtHeader.length));
	/* move the message in the buffer */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);
	new_start = bl.size - (MRT_HEADER_LENGTH + 4);
	CU_ASSERT(&bl.buffer[new_start] == memmove(&bl.buffer[new_start],
						   &bl.buffer[bl.start_pos],
						   MRT_HEADER_LENGTH + 4));
	CU_ASSERT(&bl.buffer[0] == memmove(&bl.buffer[bl.start_pos],
			   &bl.buffer[bl.start_pos + MRT_HEADER_LENGTH + 4],
					   mrtHeader.length - 4));
	bl.start_pos = bl.size - MRT_HEADER_LENGTH - 4;
	bl.end_pos = bl.end_pos - MRT_HEADER_LENGTH - 4;

	/* now read the message */
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r,
					MAX_MRT_LENGTH));

	/* attempt to read from the buffer  */
	/* check that the messages are correct */
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));


	/* clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));
}

void
testMRT_backlog_resize()
{

	Backlog 	bl;
	uint32_t 	size;
	CU_ASSERT(0 == backlog_init(&bl));
	size = bl.size;
	CU_ASSERT(0 == backlog_expand(&bl));
	CU_ASSERT(size * 2 == bl.size);
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(0 == bl.end_pos);
	CU_ASSERT(0 == backlog_shrink(&bl, size));
	CU_ASSERT(size == bl.size);
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(0 == bl.end_pos);
	CU_ASSERT(0 == backlog_destroy(&bl));

	/* this time write a message, resize and then read it */
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	uint8_t 	rawMessage_r[MAX_MRT_LENGTH];
	MRTheader 	mrtHeader, mrtHeader_r;
	CU_ASSERT(0 == backlog_init(&bl));
	size = bl.size;

	/* now write that message to the backlog */
	help_load_test_MRT(&mrtHeader, rawMessage);
	CU_ASSERT(0 == backlog_write_MRT(&bl, rawMessage, MRT_HEADER_LENGTH + mrtHeader.length));

	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);

	CU_ASSERT(0 == backlog_expand(&bl));
	CU_ASSERT(size * 2 == bl.size);
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(MRT_HEADER_LENGTH + mrtHeader.length == bl.end_pos);

	/* read the message and make sure the expand didn't mess it up */
	CU_ASSERT(0 == backlog_read_MRT(&bl, &mrtHeader_r, rawMessage_r, MAX_MRT_LENGTH));
	/* check that the messages are correct */
	CU_ASSERT(0 == memcmp(&mrtHeader, &mrtHeader_r, MRT_HEADER_LENGTH));
	CU_ASSERT(mrtHeader.timestamp == mrtHeader_r.timestamp);
	CU_ASSERT(mrtHeader.type == mrtHeader_r.type);
	CU_ASSERT(mrtHeader.subtype == mrtHeader_r.subtype);
	CU_ASSERT(mrtHeader.length == mrtHeader_r.length);
	CU_ASSERT(0 == memcmp(rawMessage + MRT_HEADER_LENGTH, rawMessage_r, mrtHeader.length));

	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);
	CU_ASSERT(0 == backlog_destroy(&bl));
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

void
testXML_backlog_write()
{
/*
  Backlog bl;

  /*XML message that we'll be writing to the backlog */
	char           *xmlMsg = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"1\">94.126.183.247</ADDRESS><PORT>179</PORT><ASN4>59469</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1396466844</TIMESTAMP><DATETIME>2014-04-02T19:27:24Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>676448809</SEQUENCE_NUMBER><COLLECTION>LIVE</COLLECTION><bgp:UPDATE bgp_message_type=\"2\"><bgp:ORIGIN optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"1\">IGP</bgp:ORIGIN><bgp:AS_PATH optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"2\"><bgp:AS_SEQUENCE><bgp:ASN4>59469</bgp:ASN4><bgp:ASN4>1299</bgp:ASN4><bgp:ASN4>2914</bgp:ASN4><bgp:ASN4>4761</bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH><bgp:NEXT_HOP optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"3\" afi=\"1\">94.126.183.247</bgp:NEXT_HOP><bgp:NLRI afi=\"1\">103.27.36.0/24</bgp:NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF003B02000000204001010040021202040000E84D0000051300000B62000012994003045E7EB7F718671B24</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"103.27.36.0/24\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>\0";
	uint32_t 	msgSize = strlen(xmlMsg);




	/* Going to the write to the backlog twice; each time checking that the  */
	/* backlog pointers are in the correct places. */

	CU_ASSERT(0 == backlog_init(&bl));
	/* writing the message to the backlog */
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, msgSize));
	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(msgSize == bl.end_pos);
	/* doing it one more time */
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, msgSize));
	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(msgSize * 2 == bl.end_pos);
	/* wonderful! let's clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));


	/* now test writing when we have to wrap around -- need enough space, but */
	/* move the start_pos and end_pos toward the end of the buffer */
	CU_ASSERT(0 == backlog_init_size(&bl, 3 * msgSize));
	/* trick it into thinking it is not empty and put the pointer toward the end */
	bl.start_pos = 2 * (msgSize) + 5;
	bl.end_pos = bl.start_pos + 2;
	uint32_t 	message_size = msgSize;
	uint32_t 	prev_end = bl.end_pos;
	/* writing to the buffer and checking that the pointers are in the right spot */
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, msgSize));
	CU_ASSERT((2 * (msgSize) + 5) == bl.start_pos);
	CU_ASSERT((3 * msgSize) == bl.size);
	CU_ASSERT((message_size - (bl.size - prev_end)) == bl.end_pos);
	CU_ASSERT(bl.start_pos > bl.end_pos);

	/* now that wrapping has happened try to write one more & make sure it works */
	prev_end = bl.end_pos;
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, msgSize));
	CU_ASSERT((2 * msgSize + 5) == bl.start_pos);
	CU_ASSERT((3 * msgSize) == bl.size);
	CU_ASSERT((prev_end + message_size) == bl.end_pos);
	/* great! clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));

	*/
}

void
testXML_backlog_read()
{				/*
	   Backlog bl;
	 
	   /*space where we will put messages as we read them out of the backlog */
	char           *xmlMsgSpace = (char *) calloc(XML_BUFFER_LEN, sizeof(char));
	uint32_t 	msgSize = 0;

	/* message that we will be writing to the backlog */
	char           *xmlMsg = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"1\">94.126.183.247</ADDRESS><PORT>179</PORT><ASN4>59469</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1396466844</TIMESTAMP><DATETIME>2014-04-02T19:27:24Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>676448809</SEQUENCE_NUMBER><COLLECTION>LIVE</COLLECTION><bgp:UPDATE bgp_message_type=\"2\"><bgp:ORIGIN optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"1\">IGP</bgp:ORIGIN><bgp:AS_PATH optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"2\"><bgp:AS_SEQUENCE><bgp:ASN4>59469</bgp:ASN4><bgp:ASN4>1299</bgp:ASN4><bgp:ASN4>2914</bgp:ASN4><bgp:ASN4>4761</bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH><bgp:NEXT_HOP optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"3\" afi=\"1\">94.126.183.247</bgp:NEXT_HOP><bgp:NLRI afi=\"1\">103.27.36.0/24</bgp:NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF003B02000000204001010040021202040000E84D0000051300000B62000012994003045E7EB7F718671B24</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"103.27.36.0/24\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>\0";
	uint32_t 	xmlMsgSize = strlen(xmlMsg);


	CU_ASSERT(0 == backlog_init(&bl));


/* try to read from an empty backlog */
	CU_ASSERT(1 == backlog_read_XML(&bl, xmlMsgSpace, XML_BUFFER_LEN, &msgSize));

	/* now write a message to the backlog */
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, xmlMsgSize));

	/* make sure that the write actually happened */
	CU_ASSERT(0 == bl.start_pos);
	CU_ASSERT(xmlMsgSize == bl.end_pos);

	/* now read the message */
	CU_ASSERT(0 == backlog_read_XML(&bl, xmlMsgSpace, XML_BUFFER_LEN, &msgSize));

	/* check that the messages are the same */
	CU_ASSERT(0 == strncmp(xmlMsg, xmlMsgSpace, xmlMsgSize));

	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* do it again for good measure */
	memset(xmlMsgSpace, '\0', msgSize);
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, xmlMsgSize));
	CU_ASSERT(0 == backlog_read_XML(&bl, xmlMsgSpace, XML_BUFFER_LEN, &msgSize));
	CU_ASSERT(0 == strncmp(xmlMsg, xmlMsgSpace, xmlMsgSize));
	CU_ASSERT(bl.end_pos == bl.start_pos);

	/* clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));
	free(xmlMsgSpace);
	*/
}

void
testXML_backlog_fastforward()
{
/*
  Backlog bl;

  /*Space where we will be reading the xml messages into from backlog */
	char           *xmlMsgSpace = (char *) calloc(XML_BUFFER_LEN, sizeof(char));
	uint32_t 	msgSize = 0;

	/* Xml message we will be writing */
	char           *xmlMsg = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"1\">94.126.183.247</ADDRESS><PORT>179</PORT><ASN4>59469</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1396466844</TIMESTAMP><DATETIME>2014-04-02T19:27:24Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>676448809</SEQUENCE_NUMBER><COLLECTION>LIVE</COLLECTION><bgp:UPDATE bgp_message_type=\"2\"><bgp:ORIGIN optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"1\">IGP</bgp:ORIGIN><bgp:AS_PATH optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"2\"><bgp:AS_SEQUENCE><bgp:ASN4>59469</bgp:ASN4><bgp:ASN4>1299</bgp:ASN4><bgp:ASN4>2914</bgp:ASN4><bgp:ASN4>4761</bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH><bgp:NEXT_HOP optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"3\" afi=\"1\">94.126.183.247</bgp:NEXT_HOP><bgp:NLRI afi=\"1\">103.27.36.0/24</bgp:NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF003B02000000204001010040021202040000E84D0000051300000B62000012994003045E7EB7F718671B24</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"103.27.36.0/24\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>\0";
	uint32_t 	xmlMsgSize = strlen(xmlMsg);



	CU_ASSERT(0 == backlog_init(&bl));

	/* add 2 messages to the backlog */
	/* reset the starting position to the middle of the  */
	/* header of the first and then fastforward */
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, xmlMsgSize));
	CU_ASSERT(0 == backlog_write(&bl, xmlMsg, xmlMsgSize));

	/* run fast forward, read the message, should get back 1 - backlog is empty */
	CU_ASSERT(2 == XML_backlog_fastforward(&bl));	/* = 2 b/c we're fast
							 * forwarding 2 msgs */
	CU_ASSERT(1 == backlog_read_XML(&bl, xmlMsgSpace, XML_BUFFER_LEN, &msgSize));
	/* check the status of the backlog */
	CU_ASSERT(bl.end_pos == bl.start_pos);


	/* clean up */
	CU_ASSERT(0 == backlog_destroy(&bl));
	free(xmlMsgSpace);
	*/

}
