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
 *  File: mrtinstance.c
 * 	Authors: He Yan, Dan Massey, Mikhail, Cathie Olschanowsky
 *
 *  Date: Oct 7, 2008
 */

#include "mrtProcessTable.h"

/* required for logging functions */
#include "../Util/log.h"
#include "../Util/utils.h"

/* needed for address management  */
#include "../Util/address.h"

/* needed for writen function  */
#include "../Util/unp.h"
#include "../Util/bgp.h"

/* needed for function getXMLMessageLen */
#include "../XML/xml.h"

/* needed for session related function */
#include "../Peering/peersession.h"

/* needed for Mrt Table Dump v2 and state of connection */
#include "../Util/bgppacket.h"
#include "../Peering/bgpmessagetypes.h"

/* needed for deleteRib table if socket connection lost */
#include "../Labeling/label.h"

/* needed for session State */
#include "../Peering/bgpstates.h"
#include "../Peering/bgpevents.h"


/* needed for malloc and free */
#include <stdlib.h>
/* needed for strncpy */
#include <string.h>
/* needed for system error codes */
#include <errno.h>
/* needed for addrinfo struct */
#include <netdb.h>
/* needed for system types such as time_t */
#include <sys/types.h>
/* needed for time function */
#include <time.h>
/* needed for socket operations */
#include <sys/socket.h>
/* needed for pthread related functions */
#include <pthread.h>

#include <stdio.h>
#include <arpa/inet.h>
#include <inttypes.h>
#include <netinet/in.h>

/*#define DEBUG */


/*
 * Purpose: check how many null and non null tables we have
 * Input:  tablebuffer pointer,  number of peers in table
 * Output:  0 failure, 1 success (signal to exit while loop)
 * Mikhail Strizhov @ Oct 6, 2010
 */
int 
checkBGPTableEmpty(TableBuffer * tablebuffer, int NumberPeers)
{
	int 		retval = 0;
	int 		i = 0;
	int 		nulltable = 0;
	int 		nonnulltable = 0;
	for (i = 0; i < NumberPeers; i++) {
		if (tablebuffer[i].start == NULL) {
			nulltable++;
		} else {
			nonnulltable++;
		}
	}

	log_msg("%s, BGP Table still maintains %d peer tables", __FUNCTION__, nonnulltable);
	/* check if numberof nulltables is eq to NumberPeers and nonnull is 0 */
	if ((nulltable == NumberPeers) && (nonnulltable == 0)) {
		retval = 1;
	}
	return retval;
}

/*
 * Purpose: insert bmf messages into buffer
 * Input:  peers pointer to linked structure, tail of structure(makes addition faster), BMF message
 * Output: return linked list for every node, also updates tail by address
 * Mikhail Strizhov @ Oct 5, 2010
 */
int 
insertBGPTable(TableBuffer * tbl, BGPMessage * bgp)
{
	if (tbl == NULL) {
		log_err("Unable to add to non-existant table\n");
		return -1;
	}
	tbl->table_exist = 1;

	if (tbl->start == NULL) {
		tbl->start = calloc(1, sizeof(struct BGPTableStruct));
		if (tbl->start == NULL) {
			log_err("Malloc Error\n");
			return -1;
		}
		tbl->msg_count = 1;
		tbl->tail = tbl->start;
	} else {
		/* get tail */
		tbl->tail->next = calloc(1, sizeof(struct BGPTableStruct));
		if (tbl->tail->next == NULL) {
			log_err("Malloc Error\n");
			return -1;
		}
		/* update tail */
		tbl->tail = tbl->tail->next;
	}

	tbl->msg_count += 1;
	tbl->tail->BGPmessage = bgp;
	tbl->tail->next = NULL;
	return 0;

}

/*
 * Purpose: write bmf messages to peer queue
 * Input: SessionID, linked list, Queue writer, convert flag (1 or 0)
 * Output: none
 * Mikhail Strizhov @ Oct 6, 2010
 */
void
writeBGPTableToQueue(int ID, struct BGPTableStruct ** start, QueueWriter writerpointer, int asLen)
{

	char 		bgpSerialized[BGP_MAX_MSG_LEN];
	/* check if its already free */
	if (*start == NULL)
		return;

	struct BGPTableStruct *ptr = NULL;

	/* this is a temporary hack while we rework the queue system */
	/* I am breaking the messages into chunks -- filling the queue 1/2 of the way */
	/* for each group... and then sleeping for up to 1 seconds.  */
	int 		chunkSize = QUEUE_MAX_ITEMS / 4;
	uint32_t 	messageCount = 0;
	for (ptr = *start; ptr != NULL; ptr = ptr->next) {
		BMF 		m = createBMF(ID, BMF_TYPE_TABLE_TRANSFER, bgpSerialized, ptr->BGPmessage->length);
		int 		res = BGP_serialize((uint8_t *) bgpSerialized, ptr->BGPmessage, asLen);
		if (res) {
			log_err("%s: Unable to serialize BGP message", __FUNCTION__);
			return;
		}
		/* bgpmonMessageAppend(m,bgpSerialized,ptr->BGPmessage->length); */
		writeQueue(writerpointer, m);
		incrementSessionMsgCount(ID);
		messageCount++;
		if (messageCount % chunkSize == 0) {
			sleep(0);
		}
	}
	log_msg("%s: Table dump required %u messages", __FUNCTION__, messageCount);
	return;
}

/*
 * Purpose: free linked list of BGP messages
 * Input:  peers pointer to linked structure
 * Output: none
 * Mikhail Strizhov @ Oct 5, 2010
 */
void 
freeBGPTable(TableBuffer * tbl)
{
	struct BGPTableStruct *ptr1, *ptr2;

	ptr1 = tbl->start;
	while (ptr1 != NULL) {
		ptr2 = ptr1->next;
		BGP_freeMessage(ptr1->BGPmessage);
		free(ptr1);
		ptr1 = ptr2;
	}
	tbl->start = tbl->tail = NULL;
}

/*
 * Purpose: this code processes MRT messages of type 13   TABLE_DUMP_V2
 * Input:  the socket to read from, the mrtheader object that put us here,
 * Output: 1 for success
 *         0 for failure
 * We are making the assumption that messages of type 13 will not be found in
 * the same conversation as other types. Once we step into this subroutine
 * we will only process type 13s until disconnect.
 * TODO: this function needs more refactoring --> it is too long The Jira Issue is
 * BGPMON-29
 */
