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

/* externally visible structures and functions for mrts */
#include "mrtProcessMSG.h"
#include "../Util/utils.h"
#include "mrtProcessTable.h"
/*#define DEBUG */
#define BGPSIZE 5000

/*
 * Purpose: read from the backlog and process messages
 * Input:  the control MRT structure for this instance
 * (and therefore the backlog)
 * Output: NONE
 * Description: This function will continue to run until it is
 * Killed by its parent
 */
void           *
MRT_processMessages(void *arg)
{

	/* the mrt node structure */
	MrtNode        *cn = arg;
	uint8_t 	rawMessage[MAX_MRT_LENGTH];
	uint8_t 	rawMessage_p[MAX_MRT_LENGTH];

#ifdef DEBUG
	log_msg("MRT reading thread backlog is %x\n", &(cn->backlog.lock));
#endif

	/* we maintain a current and previous message */
	/* this is because we sometimes don't detect a bad message until */
	/* we are trying to parse the header of the next. */
	MRTheader 	mrtHeader_c;	/* current mrt header  */
	MRTmessage 	mrtMessage_c;	/* curent mrt message */
	BMF 		bmf_c = NULL;	/* current bmf representation */
	MRTheader 	mrtHeader_p;	/* previous mrt header */
	MRTmessage 	mrtMessage_p;	/* prefious mrt message */
	BMF 		bmf_p = NULL;	/* prefioux bmf representation */


	/* as long as we are not shutting down */
	while (cn->deleteMrt == FALSE) {

		/* this loop is responsible for reading a single MRT message from the  */
		/* backlog */
		int 		read_result;
		int 		loop_cnt = 0;
		do {
			/* read a single message from the backlog */
			/* lock the backlog */
			if (pthread_mutex_lock(&(cn->backlog.lock))) {
				log_err("Unable to get the backlog lock");
				destroyMrt(cn->id);
				pthread_exit((void *) 1);
			}
			/* read */
			read_result = backlog_read_MRT(&(cn->backlog), &mrtHeader_c,
						rawMessage, MAX_MRT_LENGTH);
			if (read_result) {
				/* a problem has occured and we do not have a message */
				/* less than 0 is returned if there is a corrupt message */
				if (read_result < 0) {
					if (!loop_cnt) {
						log_err("A corrupt message has been found in the backlog...skipping"
						      " (%d)", read_result);
						char 		str      [MAX_MRT_LENGTH];
						bin2hexstr(&rawMessage_p, mrtHeader_p.length, str, MAX_MRT_LENGTH);
						log_err("Previous Type: %u Subtype: %u Length: %lu\n",
							mrtHeader_p.type, mrtHeader_p.subtype, mrtHeader_p.length);
						log_err("Previous Body: %s\n", str);

					}
					/* try to read again */
					if (MRT_backlog_fastforward_BGP(&(cn->backlog))) {
						if (!loop_cnt) {
							log_err("Fast Forwarding has Failed\n");
						}
						read_result = -1;
					}
					if (bmf_p != NULL) {
						destroyBMF(bmf_p);
						bmf_p = NULL;
					}
					read_result = 1;
				} else if (read_result > 1) {
#ifdef DEBUG
					log_msg("no room in buffer for message\n");
#endif
					/* we do not have room in the buffer for the message */
					/* this should never happen, if it does we will get stuck */
					log_err("MRT: read buffer too small: attempting to fast forward");
					MRT_backlog_fastforward_BGP(&(cn->backlog));
					if (bmf_p != NULL) {
						destroyBMF(bmf_p);
						bmf_p = NULL;
					}
					read_result = 1;
				}
			} else {
#ifdef DEBUG
				log_msg("successfully read\n");
#endif
			}
			/* unlock the backlog */
			if (pthread_mutex_unlock(&(cn->backlog.lock))) {
				log_err("Unable to unlock the backlog lock");
				destroyMrt(cn->id);
				pthread_exit((void *) 1);
			}
			/* loop_cnt++; */
		} while (1 == read_result && cn->deleteMrt == FALSE);


#ifdef DEBUG
		log_msg("Validity of header: %d\n", MRT_header_invalid(&mrtHeader_c));
#endif
		if (read_result < 0) {
			continue;
		}
		if (cn->deleteMrt == TRUE) {
			break;
		}
		/*
		 * MRT2bmf(rawMessage,rawMessage_p,mrtHeader_c,bmf_c,bmf_p); now that we are here
		 * we must have a message
		 * http://tools.ietf.org/html/draft-ietf-grow-mrt-17#section-4
		 */
		switch (mrtHeader_c.type) {

			/* this is the only type we are handling in this loop all others are  */
			/* caught at the end of the switch */
		case BGP4MP:
			{
				/* this is defaulting to a 4 byte as length  */
				/* (the case statement changes it to 2 for type 1) */
				int 		asNumLen = 4;
				switch (mrtHeader_c.subtype) {

				case BGP4MP_MESSAGE:
					asNumLen = 2;
				case BGP4MP_MESSAGE_AS4:
					/*
					 * this is the bulk of the handling code... if a message is
					 * corrupt
					 */
					/* we have to remove it and the one before */
					/* it from processing (so we are always one behind) */
					if (MRT_processType16SubtypeMessage(rawMessage, asNumLen,
									    &mrtHeader_c, &mrtMessage_c, &bmf_c)) {
						/* FAILURE: zero out all current data  */
						log_err("mrtThread: Unable to parse MRT message: removing "
						      "previous as well\n");
						log_err("mrtThread: Current (len=%lu type=%u subtype=%u "
							" aslen=%d)\n",
							mrtHeader_c.length, mrtHeader_c.type,
							mrtHeader_c.subtype, asNumLen);
						log_err("mrtThread: Previous (len=%lu type=%u subtype=%u "
							" asnlen=%d)\n",
							mrtHeader_p.length, mrtHeader_p.type,
							mrtHeader_p.subtype, asNumLen);
						if (bmf_p != NULL) {
							destroyBMF(bmf_p);
							bmf_p = NULL;
						}
						if (bmf_c != NULL) {
							destroyBMF(bmf_c);
							bmf_c = NULL;
						}
					} else {
						/* SUCCESS! parsing the current message */
						/*
						 * if the previous has not been zeroed out submit
						 * it
						 */
						if (bmf_p != NULL) {
#ifdef DEBUG
							log_msg("mrtThread, submitting time %lu type %u subtype %u "
								"length %lu\n", mrtHeader_p.timestamp,
								mrtHeader_p.type, mrtHeader_p.subtype,
							mrtHeader_p.length);
#endif
							submitBMF(cn, &mrtHeader_p, &mrtMessage_p, bmf_p);
						}
						/*
						 * make the current bmf the previous for the next
						 * iteration
						 */
						memmove(&rawMessage_p, &rawMessage, MAX_MRT_LENGTH);
						memmove(&mrtHeader_p, &mrtHeader_c, sizeof(MRTheader));
						memmove(&mrtMessage_p, &mrtMessage_c, sizeof(MRTmessage));
						bmf_p = bmf_c;
						bmf_c = NULL;
					}
					break;

					/* the subtypes that we don't handle */
				case BGP4MP_STATE_CHANGE:
				case BGP4MP_STATE_CHANGE_AS4:
				case BGP4MP_MESSAGE_LOCAL:
				case BGP4MP_MESSAGE_AS4_LOCAL:
					log_warning("mrtThread, recieved an unsupported subtype: %d\n",
						    mrtHeader_c.subtype);
					break;
					/* a signal that we got a corrupt message */
				default:
					if (bmf_p != NULL) {
						log_warning("mrtThread, previous message with type %u subtype "
							    "%u, len %u",
							    mrtHeader_p.type, mrtHeader_p.subtype,
							mrtHeader_p.length);
					} else {
						log_warning("mrtThread, previous message is not available\n");
					}
					destroyBMF(bmf_p);
					bmf_p = NULL;
				}
				break;
			}

		case TABLE_DUMP:
		case TABLE_DUMP_V2:
			/* in this case we actually want to shut down the connection and exit */
			log_err("mrtThread, recieved a table dump message, "
				"shut down connection\n");
			cn->deleteMrt = TRUE;
			break;
			/* all of the types that this code does not handle */
		case OSPFv2:
		case BGP4MP_ET:
		case ISIS:
		case ISIS_ET:
		case OSPFv3:
		case OSPFv3_ET:
			log_warning("mrtThread, received an unsupported MRT message\n");
			log_warning("mrtThread, time %d type %u, subtype %u and len %u! "
				    "skipping....",
				    mrtHeader_c.timestamp, mrtHeader_c.type,
				    mrtHeader_c.subtype, mrtHeader_c.length);
			break;

		default:
			log_warning("mrtThread, received a corrupt MRT message with time %d "
				    "type %u, subtype %u and len %u!",
				    mrtHeader_c.timestamp, mrtHeader_c.type,
				    mrtHeader_c.subtype, mrtHeader_c.length);
			if (bmf_p != NULL) {
				log_warning("mrtThread, previous message with type %u subtype %u, "
					    "len %u",
				      mrtHeader_p.type, mrtHeader_p.subtype,
					    mrtHeader_p.length);
			} else {
				log_warning("mrtThread, previous message is not available\n");
			}
			destroyBMF(bmf_p);
			bmf_p = NULL;
		}
	}
	return NULL;
}

