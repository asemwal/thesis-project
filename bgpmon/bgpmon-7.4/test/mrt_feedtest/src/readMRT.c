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
 *  File: readMRT.c
 *      Authors: Dan Massey
 *      read MRT data from a socket,  store the data in a file,
 *      and validate the data pass simple MRT header checks
 *  Date: Nov 7, 2011
 */

#include "defs.h"
#include "unp.h"
#include "readMRT.h"

/*
 * Purpose: check if system define time_t type as u_int32_t or u_int64_t
 * Input: none
 * Output:  return TIME_T_32 if time_t is signed 32 bit long
 *          return TIME_T_64 if time_t is signed 64 bit long
 *          return -1 if failure
 * Mikhail Strizhov @ Nov 10, 2011
 */
int 
checkSystemTimeSize()
{
	/* check if time_t is signed 32 bit long */
	if (sizeof(time_t) == sizeof(int32_t))
		return TIME_T_32;
	/* check if time_t is signed 64 bit long */
	if (sizeof(time_t) == sizeof(int64_t))
		return TIME_T_64;

	/* return failure */
	return -1;
}

/*
 * Purpose: check the MRT header time is in the range 0 to current time
 *          compare timestamp from mrt header and current timestamp
 * Input: MRT header timestamp, current time,  time_t type
 * Output:  return 0 in success
 *           return -1 in failure
 * Mikhail Strizhov @ Nov 10, 2011
 */
int 
calculateDiffTime(u_int32_t hdr_time, time_t curr, int type)
{
	/* check time_t type */
	if (type == -1) {
		fprintf(stderr, "Unable to identify time_t size.\n");
		return -1;
	}
	/* if time_t is 32 bit long */
	if (type == TIME_T_32) {
		if (difftime(ntohl(hdr_time), curr) > 0) {
			fprintf(stderr, "MRT timestamp of %u exceeds current time of %ld\n", ntohl(hdr_time), curr);
			return -1;
		}
		return 0;
	} else
	 /* time_t is 64 bit long */ if (type == TIME_T_64) {
		if (difftime((time_t) ntohl(hdr_time), curr) > 0) {
			fprintf(stderr, "MRT timestamp of %u exceeds current time of %ld\n", ntohl(hdr_time), curr);
			return -1;
		}
		return 0;
	}
	return -1;
}

/*
 * Purpose: check the MRT BGP4MP header length based on MRT subtype
 * Input: MRT BGP4MP header subtype, MRT BGP4MP header length
 * Output:  return 0 in success
 *           return -1 in failure
 * Mikhail Strizhov @ Nov 10, 2011
 */
int 
checkBGP4MPLength(u_int16_t subtype, u_int32_t length)
{
	/* check subtype value */
	switch (ntohs(subtype)) {
		case BGP4MP_STATE_CHANGE:
		if (ntohl(length) > BGP4MP_STATE_CHANGE_SIZE) {	/* defined in defs.h */
			fprintf(stderr, "MRT BGP4MP state change message length of %u exceeds max of %d\n",
				ntohl(length),
				BGP4MP_STATE_CHANGE_SIZE);
			return -1;
		}
		break;
	case BGP4MP_MESSAGE:
	case BGP4MP_MESSAGE_LOCAL:	/* MESSAGE_LOCAL has the same
					 * structure as MESSAGE subtype */
		if (ntohl(length) > (BGP4MP_MESSAGE_SIZE + BGPMSG_SIZE)) {	/* defined in defs.h */
			fprintf(stderr, "MRT BGP4MP update message length of %u exceeds max of %d\n",
				ntohl(length),
				(BGP4MP_MESSAGE_SIZE + BGPMSG_SIZE));
			return -1;
		}
		break;
	case BGP4MP_MESSAGE_AS4:
	case BGP4MP_MESSAGE_AS4_LOCAL:	/* MESSAGE_AS4_LOCAL has the same
					 * structure as MESSAGE_AS4 subtype */
		if (ntohl(length) > (BGP4MP_MESSAGE_AS4_SIZE + BGPMSG_SIZE)) {	/* defined in defs.h */
			fprintf(stderr, "MRT BGP4MP 4-byte AS update message length of %u exceeds max of %d\n",
				ntohl(length),
				(BGP4MP_MESSAGE_AS4_SIZE + BGPMSG_SIZE));
			return -1;
		}
		break;
	case BGP4MP_STATE_CHANGE_AS4:
		if (ntohl(length) > BGP4MP_STATE_CHANGE_AS4_SIZE) {	/* defined in defs.h */
			fprintf(stderr, "MRT BGP4MP 4-byte AS state change message length of %u exceeds max of %d\n",
				ntohl(length),
				BGP4MP_STATE_CHANGE_AS4_SIZE);
			return -1;
		}
		break;
	default:		/* unknown subtype */
		fprintf(stderr, "MRT BGP4MP message include unknown %d subtype!\n", ntohs(subtype));
		return -1;
	}

	/* return success */
	return 0;
}