int
MRT_processType13(MrtNode * cn, uint8_t * rawMessage, int *rawMessage_length, MRTheader * mrtHeader)
{

	mrt_index 	indexPtr;
	short 		eof = 0;
	TableBuffer    *tablebuffer;
	BGPMessage    **bgp_arr;
	int            *peer_idxs;
	int 		bgp_count = 0;
	int 		i;

	if (mrtHeader->subtype != 1) {
		log_err("mrtThread, TABLE_DUMP_V2 initiated with subtype %d rather than 1\n", mrtHeader->subtype);
		return -1;
	}
	/* the first message is used to create a temporary table of sessions. */
	/* if this fails we should drop the connection -- return -1 */
	if (MRT_createTableBufferFromType13Subtype1(cn, &indexPtr, &tablebuffer, rawMessage, *rawMessage_length, mrtHeader)) {
		log_err("mrtThread, TABLE_DUMP_V2 the first message was not processed\n");
		return -1;
	}
	/* create the space to be used for processing the messages */
	bgp_arr = calloc(indexPtr.PeerCount, sizeof(BGPMessage *));
	peer_idxs = calloc(indexPtr.PeerCount, sizeof(int));

	/* The Message 13 subtype 1 message is complete and now we recieve other messages */
	/* at this point we are in a conversation with the MRT collector and are  */
	/* expecting a series of messages of type 13 --> no other type */
	/* should be seen and we should not see any more of subtype 1. */
#ifdef DEBUG
	int 		debug_count = 0;
#endif
	uint32_t 	msg_count = 0;
	while (cn->deleteMrt == FALSE && !eof) {
#ifdef DEBUG
		debug_count++;
#endif
		/* update the last action time */
		cn->lastAction = time(NULL);

		if (MRT_parseHeader(cn->socket, mrtHeader)) {
			eof = 1;
			continue;
		}
		if (mrtHeader->length > *rawMessage_length) {
			free(rawMessage);
			rawMessage = calloc(mrtHeader->length, sizeof(uint8_t));
			*rawMessage_length = mrtHeader->length;
		}
		if (rawMessage == NULL) {
			log_err("%s, Malloc failure, unable to allocate message buffer", __FUNCTION__);
			return -1;
		}
		if (MRT_readMessageNoHeader(cn->socket, *mrtHeader, rawMessage)) {
			eof = 1;
			continue;
		}
		/* Only one type of message should be coming through on this port */
		if (mrtHeader->type != TABLE_DUMP_V2) {
			log_err("mrtThread, an MRT message of type %d was recieved by the thread handling only 13 (TABLE) messages\n", mrtHeader->type);
			free(tablebuffer);
			return -1;
		}
		switch (mrtHeader->subtype) {
		case PEER_INDEX_TABLE:
			log_err("mrtThread, only one type 13 subtype 1 message is expected by this thread\n");
			free(tablebuffer);
			return -1;
		case RIB_IPV4_MULTICAST:
		case RIB_IPV6_MULTICAST:
			log_warning("mrtThread, unsupported table dump subtype RIB_IPV(4|6)_MULTICAST\n");
			break;
		case RIB_IPV4_UNICAST:
		case RIB_IPV6_UNICAST:
			if (MRT_processType13SubtypeSpecific(tablebuffer, mrtHeader, rawMessage, bgp_arr, peer_idxs, &bgp_count, indexPtr.PeerCount)) {
				eof = 1;
			}
			msg_count += bgp_count;
			break;
		case RIB_GENERIC:
			if (MRT_processType13SubtypeGeneric(mrtHeader, rawMessage, bgp_arr, peer_idxs, &bgp_count)) {
				eof = 1;
			}
			break;
		default:
			log_err("mrtThread, Invalid subtype for type 13 MRT message\n", mrtHeader->subtype);
			free(tablebuffer);
			return -1;
		}

	}			/* end while */
	log_msg("%s: A total of %u messages created", __FUNCTION__, msg_count);

	free(bgp_arr);
	free(peer_idxs);
	/*
	 * the loop has ended --> this means that the MRT session is being closed through a
	 * shutdown or through an eof.
	 */
	close(cn->socket);
	log_msg("MRT table dump thread: preparing to exit");

	int 		tableloopflag = 0;
	/* 6 * 30 = 3 minutes to wait for update message. If no update message - erase all. */
	/*
	 * there is no need to do this if we are shutting down bgpmon.... in that case just proceed
	 * to cleanup
	 */
	while (tableloopflag < 6 && cn->deleteMrt == FALSE) {

		cn->lastAction = time(NULL);
		/*
		 * check if all pointers are null. if yes, than all tables are sent, thus exit
		 * thread
		 */
		if (checkBGPTableEmpty(tablebuffer, indexPtr.PeerCount) == 1) {
			log_msg("mrtThread, Table Transfer is empty, exit the MRT thread");
			break;
		}
		/* update the last action time */
		/* go through the peer list */
		int 		i;
		for (i = 0; i < indexPtr.PeerCount && cn->deleteMrt == FALSE; i++) {
			/*
			 * check the state of ID:  if update message came, it will be changed to
			 * stateMrtEstablished
			 */
			if (getSessionState(tablebuffer[i].ID) == stateMrtEstablished) {
				log_msg("%s: found active session associated to table dump (session:%d)", __FUNCTION__, tablebuffer[i].ID);
				/* check if session  ASN has changed to 2 byte */
				if ((tablebuffer[i].table_exist == 1) && (tablebuffer[i].start != NULL)) {
					cn->lastAction = time(NULL);
					log_msg("mrtThread, Session %d change ASN to %d, send entire table to MRTQueue",
						tablebuffer[i].ID, getSessionASNumberLength(tablebuffer[i].ID));
					/* write all messages for this peer */
					log_msg("%s: this table has %u messages", __FUNCTION__, tablebuffer[i].msg_count);
					writeBGPTableToQueue(tablebuffer[i].ID, &(tablebuffer[i].start), cn->qWriter, getSessionASNumberLength(tablebuffer[i].ID));
					/* free linked list */
					log_msg("mrtThread, Table for Session %d sent", tablebuffer[i].ID);
					freeBGPTable(&tablebuffer[i]);
					tablebuffer[i].start = NULL;
					tablebuffer[i].tail = NULL;
				} else if (tablebuffer[i].table_exist == 0) {
					/*
					 * case when received table for a peer is null
					 * (tablebuffer[i].start == NULL)
					 */
					/* and table_exist flag was not set to 1 */
					/* delete entire table from our RIB-IN */
					cn->lastAction = time(NULL);
					log_msg("No BGP messages received from MRT TABLE_DUMP_V2, I will delete RIB-IN table for Session %d", tablebuffer[i].ID);
					/* change state to stateError */
					setSessionState(getSessionByID(tablebuffer[i].ID), stateError, eventManualStop);
					/* delete prefix table and attributes */
					if (cleanRibTable(tablebuffer[i].ID) < 0) {
						log_warning("Could not clear table for Session ID %d", tablebuffer[i].ID);
					}
					/* skip deletion next loop */
					tablebuffer[i].table_exist = 1;
					/* free nothing */
					freeBGPTable(&tablebuffer[i]);
					tablebuffer[i].start = NULL;
					tablebuffer[i].tail = NULL;
				}
			}
		}
		tableloopflag++;
		/* sleep */
		sleep(TABLE_TRANSFER_SLEEP);
	}

	log_msg("MRT table dump thread(%d) freeing memory.", cn->id);
	cn->lastAction = time(NULL);
	/* free peer table index */
	for (i = 0; i < indexPtr.PeerCount; i++) {
		/* free linked list */
		freeBGPTable(&tablebuffer[i]);
		tablebuffer[i].start = NULL;
		tablebuffer[i].tail = NULL;
	}
	indexPtr.PeerCount = 0;
	free(tablebuffer);
	log_msg("MRT table dump thread(%d) exiting.", cn->id);
	return 1;
}