int 
MRT2bmf(uint8_t * rawMessage, MRTmessage * mrtMessage_c, MRTheader * mrtHeader_c,
	BMF * bmf_c, int *asNumLen)
{


	switch (mrtHeader_c->type) {
		/* this is the only type we are handling in this loop all others are  */
		/* caught at the end of the switch */
		case BGP4MP:
		{
			/* this is defaulting to a 4 byte as length  */
			/* (the case statement changes it to 2 for type 1) */
			*asNumLen = 4;
			switch (mrtHeader_c->subtype) {

			case BGP4MP_MESSAGE:
				*asNumLen = 2;
			case BGP4MP_MESSAGE_AS4:
				/* this is the bulk of the handling code... if a message is corrupt */
				/* we have to remove it and the one before */
				/* it from processing (so we are always one behind) */
				if (MRT_processType16SubtypeMessage(rawMessage, *asNumLen,
					mrtHeader_c, mrtMessage_c, bmf_c)) {
					return 1;
				} else {
					return 0;
				}
				break;

				/* the subtypes that we don't handle */
			case BGP4MP_STATE_CHANGE:
			case BGP4MP_STATE_CHANGE_AS4:
			case BGP4MP_MESSAGE_LOCAL:
			case BGP4MP_MESSAGE_AS4_LOCAL:
				fprintf(stderr, "mrtThread, recieved an unsupported subtype: %d\n",
					mrtHeader_c->subtype);
				break;
				/* a signal that we got a corrupt message */
			default:
				fprintf(stderr, "mrtThread, corrupt message\n");
			}
			break;
		}

	case TABLE_DUMP:
	case TABLE_DUMP_V2:
		/* in this case we actually want to shut down the connection and exit */
		fprintf(stderr, "mrtThread, recieved a table dump message, "
			"shut down connection\n");
		break;
		/* all of the types that this code does not handle */
	case OSPFv2:
	case BGP4MP_ET:
	case ISIS:
	case ISIS_ET:
	case OSPFv3:
	case OSPFv3_ET:
		fprintf(stderr, "mrtThread, received an unsupported MRT message\n");
		fprintf(stderr, "mrtThread, time %d type %u, subtype %u and len %u! "
			"skipping....",
			mrtHeader_c->timestamp, mrtHeader_c->type,
			mrtHeader_c->subtype, mrtHeader_c->length);
		break;

	default:
		fprintf(stderr, "mrtThread, received a corrupt MRT message with time %d "
			"type %u, subtype %u and len %u!",
			mrtHeader_c->timestamp, mrtHeader_c->type,
			mrtHeader_c->subtype, mrtHeader_c->length);
	}
	return 1;
}