/*
 * Purpose: validate an MRT header has the expected values
 * Input: MRT header to validate, reference to length
 * Output:  return 0 if the header is valid or -1 if invalid
 * Mikhail Strizhov @ Nov 3, 2011
 */
int 
validateHeader(MrtHdr mrtHdr, size_t * length)
{
	/* check the MRT time is in the range 0 to current time */
	time_t 		curr = time(NULL);
	if (calculateDiffTime(mrtHdr.time, curr, checkSystemTimeSize()) == -1) {
		fprintf(stderr, "MRT header timestamp validation failed\n");
		return -1;
	}
	/* check for MRT BGP4MP type */
	if (ntohs(mrtHdr.type) == BGP4MP) {
		/* check for valid subtype */
		if (ntohs(mrtHdr.subtype) != BGP4MP_STATE_CHANGE &&
		    ntohs(mrtHdr.subtype) != BGP4MP_MESSAGE &&
		    ntohs(mrtHdr.subtype) != BGP4MP_MESSAGE_AS4 &&
		    ntohs(mrtHdr.subtype) != BGP4MP_STATE_CHANGE_AS4 &&
		    ntohs(mrtHdr.subtype) != BGP4MP_MESSAGE_LOCAL &&
		    ntohs(mrtHdr.subtype) != BGP4MP_MESSAGE_AS4_LOCAL) {
			fprintf(stderr, "MRT BGP4MP message  subtype of %d is not supported\n", ntohs(mrtHdr.subtype));
			return -1;
		}
		/* check message length for each valid subtype */
		if (checkBGP4MPLength(mrtHdr.subtype, mrtHdr.length) == -1) {
			fprintf(stderr, "MRT header length validation failed\n");
			return -1;
		}
		/* header is valid, update length */
		*length = ntohl(mrtHdr.length);
		return 0;
	}
	/* check for MRT TABLE_DUMP_V2 type */
	if (ntohs(mrtHdr.type) == TABLE_DUMP_V2) {
		/* check for valid subtypes */
		if (ntohs(mrtHdr.subtype) != PEER_INDEX_TABLE &&
		    ntohs(mrtHdr.subtype) != RIB_IPV4_UNICAST &&
		    ntohs(mrtHdr.subtype) != RIB_IPV4_MULTICAST &&
		    ntohs(mrtHdr.subtype) != RIB_IPV6_UNICAST &&
		    ntohs(mrtHdr.subtype) != RIB_IPV6_MULTICAST &&
		    ntohs(mrtHdr.subtype) != RIB_GENERIC) {
			fprintf(stderr, "MRT TABLE_DUMP_V2 message subtype of %d is not supported\n", ntohs(mrtHdr.subtype));
			return -1;
		}
		/* these MRT messages are created by third party collectors */
		/* their size is not standardized by the  BGP RFCs */
		/* the TABLE_BGPSIZE is an estimate and its defined in defs.h  */
		if (ntohl(mrtHdr.length) > TABLE_BGPSIZE) {
			fprintf(stderr, "MRT TABLE_DUMP_V2 message length of %u exceeds max of %d\n", ntohl(mrtHdr.length), TABLE_BGPSIZE);
			return -1;
		}
		/* header is valid, update length */
		*length = ntohl(mrtHdr.length);
		return 0;
	}
	fprintf(stderr, "MRT message has an unsupported type of %d\n", ntohs(mrtHdr.type));
	return -1;
}