/******************************************************************************
 * Name: MRT_createTableBufferFromType13Subtype1
 * Input: MrtNode, mrtindex, tablebuffer (to be allocated), rawMessage mrtHeader
 * Outout: 0 on sucess, -1 on failure
 * Description:
 * This function reads the first message in a rib table conversation
 * and creates the infrastructure for saving all of the other data to be
 * receieved.
******************************************************************************/
int
MRT_createTableBufferFromType13Subtype1(MrtNode * cn, mrt_index * indexPtr, TableBuffer ** tablebuffer,
   const uint8_t * rawMessage, int rawMessage_length, MRTheader * mrtHeader)
{

	int 		idx = 0;
	char 		SrcIPString[ADDR_MAX_CHARS];
	/*
	 * This is an MRT message type 13 subtype 1 It is a PEER_INDEX_TABLE now we start reading
	 * the header http://tools.ietf.org/search/draft-ietf-grow-mrt-17#section-4 0
	 * 1                   2                   3 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2
	 * 3 4 5 6 7 8 9 0 1 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
	 * Collector BGP ID                         |
	 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |       View Name
	 * Length        |     View Name (variable)      |
	 * +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |          Peer Count
	 * |    Peer Entries (variable) +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
	 * 
	 * Figure 5: PEER_INDEX_TABLE Subtype
	 */

	/* collector BGP ID */
	memmove(&indexPtr->BGPSrcID, &rawMessage[idx], sizeof(indexPtr->BGPSrcID));
	idx += sizeof(indexPtr->BGPSrcID);
	if (inet_ntop(AF_INET, &indexPtr->BGPSrcID, SrcIPString, ADDR_MAX_CHARS) == NULL) {
		log_err("mrtThread, TABLE DUMP v2 message: indexPtr->BGPSrcID ipv4 convert error!");
		return -1;
	}
	if (idx >= rawMessage_length) {
		log_err("%s, reading over the end of the raw Message: Parsing error detected after BGPSrcID", __FUNCTION__);
		return -1;
	}
	/* View Name Length */
	READ_2BYTES(indexPtr->ViewNameLen, rawMessage[idx]);
	idx += 2;
	if (indexPtr->ViewNameLen != 0) {
		/* this assumes that the view name lenght is expresses in bytes */
		idx += indexPtr->ViewNameLen;
	}
	if (idx >= rawMessage_length) {
		log_err("%s, reading over the end of the raw Message: Parsing error detected after ViewNameLen", __FUNCTION__);
		return -1;
	}
	/* Peer Count */
	READ_2BYTES(indexPtr->PeerCount, rawMessage[idx]);
	idx += 2;
	if (idx >= rawMessage_length) {
		log_err("%s, reading over the end of the raw Message: Parsing error detected after PeerCount", __FUNCTION__);
		return -1;
	}
	/* allocate array of linked structure for each peer */
	(*tablebuffer) = calloc(indexPtr->PeerCount, sizeof(TableBuffer));
	if (*tablebuffer == NULL) {
		log_err("Calloc failed");
		return -1;
	}
	/* Now that the header has been read -- handle each entry */
	/* 0                   1                   2                   3 */
	/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |   Peer Type   | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                         Peer BGP ID                           | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                   Peer IP address (variable)                  | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                        Peer AS (variable)                     | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* */
	/* Figure 6: Peer Entries */
	int 		i;
	for (i = 0; i < (indexPtr->PeerCount); i++) {
		/* Peer Type */
		/* the peer type will tell us we we have ipv4 or ipv6 IP addresses */
		/* The Peer Type field is a bit field which encodes the type of the AS */
		/* and IP address as identified by the A and I bits, respectively, */
		/* below. */
		/* */
		/* 0 1 2 3 4 5 6 7 */
		/* +-+-+-+-+-+-+-+-+ */
		/* | | | | | | |A|I| */
		/* +-+-+-+-+-+-+-+-+ */
		/* */
		/* Bit 6: Peer AS number size:  0 = 16 bits, 1 = 32 bits */
		/* Bit 7: Peer IP Address family:  0 = IPv4,  1 = IPv6 */
		/* */
		/* Figure 7: Peer Type Field */
		indexPtr->PeerType = rawMessage[idx];
		idx++;
		if (idx >= rawMessage_length) {
			log_err("%s, reading over the end of the raw Message: Parsing error detected after PeerType", __FUNCTION__);
			return -1;
		}
		/* Peer BGP ID  */
		memmove(&indexPtr->PeerBGPID, &rawMessage[idx], sizeof(indexPtr->PeerBGPID));
		idx += 4;
		if (idx >= rawMessage_length) {
			log_err("%s, reading over the end of the raw Message: Parsing error detected after PeerBGPID", __FUNCTION__);
			return -1;
		}
		/* Peer IP address: the size depends on if it is IPV4 or 6 (see note above) */
		if ((indexPtr->PeerType & 0x01) == 0) {
			memmove(&indexPtr->PeerIP, &rawMessage[idx], 4);
			idx += 4;
			if (idx >= rawMessage_length) {
				log_err("%s, reading over the end of the raw Message: Parsing error detected after PeerIP", __FUNCTION__);
				return -1;
			}
			if (inet_ntop(AF_INET, &indexPtr->PeerIP, indexPtr->PeerIPStr, ADDR_MAX_CHARS) == NULL) {
				perror("INET_NTOP ERROR:");
				log_err("mrtThread, TABLE DUMP v2 message: ipv4 source address convert error!");
				free(*tablebuffer);
				*tablebuffer = NULL;
				return -1;
			}
		} else {	/* indexPtr.PeerType & 0x01) == 1 */
			memmove(&indexPtr->PeerIP, &rawMessage[idx], 16);
			idx += 16;
			if (idx >= rawMessage_length) {
				log_err("%s, reading over the end of the raw Message: Parsing error detected after PeerIP(IPV6)", __FUNCTION__);
				return -1;
			}
			if (inet_ntop(AF_INET6, &indexPtr->PeerIP, indexPtr->PeerIPStr, ADDR_MAX_CHARS) == NULL) {
				perror("INET_NTOP ERROR:");
				log_err("mrtThread, TABLE DUMP v2 message: ipv6 source address convert error!");
				free(*tablebuffer);
				tablebuffer = NULL;
				return -1;
			}
		}

		/* check 2nd bit - ASN2 or ASN4 */
		int 		ASNumLen = 4;
		if ((indexPtr->PeerType & 0x02) == 0) {
			/* set AS Num Len to 2 byte */
			ASNumLen = 2;
		}
		/* PeerAS */
		memmove(&indexPtr->PeerAS, &rawMessage[idx], ASNumLen);
		idx += ASNumLen;
		if (idx >= rawMessage_length) {
			log_err("%s, reading over the end of the raw Message: Parsing error detected after ASNumLen", __FUNCTION__);
			return -1;
		}
		if (ASNumLen == 2) {
			indexPtr->PeerAS = ntohs(indexPtr->PeerAS);
		} else {
			indexPtr->PeerAS = ntohl(indexPtr->PeerAS);
		}

		/* at this point the index table entry has been read.  */
		/* the next step is to look up the associated session. */
		/* in the case that a session does not exist, a temporary session is created. */
		/*
		 * A temporary session is required, until we recieve an update message with the
		 * associated
		 */
		/* session that indicates if we should be using 2 byte or 4 byte ASNs in the table. */
		/*
		 * the MRT collector promotes ASNs to 4 bytes and so at this point we cannot know
		 * which to use.
		 */
		int 		sessionID = findOrCreateMRTSessionStruct(indexPtr->PeerAS, indexPtr->PeerIPStr, cn->addr,
		   cn->labelAction, UNKASNLEN, stateError, eventManualStop);
		if (sessionID < 0) {
			log_err("mrtThread (13), fail to create a new session for, peer AS %u, peer IP %s, collector IP %s",
			   indexPtr->PeerAS, indexPtr->PeerIPStr, cn->addr);
			free(*tablebuffer);
			*tablebuffer = NULL;
			return -1;
		} else {
			(*tablebuffer)[i].ID = sessionID;
#ifdef DEBUG
			log_msg("mrtThread (13), found or created session for peer AS %u, peer IP %s, collector IP %s",
			   indexPtr->PeerAS, indexPtr->PeerIPStr, cn->addr);
#endif
		}
	}			/* end of Peer Entries Loop */

	log_msg("%s:successful completion of 1st message\n", __FUNCTION__);
	return 0;
}