/*
 * Purpose: this code processes MRT messages of type 16  BGP4MP subtype 1,4
 *          UPDATE
 * Input:  raw message, desired asN length, header, message and bmf pointer
 * Output: 1 for success
 *         0 for failure
 *         the bmf object is populated
 * Description: This function will process a single MRT message and
 *               then return
 */
int
MRT_processType16SubtypeMessage(uint8_t * rawMessage, int asNumLen,
			     MRTheader * mrtHeader, MRTmessage * mrtMessage,
				BMF * bmf)
{
	/* 4.4.2. BGP4MP_MESSAGE Subtype */
	/* */
	/* */
	/* This Subtype is used to encode BGP messages.  It can be used to */
	/* encode any Type of BGP message.  The entire BGP message is */
	/* encapsulated in the BGP Message field, including the 16-octet marker, */
	/* the 2-octet length, and the 1-octet type fields.  The BGP4MP_MESSAGE */
	/* Subtype does not support 4-Byte AS numbers.  The AS_PATH contained in */
	/* these messages MUST only consist of 2-Byte AS numbers.  The */
	/* BGP4MP_MESSAGE_AS4 Subtype updates the BGP4MP_MESSAGE Subtype in */
	/* order to support 4-Byte AS numbers.  The BGP4MP_MESSAGE fields are */
	/* shown below: */
	/* */
	/* 0                   1                   2                   3 */
	/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |         Peer AS number        |        Local AS number        | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |        Interface Index        |        Address Family         | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                      Peer IP address (variable)               | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                      Local IP address (variable)              | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                    BGP Message... (variable) */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* */
	/* 4.4.3. BGP4MP_MESSAGE_AS4 Subtype */
	/* */
	/* */
	/* This Subtype updates the BGP4MP_MESSAGE Subtype to support 4-Byte AS */
	/* numbers.  The BGP4MP_MESSAGE_AS4 Subtype is otherwise identical to */
	/* the BGP4MP_MESSAGE Subtype.  The AS_PATH in these messages MUST only */
	/* consist of 4-Byte AS numbers.  The BGP4MP_MESSAGE_AS4 fields are */
	/* shown below: */
	/* */
	/* 0                   1                   2                   3 */
	/* 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                         Peer AS number                        | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                         Local AS number                       | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |        Interface Index        |        Address Family         | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                      Peer IP address (variable)               | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                      Local IP address (variable)              | */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	/* |                    BGP Message... (variable) */
	/* +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ */
	int 		idx = 0;
	int 		i;

	/* Peer AS number  */
	if (asNumLen == 2) {
		READ_2BYTES(mrtMessage->peerAs, rawMessage[idx]);
		idx += 2;
	} else {
		READ_4BYTES(mrtMessage->peerAs, rawMessage[idx]);
		idx += 4;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* Local As number */
	if (asNumLen == 2) {
		READ_2BYTES(mrtMessage->localAs, rawMessage[idx]);
		idx += 2;
	} else {
		READ_4BYTES(mrtMessage->localAs, rawMessage[idx]);
		idx += 4;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* Interface Index */
	READ_2BYTES(mrtMessage->interfaceIndex, rawMessage[idx]);
	idx += 2;
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* Address Family */
	READ_2BYTES(mrtMessage->addressFamily, rawMessage[idx]);
	idx += 2;
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* Peer IP address */
	int 		ip_len_bytes = 16;
	int 		af_inet = AF_INET6;
	if (mrtMessage->addressFamily == 1) {
		ip_len_bytes = 4;
		af_inet = AF_INET;
	}
	for (i = 0; i < ip_len_bytes; i++) {
		mrtMessage->peerIPAddress[i] = rawMessage[idx];
		idx += 1;
	}
	if (inet_ntop(af_inet, mrtMessage->peerIPAddress,
		 mrtMessage->peerIPAddressString, ADDR_MAX_CHARS) == NULL) {
		log_err("mrtThread, read BGP4MP_MESSAGE message: peer address convert "
			"error!");
		return -1;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* Local IP address */
	for (i = 0; i < ip_len_bytes; i++) {
		mrtMessage->localIPAddress[i] = rawMessage[idx];
		idx += 1;
	}
	if (inet_ntop(af_inet, mrtMessage->localIPAddress,
		mrtMessage->localIPAddressString, ADDR_MAX_CHARS) == NULL) {
		log_err("mrtThread, read BGP4MP_MESSAGE message: peer address convert "
			"error!");
		return -1;
	}
	if (idx > mrtHeader->length) {
		log_err("MRT_processType16SubtypeMessage: idx:%lu exceeded length:%lu\n",
			idx, mrtHeader->length);
		return -1;
	}
	/* All but the BGP message itself has been read and so now we need to see  */
	/* if we can read the BGP raw message and make BMF message */
	int 		bgp_length = mrtHeader->length - idx;
	if (bgp_length < 0) {
		log_err("MRT_processtype16SubtypeMessage: the length is calculated to be "
			"less than 0\n");
		return -1;
	}
	if (bgp_length <= BGP_HEADER_LEN) {
		log_err("MRT_processtype16SubtypeMessage: the length is calculated to be "
			"less than the bgp header length %d\n", bgp_length);
		return -1;
	}
	int 		tmpIdx = idx;
	for (; tmpIdx < 16; tmpIdx++) {
		if (rawMessage[tmpIdx] != 0xff) {
			log_err("MRT_processtype16SubtypeMessage: Unable to continue with "
			  "message, BGP marker not found where expected\n");
			return -1;
		}
	}

	(*bmf) = createBMF(0, BMF_TYPE_MSG_FROM_PEER, NULL, 0);
	if ((*bmf) == NULL) {
		log_err("MRT_processType16SubtypeMessage: Unable to allocate memory\n");
		return (-1);
	}
	(*bmf)->timestamp = mrtHeader->timestamp;
	(*bmf)->precisiontime = 0;
	if (bgpmonMessageAppend((*bmf), &rawMessage[idx], bgp_length)) {
		log_err("MRT_processType16SubtypeMessage: Unable to submit message\n");
		return -1;
	}
	return 0;
}

/*
 * Purpose: this code attaches a session id to the BMF and submits it to the Q.
 * Input:  mrtHeader,bmf object
 * Output: 0 for success
 *         1 for success, but queue now full
 *        -1 for failure
 * Description:
 */
int
submitBMF(MrtNode * cn, MRTheader * mrtHeader, MRTmessage * mrtMessage, BMF bmf)
{
	int 		sessionID;
	int 		asNumLen = 4;
	if (mrtHeader->subtype == 1) {
		asNumLen = 2;
	}
	/* first search is for a full session, also created by an update message */
	sessionID = findSession(mrtMessage->peerAs, mrtMessage->localAs, 179, 179,
				mrtMessage->peerIPAddressString,
				mrtMessage->localIPAddressString);
	if (sessionID < 0) {
		/* this search will find one that was created by a table dump  */
		/* ( a less specific search ) */
		sessionID = findSession_R_ASNIP_C_IP(mrtMessage->peerAs,
					    mrtMessage->peerIPAddressString,
						     cn->addr);
	}
	/* no session found, likely there is no match */
	if (sessionID < 0) {
		/*
		 * this will do a search and create (the extra search is to prevent race conditions
		 * and is in an atomic block
		 */
		sessionID = findOrCreateMRTSessionStruct(mrtMessage->peerAs,
					    mrtMessage->peerIPAddressString,
						  cn->addr, cn->labelAction,
					      asNumLen, stateMrtEstablished,
							 eventNone);
	}
	/* if we still don't have a valid session there has been a failure */
	if (sessionID < 0) {
		log_err("mrtThread (submitBMF), failed to create a new session for peerAs"
			" %lu,  monitorAs %lu, peerIP %s, monitorIP %s",
			mrtMessage->peerAs, mrtMessage->localAs,
			mrtMessage->peerIPAddressString, mrtMessage->localIPAddressString);
		destroyBMF(bmf);
		bmf = NULL;
		return -1;
	}
#ifdef DEBUG
	log_msg("mrtThread (submitBMF), found or created a session for peerAs %lu, "
		" monitorAs %lu, peerIP %s, monitorIP %s",
		mrtMessage->peerAs, mrtMessage->localAs,
	 mrtMessage->peerIPAddressString, mrtMessage->localIPAddressString);
#endif

	/* grab the session and make sure it has full session information */
	Session_structp session = getSessionByID(sessionID);
	strcpy(session->configInUse.localAddr, mrtMessage->localIPAddressString);
	session->configInUse.localAS2 = mrtMessage->localAs;
	setSessionASNumberLength(sessionID, asNumLen);

	/* if state has changed (node disconnected and connected back) */
	if (getSessionState(sessionID) != stateMrtEstablished) {
		setSessionState(getSessionByID(sessionID), stateMrtEstablished, eventNone);
	}
	/* write the message to the queue */
	bmf->sessionID = (uint16_t) sessionID;
	int 		q_full = writeQueue(cn->qWriter, bmf);
	incrementSessionMsgCount(sessionID);
	return q_full;
}


int 
processMRTTableDumpFile(FILE * FileIn,
	 const char monitor_addr_str[ADDR_MAX_CHARS], int monitor_addr_type,
			uint32_t monitor_asn, uint16_t monitor_port)
{

	MRTheader 	mrtHeader;
	MRTmessage 	mrtMessage;
	uint8_t 	bgpmsg [BGPSIZE];
	char           *xmlTestBuffer;
	int 		max_len = 100000;
	int 		monitor_asn_len;
	Peer_Index_Table *peerIndexTable = NULL;

	/* Set file pointer to starting location */
	rewind(FileIn);

	/* create a buffer */
	xmlTestBuffer = (char *) calloc(max_len, sizeof(char));
	if (xmlTestBuffer == NULL) {
		goto exit_fail;
	}
	/* Find monitor AS number length */
	if (monitor_asn <= 65535) {
		monitor_asn_len = 2;
	} else {
		monitor_asn_len = 4;
	}

	/* in a loop -- this line reads a header */
	int 		num;
	while ((num = fread(&mrtHeader, sizeof(MRTheader), 1, FileIn)) > 0) {
		u_int32_t 	mrttime = 0;
		u_int16_t 	type = 0;
		u_int32_t 	length = 0;

		/* read a single message */
		type = ntohs(mrtHeader.type);
		mrtHeader.type = type;

		length = ntohl(mrtHeader.length);
		mrtHeader.length = length;
		/* if (length < 0 || length > BGPSIZE){ */
		if (length >= BGPSIZE) {
			log_err("Length of BGPmessage is wrong\n");
			goto exit_fail;
		}
		mrttime = ntohl(mrtHeader.timestamp);
		mrtHeader.timestamp = mrttime;
		mrtHeader.subtype = ntohs(mrtHeader.subtype);
		/* Read file contents into buffer */
		num = fread(bgpmsg, length, 1, FileIn);
		if (num < 0) {
			log_err("BGP msg fread failed!\n");
			goto exit_fail;
		}
		if (type == 12) {

			/* create the BMF structure */
			BMF 		bmf;
			bmf = createBMF(0, BMF_TYPE_TABLE_TRANSFER, NULL, 0);
			if (bmf == NULL) {
				log_err("processMRTTableDumpFile: Unable to create BMF");
				goto exit_fail;
			}
			int 		asn_length;
			uint16_t 	seqNo;
			if (MRT_processType_TableDump(bgpmsg, &mrtHeader,
				  &mrtMessage, &bmf, &asn_length, &seqNo)) {
				goto exit_fail;
			}
			/* create the state data needed by the XML module */
			bgp_monitor_data state_data;
			inet_ntop(AF_INET, mrtMessage.peerIPAddress,
				state_data.source_addr, ADDRESS_STRING_LEN);
			state_data.source_asn_length = asn_length;
			state_data.source_asn = mrtMessage.peerAs;
			state_data.source_port = 179;
			strncpy(state_data.monitor_addr, monitor_addr_str, ADDRESS_STRING_LEN);
			state_data.monitor_asn_length = monitor_asn_len;
			state_data.monitor_asn = monitor_asn;
			state_data.monitor_port = monitor_port;
			/* In this case destination and monitor node is same */
			strncpy(state_data.dest_addr, monitor_addr_str, ADDRESS_STRING_LEN);
			state_data.dest_asn_length = monitor_asn_len;
			state_data.dest_asn = monitor_asn;
			state_data.dest_port = monitor_port;
			state_data.sequence = seqNo;
			state_data.asn_size = asn_length;

			/* call the XML module and spit the result to STDOUT */
			/* memset(xmlTestBuffer, '\0',max_len); */
			if (0 == BMF2XML(bmf, xmlTestBuffer, max_len, (void *) &state_data)) {
				fprintf(stderr, "BMF2XML failed\n");
				goto exit_fail;
			}
			fprintf(stdout, "%s\n", xmlTestBuffer);
			destroyBMF(bmf);
		} else if (type == 13) {
			BMF            *bmfArray;
			MRTmessage    **mrtMessageArray;
			int 		entryCount = 0, i;
			int            *asn_lengthArray;
			unsigned int 	seqNo;
			if (MRT_processType_TableDumpV2(bgpmsg, &mrtHeader,
				    &peerIndexTable, &entryCount, &bmfArray,
			      &mrtMessageArray, &asn_lengthArray, &seqNo)) {
				fprintf(stderr, "processMRTTableDumpFile: "
					"Unable to parse Message\n");
				goto exit_fail;
			}
			if (mrtHeader.subtype != PEER_INDEX_TABLE) {
				for (i = 0; i < entryCount; i++) {

					/* create the state data needed by the XML module */
					bgp_monitor_data state_data;

					inet_ntop(AF_INET, mrtMessageArray[i]->peerIPAddress,
						  state_data.source_addr, ADDRESS_STRING_LEN);
					state_data.source_asn_length = asn_lengthArray[i];
					state_data.source_asn = mrtMessageArray[i]->peerAs;
					state_data.source_port = 179;
					strncpy(state_data.monitor_addr, monitor_addr_str, ADDRESS_STRING_LEN);
					state_data.monitor_asn_length = monitor_asn_len;
					state_data.monitor_asn = monitor_asn;
					state_data.monitor_port = monitor_port;
					strncpy(state_data.dest_addr, monitor_addr_str, ADDRESS_STRING_LEN);
					state_data.dest_asn_length = monitor_asn_len;
					state_data.dest_asn = monitor_asn;
					state_data.dest_port = monitor_port;
					state_data.sequence = seqNo;
					state_data.asn_size = asn_lengthArray[i];
					/* call the XML module and spit the result to STDOUT */
					/* memset(xmlTestBuffer, '\0',max_len); */
					if (0 == BMF2XML(bmfArray[i], xmlTestBuffer, max_len, (void *) &state_data)) {
						fprintf(stderr, "BMF2XML failed\n");
						goto exit_fail;
					}
					fprintf(stdout, "%s\n", xmlTestBuffer);

					free(mrtMessageArray[i]);
					free(bmfArray[i]->data);
					free(bmfArray[i]);
				}
				free(mrtMessageArray);
				free(asn_lengthArray);
			}
		} else {
			log_err("processMRTTableDumpFile: MRT type is incorrect!\n");
			goto exit_fail;
		}
	}

	goto exit_sucess;

exit_fail:
	free(xmlTestBuffer);
	return (1);

exit_sucess:
	free(xmlTestBuffer);
	return (0);
}


/*
 * Purpose : Checks if string is a valid IP address
 * Input   : Pointer to character string of IP address
 * Output  : 0 for success
 *           1 for failure
 */
int 
isValidIpAddress(char *ipAddress, int ipType)
{
	struct sockaddr_in sa;
	struct sockaddr_in6 sa6;
	int 		result;

	if (ipType == 4) {
		result = inet_pton(AF_INET, ipAddress, &(sa.sin_addr));
	} else if (ipType == 6) {
		result = inet_pton(AF_INET6, ipAddress, &(sa6.sin6_addr));
	} else {
		log_err("isValidIpAddress: wrong IP address version\n");
		return 1;
	}

	if (result != 0) {
		return 0;
	}
	return 1;
}