/*
 * Purpose: read bgp message from the socket connection
 * Input: socket descriptor, the resulting bgp message length, the output file
 * Output:  0 for success
 *          -1 for failure
 * Mikhail Strizhov @ Nov 6, 2011
 */
int 
getBGPmessage(int new_fd, size_t length, FILE * mrtData)
{
	char 		data     [MAXDATASIZE];	/* bgp data message */
	/* read BGP message from the socket connection */
	if (readn(new_fd, data, length) != length) {
		fprintf(stderr, "Unable to read BGP message from the connection\n");
		return -1;
	}
	/* check if MRT binary file is opened */
	if (mrtData == NULL) {
		fprintf(stderr, "MRT binary file is not opened\n");
		return -1;
	}
	/* write BGP message to MRT binary file */
	if (fwrite((void *) data, length, 1, mrtData) != 1) {
		fprintf(stderr, "Unable to write BGP message to MRT binary file\n");
		return -1;
	}
	return 0;
}

/*
 * Purpose: fast forward reading from the socket to the next valid BGP header
 *          we are searching for BGP marker assumed to be all 1s.
 *          Function include two while loops: first is designed to find BGP marker
               second, reads BGP message length and the rest of BGP message
 * Input:  the socket to read from, MRT binary file, reference to length
 * Output: 0 for success
 *         -1 for failure
 * Mikhail Strizhov @ Nov 10, 2011
 */
int 
fastForwardToNextValidMessage(int socket, FILE * mrtData, size_t * length)
{
	u_int8_t 	nextByte = 0;
	int 		markercount = 0;
	u_int16_t 	bgplen = 0;

	/* count the number of corrupted bytes  */
	size_t 		counter = 0;

	/* check if MRT binary file is opened */
	if (mrtData == NULL) {
		fprintf(stderr, "MRT binary file is not opened\n");
		return -1;
	}
	/* read data from the socket until we find a BGP marker,  16 bytes of 0xff */
	/* write each byte to the file */
	while (markercount != 16) {
		/* read a byte from socket */
		if (readn(socket, &nextByte, sizeof(nextByte)) != sizeof(nextByte)) {
			fprintf(stderr, "Unable to read corrupted byte from  this connection\n");
			return -1;
		}
		/* write corrupted byte to MRT binary file */
		if (fwrite((void *) &nextByte, sizeof(nextByte), 1, mrtData) != 1) {
			fprintf(stderr, "Unable to write corrupted byte to MRT binary file\n");
			return -1;
		}
		/* increment the byte count */
		counter = counter + sizeof(nextByte);	/* increment the counter
							 * for corrupted bytes */

		/* check if next byte if 0xff */
		if (nextByte == 0xff)
			markercount++;	/* increase marker counter */
		else
			markercount = 0;	/* reset marker counter */
	}

	/* read length and the rest of BGP message from the socket */
	while (1) {
		/* read a byte from socket */
		if (readn(socket, &nextByte, sizeof(nextByte)) != sizeof(nextByte)) {
			fprintf(stderr, "Unable to read corrupted byte from  this connection\n");
			return -1;
		}
		/* write corrupted byte to MRT binary file */
		if (fwrite((void *) &nextByte, sizeof(nextByte), 1, mrtData) != 1) {
			fprintf(stderr, "Unable to write corrupted byte to MRT binary file\n");
			return -1;
		}
		/* increment the byte count */
		counter = counter + sizeof(nextByte);	/* increment the counter
							 * for corrupted bytes */

		/* next byte should not be 0xff */
		/* we expect to have 2 byte BGP length */
		if (nextByte != 0xff) {
			/* shift byte to 16-bit long bgplen */
			bgplen = nextByte << 8;
			/* read second byte of BGP length */
			if (readn(socket, &nextByte, sizeof(nextByte)) != sizeof(nextByte)) {
				fprintf(stderr, "Unable to read corrupted byte from  this connection\n");
				return -1;
			}
			/* add second byte to bgplen */
			bgplen += nextByte;

			/* write second byte of BGP message length MRT binary file */
			if (fwrite((void *) &nextByte, sizeof(nextByte), 1, mrtData) != 1) {
				fprintf(stderr, "Unable to write corrupted byte to MRT binary file\n");
				return -1;
			}
			counter = counter + sizeof(bgplen);	/* increment the counter
								 * for corrupted bytes */

			/* buffer for the rest of corrupted BGP message */
			char 		buf      [bgplen - MRKR_BGPLEN_SIZE];	/* MRKR_LEN_SIZE is size
										 * of marker and BGP
										 * length */
			/* read the rest of bgp message */
			if (readn(socket, buf, sizeof(buf)) != sizeof(buf)) {
				fprintf(stderr, "Unable to read the rest of BGP message from the connection\n");
				return -1;
			}
			/* write the rest of BGP message to MRT binary file */
			if (fwrite((void *) buf, sizeof(buf), 1, mrtData) != 1) {
				fprintf(stderr, "Unable to write corrupted BGP message to MRT binary file\n");
				return -1;
			}
			counter = counter + sizeof(buf);

			/* leave while loop */
			break;
		}
	}

	/* assign the number of founded corrupted bytes */
	*length = counter;

	/* return success */
	return 0;
}