/*
 * Purpose: Process the Generic subtype from ribs
 * Input: NOT YET IMPLEMENTED
 * Output: NOT YET IMPLEMENTED
 * Info:
 * 4.3.3. RIB_GENERIC Subtype


   The RIB_GENERIC header is shown below.  It is used to cover RIB
   entries which do not fall under the common case entries defined
   above.  It consists of an AFI, Subsequent AFI (SAFI) and a single
   NLRI entry.  The NLRI information is specific to the AFI and SAFI
   values.  An implementation which does not recognize particular AFI
   and SAFI values SHOULD discard the remainder of the MRT record.

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         Sequence number                       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |    Address Family Identifier  |Subsequent AFI |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |     Network Layer Reachability Information (variable)         |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |         Entry Count           |  RIB Entries (variable)
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

                    Figure 9: RIB_GENERIC Entry Header
*/
int
MRT_processType13SubtypeGeneric(MRTheader * mrtHeader, const uint8_t * rawMessage, BGPMessage ** bgp_arr, int *peer_idxs, int *bgp_count)
{
	log_warning("mrtThread, generic table table dump message ignored\n");
	return 0;
}

/*
 * Purpose: this code processes MRT messages of type 13 subtype (2-5)
 * Input:  pointer to table buffer, ptr to mrt header, raw mesage, a pointer to an
           array of messages, an array for peer indexes, an array for counts and
           the max count expected
 * Output: 0 for success
 *         -1 for failure, this may be a read error or a format error
 *           therefore, it should not cause the read loop to exit
 *
 * Description: The main job of this function is to take the rawMessage, which is
 * in MRT format, change it to BGP format, and then wrap it with a BMF header.
 * There will be one bmf message for each rib entry in the MRT message
 */
