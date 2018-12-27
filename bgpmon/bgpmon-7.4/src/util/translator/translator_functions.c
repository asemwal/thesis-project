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
 *  File: translator_functions.c
 *  Authors: Darshan Wash <darshan.wash@gmail.com>, dsp <dsp@2f30.org>
 *  Date: Sep. 2014
 */

#include "translator.h"

int 
add_to_seen_list(struct seen_list * list, char *ip, uint32_t origtime)
{
	struct seen_entry *tmp;
	struct tm      *lt1, *lt2;
	LIST_FOREACH(tmp, &list->head, pointers) {
		if (strncmp(tmp->ipstr, ip, ADDR_MAX_CHARS) == 0) {
			if (origtime < tmp->seen) {
				lt1 = localtime((time_t *) & origtime);
				lt2 = localtime((time_t *) & tmp->seen);
				if (lt1 == NULL || lt2 == NULL) {
					trans_log("[ERROR] localtime. Filename:%s peer:%s\n", \
						  mrt_file, tmp->ipstr);
					return -1;
				}
				trans_log("Filename:%s peer:%s time:%d  \
					most recent time:%d (%s)", mrt_file, tmp->ipstr, origtime, \
					  tmp->seen, asctime(lt2));
			} else {
				tmp->seen = origtime;
			}
			return 1;
		}
	}
	struct seen_entry *se = malloc(sizeof(struct seen_entry));
	size_t 		numchar = strnlen(ip, ADDR_MAX_CHARS);
	se->ipstr = strndup(ip, numchar);
	se->strsiz = numchar;
	se->seen = origtime;
	LIST_INSERT_HEAD(&list->head, se, pointers);
	(list->size)++;
	return 1;
}

int 
free_seen_list(struct seen_list * list)
{
	struct seen_entry *ep;
	while (!LIST_EMPTY(&list->head)) {
		ep = LIST_FIRST(&list->head);
		free(ep->ipstr);
		LIST_REMOVE(ep, pointers);
		free(ep);
	}
	return 1;
}

void 
print_seen_list(struct seen_list * list)
{
	struct seen_entry *ep;
	struct tm      *lt;
	printf("---DUMPING SEEN LIST---\ntotal size:%zd \n", list->size);
	LIST_FOREACH(ep, &list->head, pointers) {
		if ((lt = localtime((time_t *) & ep->seen)) == NULL) {
			trans_log("localtime returned NULL");
			return;
		}
		printf(" Peer IP: %s , time: %s \n", ep->ipstr, asctime(lt));
	}
	return;
}

int 
trans_is_valid_IP(char *ipAddress, int ipType)
{
	struct sockaddr_in sa;
	struct sockaddr_in6 sa6;
	int 		result;

	if (ipType == 4) {
		result = inet_pton(AF_INET, ipAddress, &(sa.sin_addr));
	} else if (ipType == 6) {
		result = inet_pton(AF_INET6, ipAddress, &(sa6.sin6_addr));
	} else {
		trans_log("isValidIpAddress: wrong IP address version\n");
		return 0;
	}

	if (result == 0 || result == -1) {
		return 0;
	}
	return 1;
}