/*
 * Purpose: write the MRT header to the output file
 * Input: the MRT header, the bytecounter, whether the header is valid,
 *        and the output file
 * Output:  return 0 if header written,  -1 on error
 * Dan Massey @ Nov 7, 2011
 */
int 
writeMRTheader(MrtHdr mrtHdr, size_t bytecounter, char *valid_str, FILE * mrtSummary)
{
	/* check if MRT summary file is opened */
	if (mrtSummary == NULL) {
		fprintf(stderr, "MRT summary file is not open!\n");
		return -1;
	}
	/* print MRT header summary to MRT summary file    */
	fprintf(mrtSummary, "%ld|%d|%d|%u|%u|%s\n", bytecounter,
		ntohs(mrtHdr.type),
		ntohs(mrtHdr.subtype),
		ntohl(mrtHdr.length),
		ntohl(mrtHdr.time),
		valid_str);
	return 0;
}

/*
 * Purpose: read MRT data from a socket,  store the data in a file,
 *          and validate the data pass simple MRT header checks
 * Input: socket providing MRT data,  a file to write the MRT data,
 *        and a file for writing summary information about headers
 * Output:  return 0 if all data read and the sender closed the socket
 *          -1 on an error
 * Mikhail Strizhov @ Nov 3, 2011
 */
int 
readMRTdata(int new_fd, FILE * mrtData, FILE * mrtSummary)
{
	MrtHdr 		mrtHdr;	/* MRT header structure */
	size_t 		length = 0;	/* bgp message length */
	size_t 		bytecounter = 0;	/* byte number counter */

	while (1) {
		/* read the MRT header */
		if (readn(new_fd, &mrtHdr, sizeof(MrtHdr)) != sizeof(MrtHdr)) {
			fprintf(stderr, "Unable to read MRT header form this connection\n");
			return -1;
		}
		/* write header to a MRT binary file */
		if (fwrite((void *) &mrtHdr, sizeof(mrtHdr), 1, mrtData) != 1) {
			fprintf(stderr, "Unable to write MRT header to MRT binary file\n");
			return -1;
		}
		/* validate MRT header */
		if (validateHeader(mrtHdr, &length) == -1) {
			/* write corrupted MRT header to a MRT summary file	 */
			if (writeMRTheader(mrtHdr, bytecounter, INVALID, mrtSummary) == -1) {
				fprintf(stderr, "Unable to write corrupted MRT header to MRT summary file\n");
				return -1;
			}
			/* MRT header is corrupted, write all corrupted data to a MRT binary file  */
			/* until we find a valid MRT header */
			if (fastForwardToNextValidMessage(new_fd, mrtData, &length) == -1) {
				fprintf(stderr, "Unable to find the next valid message following an invalid header.\n");
				return -1;
			}
		} else {
			/* write MRT header to a MRT summary file	 */
			if (writeMRTheader(mrtHdr, bytecounter, VALID, mrtSummary) == -1) {
				fprintf(stderr, "Unable to write MRT header to MRT summary file\n");
				return -1;
			}
			/* MRT header is valid. write the BGP message  */
			if (getBGPmessage(new_fd, length, mrtData) == -1) {
				fprintf(stderr, "Unable to read and write BGP message from the connection\n");
				return -1;
			}
		}

		/* increase bytecounter */
		bytecounter = bytecounter + sizeof(MrtHdr) + length;
	}
}