int
MRT_processType13SubtypeSpecific(TableBuffer * tablebuffer, MRTheader * mrtHeader, const uint8_t * rawMessage, BGPMessage ** bgp_arr,
			   int *peer_indexes, int *bgp_count, int max_count)
{

	int 		idx = 0;/* this variable keeps track of our progress
				 * walking through rawMessage */
	uint16_t 	afi;
	uint8_t 	safi;

	/* max prefix length in bytes (IPV6 = 16, IPV4 = 4) */
	/* we can get this from the subtype */
	int 		max_prefix_len = 0;
	switch (mrtHeader->subtype) {
	case RIB_IPV4_UNICAST:
		max_prefix_len = 4;
		afi = 1;
		safi = 1;
		break;
	case RIB_IPV4_MULTICAST:
		max_prefix_len = 4;
		afi = 1;
		safi = 2;
		break;
	case RIB_IPV6_UNICAST:
		max_prefix_len = 16;
		afi = 2;
		safi = 1;
		break;
	case RIB_IPV6_MULTICAST:
		max_prefix_len = 16;
		afi = 2;
		safi = 2;
		break;
	default:
		log_err("mrtThread, invalid subtype\n");
		return -1;
	}

	/* space to save the message data */
	mrt_uni 	uni;

	/* 4.3.2. AFI/SAFI specific RIB Subtypes */
	/* */
	/* */
	/* The AFI/SAFI specific RIB Subtypes consist of the RIB_IPV4_UNICAST, */
	/* RIB_IPV4_MULTICAST, RIB_IPV6_UNICAST, and RIB_IPV6_MULTICAST */
	/* Subtypes.  These specific RIB table entries are given their own MRT */
	/* TABLE_DUMP_V2 subtypes as they are the most common type of RIB table */
	/* instances and providing specific MRT subtypes for them permits more */
	/* compact encodings.  These subtypes permit a single MRT record to */
	/* encode multiple RIB table entries for a single prefix.  The Prefix */
	/* Length and Prefix fields are encoded in the same manner as the BGP */
	/* NLRI encoding for IPV4 and IPV6 prefixes.  Namely, the Prefix field */
	/* contains address prefixes followed by enough trailing bits to make */
	/* the end of the field fall on an octet boundary.  The value of */
	/* trailing bits is irrelevant. */
	/* */
	/* 0                   1                   2                   3 */
	/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                         Sequence number                       | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* | Prefix Length | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                        Prefix (variable)                      | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |         Entry Count           |  RIB Entries (variable) */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* */
	/* Figure 8: RIB Entry Header */

	/* Sequence number */
	READ_4BYTES(uni.SeqNumb, rawMessage[idx]);
	idx += 4;

	/* Prefix Length */
	uni.PrefixLen = rawMessage[idx];
	idx += 1;

	/* validate the prefix length */
	if (uni.PrefixLen > max_prefix_len * 8) {
		log_err("mrtThread, the prefix length is not valid for this type \n");
		return 0;
	}
	/* Prefix */
	int 		i;
	for (i = 0; i < uni.PrefixLen / 8; i++) {
		uni.Prefix[i] = rawMessage[idx];
		idx++;
	}
	if (uni.PrefixLen % 8) {
		uni.Prefix[i] = rawMessage[idx];
		idx++;
	}
	/* Entry Count */
	READ_2BYTES(uni.EntryCount, rawMessage[idx]);
	idx += 2;

	if (uni.EntryCount > max_count) {
		log_err("The mrt table dump message contains more entries than the number of peers\n");
		return -1;
	}
	/* each entry will result in a bgp message being added to the array */
	(*bgp_count) = 0;

	/* RIB Entries */
	/* 4.3.4. RIB Entries */
	/* */
	/* */
	/* The RIB Entries are repeated Entry Count times.  These entries share */
	/* a common format as shown below.  They include a Peer Index from the */
	/* PEER_INDEX_TABLE MRT record, an originated time for the RIB Entry, */
	/* and the BGP path attribute length and attributes.  All AS numbers in */
	/* the AS_PATH attribute MUST be encoded as 4-Byte AS numbers. */
	/* */
	/* 0                   1                   2                   3 */
	/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |         Peer Index            | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                         Originated Time                       | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |      Attribute Length         | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                    BGP Attributes... (variable) */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* */
	/* Figure 10: RIB Entries */
	/* */
	/* There is one exception to the encoding of BGP attributes for the BGP */
	/* MP_REACH_NLRI attribute (BGP Type Code 14) RFC 4760 [RFC4760].  Since */
	/* the AFI, SAFI, and NLRI information is already encoded in the */
	/* MULTIPROTOCOL header, only the Next Hop Address Length and Next Hop */
	/* Address fields are included.  The Reserved field is omitted.  The */
	/* attribute length is also adjusted to reflect only the length of the */
	/* Next Hop Address Length and Next Hop Address fields. */
#ifdef DEBUG
	log_msg("MRT type specific message: %d entry count\n", uni.EntryCount);
#endif
	int 		j;
	for (j = 0; j < uni.EntryCount; j++) {
		/* each of these will result in an BGP message being created */
		/* each of them will be an update message */
		BGPMessage     *bgpMessage = BGP_createMessage(BGP_UPDATE);

		/* Peer Index */
		READ_2BYTES(uni.PeerIndex, rawMessage[idx]);
		idx += 2;

		/* Originating Time  */
		READ_4BYTES(uni.OrigTime, rawMessage[idx]);
		idx += 4;

		/* Attribute Length	 */
		READ_2BYTES(uni.AttrLen, rawMessage[idx]);
		idx += 2;
		int 		attr_start_pos = idx;	/* keep track of where
							 * the attributes start */
		/* so we know when they are finished */

		/* BGP Attributes */
		/* 0                   1 */
		/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 */
		/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
		/* |  Attr. Flags  |Attr. Type Code| */
		/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */

		while (idx - attr_start_pos < uni.AttrLen) {
			/*
			 * type is handled special because it is actually a 2 octet data type and
			 * not
			 */
			/* a value to be combined using ntohs. */
			uint8_t 	flags = rawMessage[idx];
			uint8_t 	code = rawMessage[idx + 1];
			idx += 2;

			/* If the Extended Length bit of the Attribute Flags octet is set */
			/* to 0, the third octet of the Path Attribute contains the length */
			/* of the attribute data in octets. */
			/* */
			/* If the Extended Length bit of the Attribute Flags octet is set */
			/* to 1, the third and fourth octets of the path attribute contain */
			/* the length of the attribute data in octets. */
			int 		len = BGP_PAL_LEN(flags);
			uint16_t 	length;
			if (len == 1) {
				length = rawMessage[idx];
				idx++;
			} else {
				READ_2BYTES(length, rawMessage[idx]);
				idx += 2;
			}

			/* this is a special case ==> MP_REACH_NLRI */
			/* for this one we need to do some editing to the attributes */
			/* There is one exception to the encoding of BGP attributes for the BGP */
			/* MP_REACH_NLRI attribute (BGP Type Code 14) RFC 4760 [RFC4760].  Since */
			/* the AFI, SAFI, and NLRI information is already encoded in the */
			/* MULTIPROTOCOL header, only the Next Hop Address Length and Next Hop */
			/* Address fields are included.  The Reserved field is omitted.  The */
			/* attribute length is also adjusted to reflect only the length of the */
			/* Next Hop Address Length and Next Hop Address fields. */

			/* TODO: remove the 14 and put in #define */
			if (code == 14) {
#ifdef DEBUG
				log_msg("MRT TD Processing code type 14\n");
#endif
				/* this is what we want */
				/* +/ */
				/* | Address Family Identifier (2 octets)                    | */
				/* +/ */
				/* | Subsequent Address Family Identifier (1 octet)          | */
				/* +/ */
				/* | Length of Next Hop Network Address (1 octet)            | */
				/* +/ */
				/* | Network Address of Next Hop (variable)                  | */
				/* +/ */
				/* | Reserved (1 octet)                                      | */
				/* +/ */
				/* | Network Layer Reachability Information (variable)       | */
				/* +/ */

				/* this is what we have */
				/* +/ */
				/* | Length of Next Hop Network Address (1 octet)            | */
				/* +/ */
				/* | Network Address of Next Hop (variable)                  | */
				/* +/ */

				/* TODO: magic number removal */
				uint8_t 	newAtt [135];
				int 		i = 0;
				/* AFI and SAFI are determined by the type and subtype */
				/* look at the switch statement above to see them set */
				BGP_ASSIGN_2BYTES(&newAtt[i], afi);
				i += 2;
				newAtt[i] = safi;
				i += 1;

				/* Length of next hop and next hop */
				int 		j;
				for (j = 0; j < length; j++) {
					newAtt[i + j] = rawMessage[idx + j];
				}
				i += j;
				idx += j;

				/* Reserved */
				i += 1;

				/* NLRI -- there is only one here */
				newAtt[i] = uni.PrefixLen;
				i += 1;
				for (j = 0; j < uni.PrefixLen / 8; j++) {
					newAtt[i] = uni.Prefix[j];
					i += 1;
				}
				if (uni.PrefixLen % 8) {
					newAtt[i] = uni.Prefix[j];
					i += 1;
				}
				/* idx += length; */
				/* this is where the path attribute is added to the object  */
				if (uni.AttrLen != (idx - attr_start_pos)) {
					log_err("%s: Within special type attr length and current position don't match\n");
				}
				BGP_addPathAttributeToUpdate(bgpMessage, flags, code, i, newAtt);
			} else {
				/* this is where the path attribute is added to the object  */
				BGP_addPathAttributeToUpdate(bgpMessage, flags, code, length, &rawMessage[idx]);
				idx += length;
			}
		}
		if (idx - attr_start_pos != uni.AttrLen) {
			log_err("Attribute length does not match position: attrLen: %d pos: %d\n", uni.AttrLen, idx - attr_start_pos);
		}
		if (uni.PeerIndex >= max_count) {
			log_err("PeerIndex is out of range: %d\n", uni.PeerIndex);
			return -1;
		}
		(*bgp_count)++;
		/* At this point this BGP message is complete add it to the table buffer */
		if (insertBGPTable(&(tablebuffer[uni.PeerIndex]), bgpMessage)) {
			log_err("%s: Unable to insert bgp message to table buffer", __FUNCTION__);
			return -1;
		}
	}			/* end for */

	return 0;
}