int 
trans_process_update_file()
{
	char 		error = 0;
	int 		num      , ret = 0;
	u_int32_t 	mrttime = 0;
	u_int16_t 	type = 0;
	u_int32_t 	length = 0;
	counter = largercounter = 0;	/* reset the glob msg counter */
	MRTheader 	mrtHeader;
	MRTmessage 	mrtMessage;
	/* create the BMF structure */
	BMF 		bmf;
	/* create the state data needed by the XML module */
	bgp_monitor_data state_data;
	state_data.source_port = state_data.monitor_port = state_data.dest_port = 179;
	state_data.sequence = 50000;

	while ((num = fread(&mrtHeader, sizeof(MRTheader), 1, FileIn)) > 0 && error == 0) {
		counter++;
		type = ntohs(mrtHeader.type);
		mrtHeader.type = type;
		length = ntohl(mrtHeader.length);
		mrtHeader.length = length;
		if (length > BGPSIZE && length < 2 * BGPSIZE) {
			largercounter++;
			trans_log("Length [%d] of BGPmessage %d is larger than RFC, at"
			       "fpos:%ld parsing anyway\n", length, counter,
				  ftell(FileIn) - sizeof(MRTheader));
		}
		if (length >= 2 * BGPSIZE) {
			largercounter++;
			trans_log("Length [%d] of BGPmessage %d is larger than"
				  " the maximum array size of 10k, at fpos:%ld, discarding\n",
			length, counter, ftell(FileIn) - sizeof(MRTheader));
			fseek(FileIn, length, SEEK_CUR);
			continue;
		}
		mrttime = ntohl(mrtHeader.timestamp);
		mrtHeader.timestamp = mrttime;
		/* printf("time: %lld %x\n",mrttime, mrttime); */
		/* return EXIT_FAILURE; */
		mrtHeader.subtype = ntohs(mrtHeader.subtype);
		/* Read file contents into buffer */
		num = fread(bgpmsg, length, 1, FileIn);
		if (num < 0) {
			trans_log("BGP msg fread failed!\n");
			return EXIT_FAILURE;
		}
		int 		asn_length;
		if (MRT2bmf(bgpmsg, &mrtMessage, &mrtHeader, &bmf, &asn_length)) {
			trans_log("Unable to parse Message\n");
			return EXIT_FAILURE;
		}
		inet_ntop(AF_INET, mrtMessage.peerIPAddress,
			  state_data.source_addr, ADDRESS_STRING_LEN);
		if (ttraveler_flag == 1) {
			if ((ret = add_to_seen_list(&seenl, state_data.source_addr, mrttime)) == -1)
				return EXIT_FAILURE;	/* XXX: free bmf->data */
		}
		state_data.source_asn_length = asn_length;
		state_data.dest_asn_length = state_data.monitor_asn_length = (mrtMessage.localAs <= 65535) ? 2 : 4;
		state_data.asn_size = asn_length;
		state_data.source_asn = mrtMessage.peerAs;
		inet_ntop(AF_INET, mrtMessage.localIPAddress, state_data.monitor_addr, ADDRESS_STRING_LEN);
		state_data.monitor_asn = mrtMessage.localAs;
		inet_ntop(AF_INET, mrtMessage.localIPAddress, state_data.dest_addr, ADDRESS_STRING_LEN);
		state_data.dest_asn = mrtMessage.localAs;
		/* call the XML module and spit the result to STDOUT */
		/* memset(xml_buf, '\0',max_len); */
		if (0 == BMF2XML(bmf, xml_buf, XMLBUFSIZ, (void *) &state_data)) {
			trans_log("BMF2XML failed\n");
			return EXIT_FAILURE;
		}
		fprintf(stdout, "%s\n", xml_buf);
		free(bmf->data);
		free(bmf);
	}
	if (num == 0) {
		if (!feof(FileIn)) {
			trans_log("fread failure, short object on msg num:%d\n", counter);
			return EXIT_FAILURE;
		}
	}
	return EXIT_SUCCESS;
}

