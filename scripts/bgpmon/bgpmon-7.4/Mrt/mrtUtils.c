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
 *	OTHER DEALINGS IN THE SOFTWARE.\
 *
 *
 *  File: mrtUtils.c
 * 	Authors: Dan Massey, Cathie Olschanowsky
 *
 *  Date: April 2012
 *  Edited: June 2012
 */

/* externally visible structures and functions for mrts */
#include "mrtUtils.h"
#include "../Util/utils.h"

/*#define DEBUG */


/******************************************************************************
 * MRT_readMessage
 * Input: socket, pointer to the MRT header to populate, pointer to space
 *        for the raw message
 * Return: -1 on read error
 *          n on success; n= the number of messages fast forwarded over
 *                        to get to the next valid header
 *          0 on total sucess > 0 with some failures, but can proceed
 *****************************************************************************/
int
MRT_readMessage(int socket, MRTheader * mrtHeader, uint8_t * rawMessage)
{

	int 		forward = 0;

	while (MRT_parseHeader(socket, mrtHeader)) {
		log_warning("mrtThread, header parsing failed\n");
		if (MRT_fastForwardToBGPHeader(socket)) {
			return -1;
		}
		forward++;
	}
	if (forward > 0) {
		log_err("mrtThread (readMessage): had to fast forward %d times to recover, new length is %lu\n", forward, mrtHeader->length);
	}
	int 		read_len = readn(socket, rawMessage, mrtHeader->length);
	if (read_len != mrtHeader->length) {
		log_err("mrtThread, message reading failed\n");
		return -1;
	}
	return forward;
}

/******************************************************************************
 * MRT_readMessageNoHeader
 * Input: socket, pointer to the MRT header to populate, pointer to space
 *        for the raw message
 * Return: -1 on read error
 *          n on success; n= the number of messages fast forwarded over
 *                        to get to the next valid header
 *          0 on total sucess > 0 with some failures, but can proceed
 *****************************************************************************/
int
MRT_readMessageNoHeader(int socket, MRTheader mrtHeader, uint8_t * rawMessage)
{

	int 		read_len = readn(socket, rawMessage, mrtHeader.length);
	if (read_len != mrtHeader.length) {
		log_err("mrtThread, message reading failed\n");
		return -1;
	}
	return 0;
}

/*
 * Purpose: read in the mrt header
 * Input:  the socket to read from, a pointer the MRT header struct to populate
 * Output: 1 for success
 *         0 for failure --> should result in closing the MRT session
 * Cathie Olschanowsky @ 8/2011
 * first read the MRT common header http://tools.ietf.org/search/draft-ietf-grow-mrt-15#section-2
 * expected format
 *0                   1                   2                   3
 *0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                           Timestamp                           |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|             Type              |            Subtype            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                             Length                            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                      Message... (variable)
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */
int
MRT_parseHeader(int socket, MRTheader * mrtHeader)
{
	int 		n = readn(socket, mrtHeader, sizeof(MRTheader));
	if (n != sizeof(MRTheader)) {
		log_err("mrtThread, read MRT header: EOF may have been reached: attempted to read %u bytes and read %d", sizeof(MRTheader), n);
		return -1;
	}
	mrtHeader->timestamp = ntohl(mrtHeader->timestamp);
	mrtHeader->type = ntohs(mrtHeader->type);
	mrtHeader->subtype = ntohs(mrtHeader->subtype);
	mrtHeader->length = ntohl(mrtHeader->length);

	if (mrtHeader->length > MAX_MRT_LENGTH) {
		log_warning("mrtThread, read MRT header: invalid length %lu > %lu (this may be valid for table dump)\n", mrtHeader->length, MAX_MRT_LENGTH);
	}
	if (mrtHeader->length < MRT_MRT_MSG_MIN_LENGTH) {
		log_err("mrtThread, read MRT header: invalid length %lu < %lu\n", mrtHeader->length, MRT_MRT_MSG_MIN_LENGTH);
		return -1;
	}
	return 0;
}
/*
 * Purpose: write an MRT header to a buffer
 * Input:  the buffer to write to and the mrt header
 * Output: 1 for success
 *         0 for failure --> should result in closing the MRT session
 * Cathie Olschanowsky @ march 2012
 * first read the MRT common header http://tools.ietf.org/search/draft-ietf-grow-mrt-15#section-2
 * expected format
 *0                   1                   2                   3
 *0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                           Timestamp                           |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|             Type              |            Subtype            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                             Length                            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                      Message... (variable)
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 */
int
MRT_writeHeader(uint8_t * dest, MRTheader * mrtHeader)
{

	int 		time_pos = 0;
	int 		type_pos = 4;
	int 		subtype_pos = 6;
	int 		length_pos = 8;

	dest[time_pos] = htonl(mrtHeader->timestamp);
	dest[type_pos] = htons(mrtHeader->type);
	dest[subtype_pos] = htons(mrtHeader->subtype);
	dest[length_pos] = htons(mrtHeader->length);

	mrtHeader->timestamp = ntohl(mrtHeader->timestamp);
	mrtHeader->type = ntohs(mrtHeader->type);
	mrtHeader->subtype = ntohs(mrtHeader->subtype);
	mrtHeader->length = ntohl(mrtHeader->length);

	return 0;
}

/*
 * Purpose: fast forward reading from the socket, the given number of bytes
 * Input:  the socket to read from, the number of bytes to skip
 * Output: 1 for success
 *         0 for failure
 */
int
fastForward(int socket, int length)
{

	int 		n = 0;
	uint8_t        *skip = malloc(length);
	if (skip == NULL) {
		log_err("mrtThread, unable to malloc %u for skipping\n", length);
		return -1;
	} else {
		n = readn(socket, skip, length);
		if (n != length) {
			log_err("mrtThread, unable to read skipped message");
			free(skip);
			return -1;
		}
	}
	free(skip);
	return 0;
}
/*
 * Purpose: fast forward reading from the socket to the next valid BGP header
 * Input:  the socket to read from
 * Output: 1 for success
 *         0 for failure
 * we are searching for 16 255s in a row here.
 * the magic 18 is because 16 bytes + 2 bytes for length = 18 bytes
 * the lenght is inclusive in the BGP header
 */
int
MRT_fastForwardToBGPHeader(int socket)
{

	uint8_t 	nextByte = 0;
	int 		i        , n;

	while (1) {
		n = readn(socket, &nextByte, 1);
		if (n != 1) {
			log_err("mrtThread, unable to read from socket\n");
			return -1;
		}
		if (nextByte == 255) {
			for (i = 0; i < 15; i++) {
				n = readn(socket, &nextByte, 1);
				if (n != 1) {
					log_err("mrtThread, unable to read from socket\n");
					return -1;
				}
				if (nextByte != 255) {
					break;
				}
			}
			if (i == 15) {
				uint16_t 	len;
				uint8_t        *tmpBuf = NULL;
				n = readn(socket, &len, 2);
				if (n != 2) {
					log_err("mrtThread, unable to read from socket\n");
					return -1;
				}
				len = ntohs(len);
				tmpBuf = malloc(len - 18);
				if (tmpBuf == NULL) {
					log_err("mrtThread, malloc error\n");
					return -1;
				}
				n = readn(socket, tmpBuf, len - 18);
				if (n != (len - 18)) {
					log_err("mrtThread, unable to read from socket\n");
					free(tmpBuf);
					return -1;
				}
				log_msg("mrtThread, found next BGP message with len %d", len);
				free(tmpBuf);
				break;
			}
		}
	}
	return 0;
}