int 
MRT_processType_TableDump(uint8_t * rawMessage, MRTheader * mrtHeader,
      MRTmessage * mrtMessage_c, BMF * bmf, int *asNumLen, uint16_t * seqNo)
{

/*	   The TABLE_DUMP Type is used to encode the contents of a BGP Routing */
/*	   Information Base (RIB).  Each RIB entry is encoded in a distinct */
/*	   sequential MRT record.  It is RECOMMENDED that new MRT encoding */
/*	   implementations use the TABLE_DUMP_V2 Type (see below) instead of the */
/*	   TABLE_DUMP Type due to limitations in this type.  However, due to the */
/*	   significant volume of historical data encoded with this type, MRT */
/*	   decoding applications MAY wish to support this type. */
/* */
/*	   The Subtype field is used to encode whether the RIB entry contains */
/*	   IPv4 or IPv6 [RFC2460] addresses.  There are two possible values for */
/*	   the Subtype as shown below. */
/* */
/*	       1    AFI_IPv4 */
/*	       2    AFI_IPv6 */
/* */
/*	   The format of the TABLE_DUMP Type is illustrated below. */
/* */
/*	        0                   1                   2                   3 */
/*	        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |         View Number           |       Sequence Number         | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |                        Prefix (variable)                      | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       | Prefix Length |    Status     | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |                         Originated Time                       | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |                    Peer IP Address (variable)                 | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |           Peer AS             |       Attribute Length        | */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/*	       |                   BGP Attribute... (variable) */
/*	       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
/* */
/*	                         Figure 4: TABLE_DUMP Type */
/* */

	int 		idx = 0;
	int 		bgpidx = 0;
	int 		i;
	TABLE_DUMP_MSG 	tableDumpMsg;

	/* Temporary provision to find out TABLE DUMP V1 IPV6 subtype message */
	/* If encountered with IPV6 subtype then print it at standard output in HEX */
	if (mrtHeader->subtype == AFI_IPv6) {
		char 		buffer   [1024] = {0};
		for (idx = 0; idx < mrtHeader->length; idx++) {
			sprintf(buffer + (idx * 2), "%02X", rawMessage[idx]);
		}
		printf("Table Dump v1 IPV6 : %s\n", buffer);
		return 1;
	}
	/* View Number */
	READ_2BYTES(tableDumpMsg.viewNumber, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Sequence Number */
	READ_2BYTES(tableDumpMsg.sequenceNumber, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Prefix */
	int 		ipLen = 16;
	int 		af_inet = AF_INET6;
	if (mrtHeader->subtype == AFI_IPv4) {
		ipLen = 4;
		af_inet = AF_INET;
	}
	for (i = 0; i < ipLen; i++) {
		tableDumpMsg.prefix[i] = rawMessage[idx];
		idx += 1;
	}

	if (inet_ntop(af_inet, tableDumpMsg.prefix,
		      tableDumpMsg.prefixStr, ADDR_MAX_CHARS) == NULL) {
		log_err("mrtThread, read TABLE DUMP message: prefix address convert "
			"error!");
		return 1;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Prefix Length */
	tableDumpMsg.prefixLength = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* status */
	tableDumpMsg.status = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	if (tableDumpMsg.status != 1) {
		log_err("MRT_processType_TableDump: status = %d but status field "
			"should be 1", tableDumpMsg.status);
		return 1;
	}
	/* Originated Time */
	READ_4BYTES(tableDumpMsg.originatedTime, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Peer IP Address */
	for (i = 0; i < ipLen; i++) {
		tableDumpMsg.peerIP[i] = rawMessage[idx];
		idx += 1;
	}
	if (inet_ntop(af_inet, tableDumpMsg.peerIP,
		      tableDumpMsg.peerIPstr, ADDR_MAX_CHARS) == NULL) {
		log_err("MRT_processType_TableDump: peer address conversion "
			"error!");
		return 1;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Peer AS */
	READ_2BYTES(tableDumpMsg.peerAs, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* Attribute Length */
	READ_2BYTES(tableDumpMsg.attributeLength, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return 1;
	}
	/* BGP attributes */

	memmove(&tableDumpMsg.BGPAttr, &rawMessage[idx],
		tableDumpMsg.attributeLength);
	idx += tableDumpMsg.attributeLength;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDump: idx:%lu exceeded length:%lu",
			idx, mrtHeader->length);
		return 1;
	}
	/* Update BFM fields */
	(*bmf)->length = idx;
	(*bmf)->timestamp = tableDumpMsg.originatedTime;
	(*bmf)->precisiontime = 0;

	/* Create BGP message */
	int 		j = 0;
	int 		prefix_size;
	u_char 		packed_prifix[16];
	prefix_size = packPrefix(tableDumpMsg.prefix, ipLen, tableDumpMsg.prefixLength, packed_prifix);

	/* Assigning all 1s to BGP Marker */
	for (j = 0; j < 16; j++) {
		(*bmf)->message[j] = ~0;
		bgpidx += 1;
	}
	/* Update length field of BGP message */
	const uint16_t 	bgp_length =
	htons(23 + tableDumpMsg.attributeLength + 1 + prefix_size);
	memmove(&(*bmf)->message[bgpidx], &bgp_length, sizeof(bgp_length));
	bgpidx += sizeof(bgp_length);
	/* Update type field of BGP message */
	uint8_t 	bgp_type = 2;
	memmove(&(*bmf)->message[bgpidx], &bgp_type, sizeof(bgp_type));
	bgpidx += sizeof(bgp_type);
	/* Update Withdrawn Routes Length field of BGP message to 0 */
	uint16_t 	bgp_withdrawn_length = 0;
	memmove(&(*bmf)->message[bgpidx], &bgp_withdrawn_length, sizeof(bgp_withdrawn_length));
	bgpidx += sizeof(bgp_withdrawn_length);
	/* Update total Path Attribute Length of BGP message */
	const uint16_t 	atrlen = htons(tableDumpMsg.attributeLength);
	memmove(&(*bmf)->message[bgpidx], &atrlen, sizeof(atrlen));
	bgpidx += sizeof(tableDumpMsg.attributeLength);
	/* Update Path Attributes of BGP message */
	memmove(&(*bmf)->message[bgpidx], &tableDumpMsg.BGPAttr,
		tableDumpMsg.attributeLength);
	bgpidx += tableDumpMsg.attributeLength;
	/* Update length in NLRI field of BGP message */
	memmove(&(*bmf)->message[bgpidx], &tableDumpMsg.prefixLength,
		sizeof(tableDumpMsg.prefixLength));
	bgpidx += sizeof(tableDumpMsg.prefixLength);
	/* Update prefix field of BGP message */
	memmove(&(*bmf)->message[bgpidx], &packed_prifix,
		prefix_size);

	/* Update mrtMessage - Peer IP address and Peer As number */
	for (i = 0; i < ipLen; i++) {
		mrtMessage_c->peerIPAddress[i] = tableDumpMsg.peerIP[i];
		mrtMessage_c->localIPAddress[i] = 0;
	}
	mrtMessage_c->peerAs = tableDumpMsg.peerAs;
	*asNumLen = 2;
	mrtMessage_c->localAs = 0;
	*seqNo = tableDumpMsg.sequenceNumber;

	return 0;

}

int 
MRT_processType_TableDumpV2(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable,
	   int *entryCount, BMF ** bmfArray, MRTmessage *** mrtMessageArray,
			    int **asn_lengthArray, unsigned int *seqNo)
{

	switch (mrtHeader->subtype) {

		case PEER_INDEX_TABLE:
		if (MRT_processType_TableDumpV2_PeerIndexTable(rawMessage, mrtHeader,
							  peerIndexTable)) {
			return (1);
		} else
			return (0);

	case RIB_IPV4_UNICAST:
	case RIB_IPV4_MULTICAST:
	case RIB_IPV6_UNICAST:
	case RIB_IPV6_MULTICAST:
		if (MRT_processType_TableDumpV2_RIB_SUBTYPE(rawMessage, mrtHeader,
				       peerIndexTable, entryCount, bmfArray,
				 mrtMessageArray, asn_lengthArray, seqNo)) {
			return (1);
		} else {
			return (0);
		}
	case RIB_GENERIC:
		if (MRT_processType_TableDumpV2_GENERIC_SUBTYPE(rawMessage,
						     mrtHeader, bmfArray)) {
			return (1);
		} else
			return (0);

	default:
		log_err("Wrong subtype for TABLE DUMP V2: %d", mrtHeader->subtype);
		return (1);
	}

	return (0);
}

int 
MRT_processType_TableDumpV2_PeerIndexTable(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable)
{

	int 		idx = 0;
	int 		i;

	/* Create Peer Index Table */
	if (*peerIndexTable == NULL) {
		(*peerIndexTable) = (Peer_Index_Table *) malloc(sizeof(struct MRT_PEER_INDEX_TABLE_struct));
	} else {
		log_err("MRT_processType_TableDumpV2_PeerIndexTable: "
			"Second instance of PEER INDEX TABLE found.");
		return (1);
	}

	/* Collector BGP ID */
	READ_4BYTES((*peerIndexTable)->BGPSrcID, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			"exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* View Name Length */
	READ_2BYTES((*peerIndexTable)->ViewNameLen, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			"exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* View Name */
	if ((*peerIndexTable)->ViewNameLen != 0) {
		READ_2BYTES((*peerIndexTable)->ViewName, rawMessage[idx]);
		idx += 2;

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
	}
	/* Peer Count */
	READ_2BYTES((*peerIndexTable)->PeerCount, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu exceeded "
			"length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Allocate memory for peer entries */
	if ((*peerIndexTable)->PeerCount > 0) {

		(*peerIndexTable)->peerEntries = (Peer_Entry *) calloc
			((*peerIndexTable)->PeerCount, sizeof(Peer_Entry));

		if ((*peerIndexTable)->peerEntries == NULL) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: error in "
				"allocating memory for peer entries\n");
			return 1;
		}
	}
	for (i = 0; i < (*peerIndexTable)->PeerCount; i++) {

		/* Peer Type */
		(*peerIndexTable)->peerEntries[i].peerType = rawMessage[idx];
		idx++;

		if ((*peerIndexTable)->peerEntries[i].peerType > 3) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: Wrong Peer "
				"Type value:%lu", (*peerIndexTable)->peerEntries[i].peerType);
			return 1;
		}
		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu exceeded"
				"length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Peer BGP ID */
		READ_4BYTES((*peerIndexTable)->peerEntries[i].peerBGPID, rawMessage[idx]);
		idx += 4;

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Peer IP Address */
		int 		j;
		int 		ipLen = 16;
		if ((*peerIndexTable)->peerEntries[i].peerType == 0 ||
		    (*peerIndexTable)->peerEntries[i].peerType == 2) {
			ipLen = 4;
		}
		for (j = 0; j < ipLen; j++) {
			(*peerIndexTable)->peerEntries[i].peerIP[j] = rawMessage[idx];
			idx += 1;
		}

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Peer AS */
		if ((*peerIndexTable)->peerEntries[i].peerType == 0 ||
		    (*peerIndexTable)->peerEntries[i].peerType == 1) {
			READ_2BYTES((*peerIndexTable)->peerEntries[i].peerAS, rawMessage[idx]);
			idx = idx + 2;
		} else {
			READ_4BYTES((*peerIndexTable)->peerEntries[i].peerAS, rawMessage[idx]);
			idx = idx + 4;
		}

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
	}

	return (0);
}

int 
MRT_processType_TableDumpV2_RIB_SUBTYPE(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable,
	   int *entryCount, BMF ** bmfArray, MRTmessage *** mrtMessageArray,
				 int **asn_lengthArray, unsigned int *seqNo)
{

	Mrt_Rib_Table 	mrtRibTable;
	int 		idx = 0, 	ribEntryHeaderLength = 0;
	int 		i;

	/* Check If Peer Index table is present. */
	if (*peerIndexTable == NULL) {
		log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: Peer Index Table "
			"is not set");
		return 1;
	}
	/* Sequence Number */
	READ_4BYTES(mrtRibTable.SeqNumb, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu "
			"exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Update Sequence Number */
	*seqNo = mrtRibTable.SeqNumb;

	/* Prefix Length */
	mrtRibTable.PrefixLen = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
			"length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Prefix */
	int 		prefixBytes = 0;
	prefixBytes = (mrtRibTable.PrefixLen / 8);
	if (mrtRibTable.PrefixLen % 8 != 0) {
		prefixBytes += 1;
	}
	for (i = 0; i < prefixBytes; i++) {
		mrtRibTable.Prefix[i] = rawMessage[idx];
		idx += 1;
	}

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
			"length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Entry Count */
	READ_2BYTES(mrtRibTable.EntryCount, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
			"length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* store entry count value */
	*entryCount = mrtRibTable.EntryCount;

	/* Copy RIB Entry header */
	ribEntryHeaderLength = idx;

	/* Allocate memory for RIB entries */
	if (mrtRibTable.EntryCount > 0) {

		mrtRibTable.RibEntry = (Rib_Entry *) malloc
			(mrtRibTable.EntryCount * sizeof(Rib_Entry));

		if (mrtRibTable.RibEntry == NULL) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
				"allocating memory for peer entries\n");
			return (1);
		}
	}
	/* Allocate memory for BMF array */
	if (mrtRibTable.EntryCount > 0) {
		*bmfArray = malloc
			(mrtRibTable.EntryCount * sizeof(BMF));

		if (*bmfArray == NULL) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
				"allocating memory for BMF pointer array\n");
			return (1);
		}
	}
	/* Allocate memory for MrtMessage array */
	if (mrtRibTable.EntryCount > 0) {
		*mrtMessageArray = malloc
			(mrtRibTable.EntryCount * sizeof(MRTmessage *));

		if (*mrtMessageArray == NULL) {

			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
			"allocating memory for mrtMessage pointer array\n");
			return (1);
		}
	}
	/* Allocate memory for asn_length array */
	if (mrtRibTable.EntryCount > 0) {
		*asn_lengthArray = (int *) malloc
			(mrtRibTable.EntryCount * sizeof(int));

		if (*asn_lengthArray == NULL) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
			"allocating memory for asn_length pointer array\n");
			return (1);
		}
	}
	/* Loop to read each RIB entry */
	for (i = 0; i < mrtRibTable.EntryCount; i++) {

		/* pointers to locate position of RIB ENTRY in rawMessage */
		int 		ribEntryStart = 0;
		int 		ribEntryEnd = 0;
		int 		totalRibEntryLength = 0;
		uint8_t        *ribGenericEntry;
		ribEntryStart = idx;
		uint16_t 	pIndex;
		int 		bgpidx = 0;

		/* Peer Index */
		READ_2BYTES(mrtRibTable.RibEntry[i].PeerIndex, rawMessage[idx]);
		idx += 2;
		pIndex = mrtRibTable.RibEntry[i].PeerIndex;

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				"length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Originated Time */
		READ_4BYTES(mrtRibTable.RibEntry[i].OrigTime, rawMessage[idx]);
		idx += 4;

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				"length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Attribute Length */
		READ_2BYTES(mrtRibTable.RibEntry[i].AttrLen, rawMessage[idx]);
		idx += 2;

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				"length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* BGP Attributes */
		int 		j;
		for (j = 0; j < mrtRibTable.RibEntry[i].AttrLen; j++) {
			mrtRibTable.RibEntry[i].BGPAttr[j] = rawMessage[idx];
			idx += 1;
		}

		if (idx > mrtHeader->length) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				"length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Store end index of Rib entry */
		ribEntryEnd = idx;

		/* Allocate memory for to store complete Rib entry */
		totalRibEntryLength = (ribEntryEnd - ribEntryStart) +
			ribEntryHeaderLength;
		ribGenericEntry = (uint8_t *) malloc(totalRibEntryLength * sizeof(uint8_t));
		if (ribGenericEntry == NULL) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
				"allocating memory for Rib Generic Entry\n");
			return (1);
		}
		/* Copy complete Rib entry */
		memmove(&ribGenericEntry[0], &rawMessage[0], ribEntryHeaderLength);
		memmove(&ribGenericEntry[ribEntryHeaderLength],
		 &rawMessage[ribEntryStart], (ribEntryEnd - ribEntryStart));

		/* Create BMF with TABLE DUMP V2 message */
		(*bmfArray)[i] = createBMFWithData(0, BMF_TYPE_TABLE_TRANSFER,
						   ribGenericEntry);

		if ((*bmfArray)[i] == NULL) {
			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: "
				"Unable to create BMF");
			return (1);
		}
		/* Update BFM fields */
		(*bmfArray)[i]->length = totalRibEntryLength;
		(*bmfArray)[i]->timestamp = mrtRibTable.RibEntry[i].OrigTime;
		(*bmfArray)[i]->precisiontime = 0;

		/* Create BGP message */

		/* Assigning all 1s to BGP Marker */
		for (j = 0; j < 16; j++) {
			(*bmfArray)[i]->message[j] = ~0;
			bgpidx += 1;
		}

		/* Update length field of BGP message */
		const uint16_t 	bgp_length =
		htons(23 + mrtRibTable.RibEntry[i].AttrLen + 1 + prefixBytes);
		memmove(&(*bmfArray)[i]->message[bgpidx], &bgp_length, sizeof(bgp_length));
		bgpidx += sizeof(bgp_length);
		/* Update type field of BGP message */
		uint8_t 	bgp_type = 2;
		memmove(&(*bmfArray)[i]->message[bgpidx], &bgp_type, sizeof(bgp_type));
		bgpidx += sizeof(bgp_type);
		/* Update Withdrawn Routes Length field of BGP message to 0 */
		uint16_t 	bgp_withdrawn_length = 0;
		memmove(&(*bmfArray)[i]->message[bgpidx], &bgp_withdrawn_length, sizeof(bgp_withdrawn_length));
		bgpidx += sizeof(bgp_withdrawn_length);
		/* Update total Path Attribute Length of BGP message */
		const uint16_t 	atrlen = htons(mrtRibTable.RibEntry[i].AttrLen);
		memmove(&(*bmfArray)[i]->message[bgpidx], &atrlen, sizeof(atrlen));
		bgpidx += sizeof(atrlen);
		/* Update Path Attributes of BGP message */
		memmove(&(*bmfArray)[i]->message[bgpidx], &mrtRibTable.RibEntry[i].BGPAttr,
			mrtRibTable.RibEntry[i].AttrLen);
		bgpidx += mrtRibTable.RibEntry[i].AttrLen;
		/* Update length in NLRI field of BGP message */
		memmove(&(*bmfArray)[i]->message[bgpidx], &mrtRibTable.PrefixLen,
			sizeof(mrtRibTable.PrefixLen));
		bgpidx += sizeof(mrtRibTable.PrefixLen);
		/* Update prefix field of BGP messages */
		memmove(&(*bmfArray)[i]->message[bgpidx], &mrtRibTable.Prefix,
			prefixBytes);

		/* Allocate memory for MrtMessage */
		(*mrtMessageArray)[i] = malloc(sizeof(MRTmessage));

		if ((*mrtMessageArray)[i] == NULL) {

			log_err("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
				"allocating memory for mrtMessage\n");
			return (1);
		}
		/* Copy corresponding data from peer index table to MRT Message */
		/* for this Rib entry */
		int 		ipLen = 16;
		int 		asNLen = 4;
		if ((*peerIndexTable)->peerEntries[pIndex].peerType == 0 ||
		    (*peerIndexTable)->peerEntries[pIndex].peerType == 2) {
			ipLen = 4;
		}
		if ((*peerIndexTable)->peerEntries[pIndex].peerType == 0 ||
		    (*peerIndexTable)->peerEntries[pIndex].peerType == 1) {
			asNLen = 2;
		}
		(*asn_lengthArray)[i] = asNLen;

		memmove((*mrtMessageArray)[i]->peerIPAddress,
		      (*peerIndexTable)->peerEntries[pIndex].peerIP, ipLen);

		(*mrtMessageArray)[i]->peerAs =
			(*peerIndexTable)->peerEntries[pIndex].peerAS;

		for (j = 0; j < ipLen; j++) {
			(*mrtMessageArray)[i]->localIPAddress[j] = 0;
		}
		(*mrtMessageArray)[i]->localAs = 0;

	}

	free(mrtRibTable.RibEntry);

	return 0;
}