int 
trans_process_table_dump_file()
{
	MRTheader 	mrtHeader;
	MRTmessage 	mrtMessage;
	int 		monitor_asn_len;
	Peer_Index_Table *peerIndexTable = NULL;
	counter = largercounter = 0;	/* reset the glob msg counter */
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
		counter++;

		/* read a single message */
		type = ntohs(mrtHeader.type);
		mrtHeader.type = type;

		length = ntohl(mrtHeader.length);
		if (length > BGPSIZE && length < 2 * BGPSIZE) {
			largercounter++;
			trans_log("Length [%d] of BGPmessage %d is larger than RFC, at"
			       "fpos:%ld parsing anyway\n", length, counter,
				  ftell(FileIn) - sizeof(MRTheader));
		}
		if (length >= 2 * BGPSIZE) {
			largercounter++;
			trans_log("Length [%d] of BGPmessage %d is larger than"
				  "the maximum array size of 10k, at fpos:%ld, discarding\n",
			length, counter, ftell(FileIn) - sizeof(MRTheader));
			fseek(FileIn, length, SEEK_CUR);
			continue;
		}
		mrtHeader.length = length;

		mrttime = ntohl(mrtHeader.timestamp);
		mrtHeader.timestamp = mrttime;
		mrtHeader.subtype = ntohs(mrtHeader.subtype);
		/* Read file contents into buffer */
		num = fread(bgpmsg, length, 1, FileIn);
		if (num < 0) {
			trans_log("BGP msg fread failed!\n");
			goto fail;
		}
		if (type == 12) {
			/* create the BMF structure */
			BMF 		bmf;
			bmf = createBMF(0, BMF_TYPE_TABLE_TRANSFER, NULL, 0);
			if (bmf == NULL) {
				trans_log("trans_processMRTTableDumpFile: Unable to create BMF");
				goto fail;
			}
			int 		asn_length;
			uint16_t 	seqNo;
			if (trans_MRT_processType_TableDump(bgpmsg, &mrtHeader,
				  &mrtMessage, &bmf, &asn_length, &seqNo)) {
				goto fail;
			}
			/* create the state data needed by the XML module */
			bgp_monitor_data state_data;
			inet_ntop(AF_INET, mrtMessage.peerIPAddress,
				state_data.source_addr, ADDRESS_STRING_LEN);
			state_data.source_asn_length = asn_length;
			state_data.source_asn = mrtMessage.peerAs;
			state_data.source_port = 179;
			strncpy(state_data.monitor_addr, monitor_addr, ADDRESS_STRING_LEN);
			state_data.monitor_asn_length = monitor_asn_len;
			state_data.monitor_asn = monitor_asn;
			state_data.monitor_port = monitor_port;
			/* In this case destination and monitor node is same */
			strncpy(state_data.dest_addr, monitor_addr, ADDRESS_STRING_LEN);
			state_data.dest_asn_length = monitor_asn_len;
			state_data.dest_asn = monitor_asn;
			state_data.dest_port = monitor_port;
			state_data.sequence = seqNo;
			state_data.asn_size = asn_length;

			/* call the XML module and spit the result to STDOUT */
			/* memset(xmlTestBuffer, '\0',max_len); */
			if (0 == BMF2XML(bmf, xml_buf, XMLBUFSIZ, (void *) &state_data)) {
				trans_log("BMF2XML failed\n");
				goto fail;
			}
			fprintf(stdout, "%s\n", xml_buf);
			destroyBMF(bmf);
		} else if (type == 13) {
			BMF            *bmfArray;
			MRTmessage    **mrtMessageArray;
			int 		entryCount = 0, i;
			int            *asn_lengthArray;
			unsigned int 	seqNo;
			if (trans_MRT_processType_TableDumpV2(bgpmsg, &mrtHeader,
				    &peerIndexTable, &entryCount, &bmfArray,
			      &mrtMessageArray, &asn_lengthArray, &seqNo)) {
				trans_log("trans_processMRTTableDumpFile:Unable to parse Message\n");
				goto fail;
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
					strncpy(state_data.monitor_addr, monitor_addr, ADDRESS_STRING_LEN);
					state_data.monitor_asn_length = monitor_asn_len;
					state_data.monitor_asn = monitor_asn;
					state_data.monitor_port = monitor_port;
					strncpy(state_data.dest_addr, monitor_addr, ADDRESS_STRING_LEN);
					state_data.dest_asn_length = monitor_asn_len;
					state_data.dest_asn = monitor_asn;
					state_data.dest_port = monitor_port;
					state_data.sequence = seqNo;
					state_data.asn_size = asn_lengthArray[i];
					/* call the XML module and spit the result to STDOUT */
					/* memset(xmlTestBuffer, '\0',max_len); */
					if (0 == BMF2XML(bmfArray[i], xml_buf, XMLBUFSIZ, (void *) &state_data)) {
						trans_log("BMF2XML failed\n");
						goto fail;
					}
					fprintf(stdout, "%s\n", xml_buf);
					free(mrtMessageArray[i]);
					free(bmfArray[i]->data);
					free(bmfArray[i]);
				}
				free(mrtMessageArray);
				free(asn_lengthArray);
			}
		} else {
			trans_log("trans_processMRTTableDumpFile: MRT type is incorrect!\n");
			goto fail;
		}

	}
	if (num == 0) {
		if (!feof(FileIn)) {
			trans_log("fread failure, short object on msg num:%d\n", counter);
			goto fail;
		}
	}
	return EXIT_SUCCESS;
fail:
	return EXIT_FAILURE;
}