int 
MRT_processType_TableDumpV2_GENERIC_SUBTYPE(uint8_t * rawMessage,
				     MRTheader * mrtHeader, BMF ** bmfArray)
{

	int 		idx = 0;

	/* Temporary provision to find out TABLE DUMP V2 GENERIC subtype message */
	/* If encountered with GENERIC subtype then print it at standard output */
	/* in HEX */
	char 		buffer   [1024] = {0};
	for (idx = 0; idx < mrtHeader->length; idx++) {
		sprintf(buffer + (idx * 2), "%02X", rawMessage[idx]);
	}
	printf("MRT_processType_TableDumpV2_GENERIC_SUBTYPE : %s\n", buffer);
	return 1;
}


int 
packPrefix(uint8_t * prefixIpAddr, int ipVer, int prefixLen,
	   u_char * packedPrefix)
{
	int 		i;
	if (ipVer == 4) {
		unsigned long 	mask = (0xFFFFFFFF << (32 - prefixLen)) & 0xFFFFFFFF;
		for (i = 0; i < ((prefixLen % 8 == 0) ? (prefixLen / 8) : ((prefixLen / 8) + 1)); i++) {
			uint8_t 	mask_byte = (mask >> (32 - 8 * (i + 1))) & 0xFF;
			packedPrefix[i] = prefixIpAddr[i] & mask_byte;
		}

		return ((prefixLen % 8 == 0) ? (prefixLen / 8) : ((prefixLen / 8) + 1));
	}
	/* This is temporary provision, Need upgradation to handle IPV6 prefix */
	else if (ipVer == 6) {
		log_err("packPrefix: IPV6 \n");
		return (0);
	} else {
		log_err("packPrefix: Wrong IP address version\n");
		return (0);
	}
}