int 
trans_MRT_processType_TableDump(uint8_t * rawMessage, MRTheader * mrtHeader,
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
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* Sequence Number */
	READ_2BYTES(tableDumpMsg.sequenceNumber, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
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
		trans_log("mrtThread, read TABLE DUMP message: prefix address convert "
			  "error!");
		return 1;
	}
	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* Prefix Length */
	tableDumpMsg.prefixLength = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* status */
	tableDumpMsg.status = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	if (tableDumpMsg.status != 1) {
		trans_log("MRT_processType_TableDump: status = %d but status field "
			  "should be 1", tableDumpMsg.status);
		return 1;
	}
	/* Originated Time */
	READ_4BYTES(tableDumpMsg.originatedTime, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
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
		trans_log("MRT_processType_TableDump: peer address conversion error!");
		return 1;
	}
	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* Peer AS */
	READ_2BYTES(tableDumpMsg.peerAs, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* Attribute Length */
	READ_2BYTES(tableDumpMsg.attributeLength, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu\n",
			  idx, mrtHeader->length);
		return 1;
	}
	/* BGP attributes */

	memmove(&tableDumpMsg.BGPAttr, &rawMessage[idx], tableDumpMsg.attributeLength);
	idx += tableDumpMsg.attributeLength;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDump: idx:%lu exceeded length:%lu",
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
	prefix_size = trans_packPrefix(tableDumpMsg.prefix, ipLen, tableDumpMsg.prefixLength, packed_prifix);
	/* Assigning all 1s to BGP Marker */
	for (j = 0; j < 16; j++) {
		(*bmf)->message[j] = ~0;
		bgpidx += 1;
	}
	/* Update length field of BGP message */
	const uint16_t 	bgp_length = htons(23 + tableDumpMsg.attributeLength + 1 + prefix_size);
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
	memmove(&(*bmf)->message[bgpidx], &tableDumpMsg.BGPAttr, tableDumpMsg.attributeLength);
	bgpidx += tableDumpMsg.attributeLength;
	/* Update length in NLRI field of BGP message */
	memmove(&(*bmf)->message[bgpidx], &tableDumpMsg.prefixLength, sizeof(tableDumpMsg.prefixLength));
	bgpidx += sizeof(tableDumpMsg.prefixLength);
	/* Update prefix field of BGP message */
	memmove(&(*bmf)->message[bgpidx], &packed_prifix, prefix_size);
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
trans_MRT_processType_TableDumpV2(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable,
	   int *entryCount, BMF ** bmfArray, MRTmessage *** mrtMessageArray,
				  int **asn_lengthArray, unsigned int *seqNo)
{

	switch (mrtHeader->subtype) {
		case PEER_INDEX_TABLE:
		if (trans_MRT_processType_TableDumpV2_PeerIndexTable(rawMessage, mrtHeader,
							    peerIndexTable))
			return EXIT_FAILURE;
		else
			return EXIT_SUCCESS;

	case RIB_IPV4_UNICAST:
	case RIB_IPV4_MULTICAST:
	case RIB_IPV6_UNICAST:
	case RIB_IPV6_MULTICAST:
		if (trans_MRT_processType_TableDumpV2_RIB_SUBTYPE(rawMessage, mrtHeader,
				       peerIndexTable, entryCount, bmfArray,
				   mrtMessageArray, asn_lengthArray, seqNo))
			return EXIT_FAILURE;
		else
			return EXIT_SUCCESS;
	case RIB_GENERIC:
		if (trans_MRT_processType_TableDumpV2_GENERIC_SUBTYPE(rawMessage,
						       mrtHeader, bmfArray))
			return EXIT_FAILURE;
		else
			return EXIT_SUCCESS;
	default:
		trans_log("Wrong subtype for TABLE DUMP V2: %d", mrtHeader->subtype);
		return EXIT_FAILURE;
	}
	return EXIT_SUCCESS;
}




int 
trans_MRT_processType_TableDumpV2_PeerIndexTable(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable)
{

	int 		idx = 0;
	int 		i;

	/* Create Peer Index Table */
	if (*peerIndexTable == NULL) {
		(*peerIndexTable) = malloc(sizeof(struct MRT_PEER_INDEX_TABLE_struct));
	} else {
		trans_log("MRT_processType_TableDumpV2_PeerIndexTable: "
			  "Second instance of PEER INDEX TABLE found.");
		return (1);
	}

	/* Collector BGP ID */
	READ_4BYTES((*peerIndexTable)->BGPSrcID, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			  "exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* View Name Length */
	READ_2BYTES((*peerIndexTable)->ViewNameLen, rawMessage[idx]);
	idx += 2;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			  "exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* View Name */
	if ((*peerIndexTable)->ViewNameLen != 0) {
		READ_2BYTES((*peerIndexTable)->ViewName, rawMessage[idx]);
		idx += 2;
		if (idx > mrtHeader->length) {
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
	}
	/* Peer Count */
	READ_2BYTES((*peerIndexTable)->PeerCount, rawMessage[idx]);
	idx += 2;
	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu exceeded "
			  "length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Allocate memory for peer entries */
	if ((*peerIndexTable)->PeerCount > 0) {
		(*peerIndexTable)->peerEntries = calloc
			((*peerIndexTable)->PeerCount, sizeof(Peer_Entry));

		if ((*peerIndexTable)->peerEntries == NULL) {
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: error in "
				  "allocating memory for peer entries\n");
			return 1;
		}
	}
	for (i = 0; i < (*peerIndexTable)->PeerCount; i++) {
		/* Peer Type */
		(*peerIndexTable)->peerEntries[i].peerType = rawMessage[idx];
		idx++;

		if ((*peerIndexTable)->peerEntries[i].peerType > 3) {
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: Wrong Peer "
				  "Type value:%lu", (*peerIndexTable)->peerEntries[i].peerType);
			return 1;
		}
		if (idx > mrtHeader->length) {
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu exceeded"
				  "length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Peer BGP ID */
		READ_4BYTES((*peerIndexTable)->peerEntries[i].peerBGPID, rawMessage[idx]);
		idx += 4;
		if (idx > mrtHeader->length) {
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
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
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
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
			trans_log("MRT_processType_TableDumpV2_PeerIndexTable: idx:%lu "
			   "exceeded length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
	}

	return (0);
}

int 
trans_MRT_processType_TableDumpV2_RIB_SUBTYPE(uint8_t * rawMessage,
		  MRTheader * mrtHeader, Peer_Index_Table ** peerIndexTable,
	   int *entryCount, BMF ** bmfArray, MRTmessage *** mrtMessageArray,
				 int **asn_lengthArray, unsigned int *seqNo)
{

	Mrt_Rib_Table 	mrtRibTable;
	int 		idx = 0, 	ribEntryHeaderLength = 0;
	int 		i;

	/* Check If Peer Index table is present. */
	if (*peerIndexTable == NULL) {
		trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: Peer Index Table "
			  "is not set");
		return 1;
	}
	/* Sequence Number */
	READ_4BYTES(mrtRibTable.SeqNumb, rawMessage[idx]);
	idx += 4;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu "
			  "exceeded length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Update Sequence Number */
	*seqNo = mrtRibTable.SeqNumb;

	/* Prefix Length */
	mrtRibTable.PrefixLen = rawMessage[idx];
	idx += 1;

	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
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
		trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
			  "length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* Entry Count */
	READ_2BYTES(mrtRibTable.EntryCount, rawMessage[idx]);
	idx += 2;
	if (idx > mrtHeader->length) {
		trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
			  "length:%lu\n", idx, mrtHeader->length);
		return 1;
	}
	/* store entry count value */
	*entryCount = mrtRibTable.EntryCount;

	/* Copy RIB Entry header */
	ribEntryHeaderLength = idx;

	/* Allocate memory for RIB entries */
	if (mrtRibTable.EntryCount > 0) {
		mrtRibTable.RibEntry = malloc
			(mrtRibTable.EntryCount * sizeof(Rib_Entry));
		if (mrtRibTable.RibEntry == NULL) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
				  "allocating memory for peer entries\n");
			return (1);
		}
	}
	/* Allocate memory for BMF array */
	if (mrtRibTable.EntryCount > 0) {
		*bmfArray = malloc
			(mrtRibTable.EntryCount * sizeof(BMF));

		if (*bmfArray == NULL) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
			       "allocating memory for BMF pointer array\n");
			return (1);
		}
	}
	/* Allocate memory for MrtMessage array */
	if (mrtRibTable.EntryCount > 0) {
		*mrtMessageArray = malloc
			(mrtRibTable.EntryCount * sizeof(MRTmessage *));

		if (*mrtMessageArray == NULL) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
			"allocating memory for mrtMessage pointer array\n");
			return (1);
		}
	}
	/* Allocate memory for asn_length array */
	if (mrtRibTable.EntryCount > 0) {
		*asn_lengthArray = malloc(mrtRibTable.EntryCount * sizeof(int));
		if (*asn_lengthArray == NULL) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
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
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				  "length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Originated Time */
		READ_4BYTES(mrtRibTable.RibEntry[i].OrigTime, rawMessage[idx]);
		idx += 4;

		if (idx > mrtHeader->length) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
				  "length:%lu\n", idx, mrtHeader->length);
			return 1;
		}
		/* Attribute Length */
		READ_2BYTES(mrtRibTable.RibEntry[i].AttrLen, rawMessage[idx]);
		idx += 2;

		if (idx > mrtHeader->length) {
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
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
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: idx:%lu exceeded "
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
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
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
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: "
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
			trans_log("MRT_processType_TableDumpV2_RIB_SUBTYPE: error in "
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
trans_MRT_processType_TableDumpV2_GENERIC_SUBTYPE(uint8_t * rawMessage,
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
	printf("trans_MRT_processType_TableDumpV2_GENERIC_SUBTYPE : %s\n", buffer);
	return 1;
}


int 
trans_packPrefix(uint8_t * prefixIpAddr, int ipVer, int prefixLen,
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
		trans_log("packPrefix: IPV6 \n");
		return (0);
	} else {
		trans_log("packPrefix: Wrong IP address version\n");
		return (0);
	}
}
