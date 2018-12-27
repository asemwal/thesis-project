/*
 *  Copyright (c) 2010 Colorado State University
 *
 *  Permission is hereby granted, free of charge, to any person
 *  obtaining a copy of this software and associated documentation
 *  files (the "Software"), to deal in the Software without
 *  restriction, including without limitation the rights to use,
 *  copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom
 *  the Software is furnished to do so, subject to the following
 *  conditions:
 *
 *  The above copyright notice and this permission notice shall be
 *  included in all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 *  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 *  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 *  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 *  OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 *  File:    xml_gen.c
 *  Authors: M. Lawrence Weikum
 *           Catherine Olschanowsky
 *  Date:    October 2013 - June 2014
 *
 */

#include "xml_gen.h"

/* needed for fprintf*/
#include <stdio.h>

/* Needed for generating skip ahead messages */
#include "../Queues/gen_skip_msg.h"

/* geolocation */
#include "../Util/geolocation.h"


/**Flags for an XML parsing error**/
static uint8_t 	parse_error = 0;
static uint16_t parse_error_length = 0;
static uint8_t 	previous_type = -1;

/*
 * Purpose: entry fucntion which converts all types of BMF messages to XML
 *          text representations
 * input:   bmf - our internal BMF message
 *          xml - pointer to the buffer used for conversion
 *          maxlen - max length of the buffer
 * output:  the length of generated xml string
 * M. Lawrence Weikum - October 2013
 */
int
BMF2XML(const BMF bmf, char *xml, const int maxlen, const void *monitorData)
{

	/* create the xml document */
	xmlDocPtr 	doc = genMSGDoc(bmf, monitorData);

	/* write the message to a string */
	xmlBuffer      *buffer = xmlBufferCreate();
	xmlNodeDump(buffer, NULL, doc->children, 0, 0);
	int 		xmlStrSize = snprintf(xml, maxlen, "%s", (char *) buffer->content);
	if (xmlStrSize < 0) {
		/* failed to copy over to the buffer - msg truncated */
		log_err("BMF2XML: Failed to copy the xml string to buffer!");
		return 0;
	}
	/* clean up space */
	if (buffer != NULL) {
		xmlBufferFree(buffer);
	}
	if (doc != NULL) {
		xmlFreeDoc(doc);
	}
	/* return the lenghth of the string */
	return xmlStrSize;
}

/*
 * Purpose: manages the process for creating the actual message
 * input:   bmf - our internal BMF message
 * output:  an xmlNodePtr that will be added to a document
 * M. Lawrence Weikum - October 2013
 */
xmlDocPtr
genMSGDoc(const BMF bmf, const void *state_data)
{


	/* create the document */
	xmlDocPtr 	doc = xmlNewDoc(BAD_CAST XML_DEFAULT_VERSION);
	if (doc == NULL) {
		log_err("testXmlwriterTree: Error creating the xml document tree\n");
		return NULL;
	}
	/* Creates BGP_MESSAGE node, name space and attribute */
	xmlNodePtr 	bgp_message_node = xmlNewNode(NULL, BAD_CAST "BGP_MONITOR_MESSAGE");
	xmlNewNs(bgp_message_node, BAD_CAST _XML_NS, BAD_CAST "xsi");
	xmlNewNs(bgp_message_node, BAD_CAST _MON_NS, NULL);
	xmlNsPtr 	bgp_ns = xmlNewNs(bgp_message_node, BAD_CAST _XFB_NS, BAD_CAST "bgp");
	xmlNewNs(bgp_message_node, BAD_CAST _NE_NS, BAD_CAST "ne");

	/* cast the data that we need from a void pointer to the right type */
	bgp_monitor_data *mon_data = (bgp_monitor_data *) state_data;

	/* set the root element of the document (needs to be done for all types */
	xmlDocSetRootElement(doc, bgp_message_node);

	/* specialize messages for each type */
	switch (bmf->type) {
	case BMF_TYPE_MSG_TO_PEER:
	case BMF_TYPE_MSG_FROM_PEER:
	case BMF_TYPE_MSG_LABELED:
	case BMF_TYPE_TABLE_TRANSFER:
		{
			/* monitor data */
			xmlAddChild(bgp_message_node, genSourceNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genDestNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);

			/* the message itself (bgp namespace) */
			xmlNodePtr 	bgp_node = xmlAddChild(bgp_message_node,
			    genBGPMSGNode(bmf, bgp_ns, mon_data->asn_size));

			/* octet message */
			xmlNodePtr 	octets = genOctetsNode(bmf);
			xmlAddChild(bgp_message_node, octets);
			if (parse_error) {
				xmlChar        *octetsStr = xmlXPathCastNodeToString(octets);
				log_err("ParseErrMsgOctets: %s", octetsStr);
			}
			if (bmf->type != BMF_TYPE_TABLE_TRANSFER) {
				/* labels */
				addMetaData(bmf, doc, bgp_message_node, bgp_node, mon_data);
			}
			break;
		}

		/* Table start messages */
	case BMF_TYPE_TABLE_START:
		{
			/* peering        */
			xmlAddChild(bgp_message_node, genSourceNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genDestNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);
			/* status          */
			xmlAddChild(bgp_message_node, genStatusNode(bmf, bmf->type));
			break;
		}
		/* Table sttop messages */
	case BMF_TYPE_TABLE_STOP:
		{
			/* peering        */
			xmlAddChild(bgp_message_node, genSourceNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genDestNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);
			/* status          */
			xmlAddChild(bgp_message_node, genStatusNode(bmf, bmf->type));
			break;
		}
		/* State change messages */
	case BMF_TYPE_FSM_STATE_CHANGE:
		{
			/* peering        */
			xmlAddChild(bgp_message_node, genSourceNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genDestNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);
			/* status          */
			xmlAddChild(bgp_message_node, genStatusNode(bmf, bmf->type));
			break;
		}
		/* Status messages */
	case BMF_TYPE_CHAINS_STATUS:
	case BMF_TYPE_QUEUES_STATUS:
	case BMF_TYPE_SESSION_STATUS:
	case BMF_TYPE_MRT_STATUS:
	case BMF_TYPE_BGPMON_START:
	case BMF_TYPE_BGPMON_STOP:
	case BMF_TYPE_CLIENT_SKIP_AHEAD:
		{
			/* monitor information */
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);
			/* status          */
			xmlAddChild(bgp_message_node, genStatusNode(bmf, bmf->type));
			break;
		}
	case BMF_TYPE_SKIP_AHEAD:
		{
			/* monitor information */
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);
			/* status  - skip ahead */
			xmlAddChild(bgp_message_node, genSkipAheadStatusNode(bmf));
			break;

		}
	case BMF_TYPE_MRT_TABLE_DUMP:
		{
			/* peering        */
			xmlAddChild(bgp_message_node, genSourceNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genDestNode(bmf, mon_data));
			xmlAddChild(bgp_message_node, genMonitorNode(bmf, mon_data));
			/* time           */
			xmlAddChild(bgp_message_node, genObservedTimeNode(bmf));
			/* sequence num   */
			xmlAddChild(bgp_message_node, genSequenceNumNode(bmf, mon_data));
			/* collection method */
			genCollectionMethodNode(bmf, bgp_message_node);

			break;
		}
	case BMF_TYPE_MRT_TABLE_DUMP_V2:
		{
			log_err("BMF2XML: Received type MRT_TABLE_DUMP_V2 - yet to be implemented");
			/*
			 * fprintf(stderr, "BMF2XML: Received type MRT_TABLE_DUMP_V2 - yet to be
			 * implemented\n");
			 */
			break;
		}
	default:
		{
			log_err("BMF2XML:genMSGDoc: unknown type! %u", bmf->type);
			break;
		}
	}

	return doc;
}

/**
 * Purpose: Will create the <COLLECTION> tag for XML messages based on the
 *          BMF type.
 * input:   bmf - our internal BMF message
 *          bgpNode - the current XML message
 * output:  None
 * M. Lawrence Weikum - October 2013
**/
void
genCollectionMethodNode(const BMF bmf, xmlNodePtr bgpNode)
{

	char           *live = "LIVE";
	char           *dump = "TABLE_DUMP";

	switch (bmf->type) {
	case BMF_TYPE_MSG_TO_PEER:
	case BMF_TYPE_MSG_LABELED:
	case BMF_TYPE_MSG_FROM_PEER:
		{
			xmlNewChildString(bgpNode, "COLLECTION", live);
			break;
		}
	case BMF_TYPE_TABLE_TRANSFER:
	case BMF_TYPE_TABLE_START:
	case BMF_TYPE_TABLE_STOP:
	case BMF_TYPE_FSM_STATE_CHANGE:
	case BMF_TYPE_MRT_TABLE_DUMP:
	case BMF_TYPE_MRT_TABLE_DUMP_V2:
		{
			xmlNewChildString(bgpNode, "COLLECTION", dump);
			break;
		}
	case BMF_TYPE_CHAINS_STATUS:
	case BMF_TYPE_QUEUES_STATUS:
	case BMF_TYPE_SESSION_STATUS:
	case BMF_TYPE_MRT_STATUS:
	case BMF_TYPE_BGPMON_START:
	case BMF_TYPE_BGPMON_STOP:
		{
			/* These are status messages and shouldn't  */
			/* have a collection part to them */
		}
	default:
		{
		}
	}
}

/*
 * Purpose: generate SOURCE node
 * input:   bmf - pointer to BMF structure, and pointer to monitor data
 * Output:  the new xml node
 *
 * Ex:
 *<SOURCE>
 *  <ADDRESS afi="1">202.167.228.44</ADDRESS>
 *  <PORT>179</PORT>
 *  <ASN2>10026</ASN2>
 *</SOURCE>
 */
xmlNodePtr
genSourceNode(const BMF bmf, bgp_monitor_data * mon_data)
{

	xmlNodePtr 	node = xmlNewNode(NULL, BAD_CAST "SOURCE");

	/* populate address */
	xmlNodePtr 	address = xmlNewChildString(node, "ADDRESS", mon_data->source_addr);
	int 		afi = get_afi(mon_data->source_addr);
	if (afi == -1) {
		/* handle rror */
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	xmlNewPropInt(address, "afi", afi);
	/* populate port */
	xmlNewChildInt(node, "PORT", mon_data->source_port);
	/* populate ASN2 or ASN4 */
	if (mon_data->source_asn_length == 2)
		xmlNewChildUnsignedInt(node, "ASN2", mon_data->source_asn);
	else
		xmlNewChildUnsignedInt(node, "ASN4", mon_data->source_asn);

	return node;
}

/*
 * Purpose: generate MONITOR node
 * input:   bmf - pointer to BMF structure, and pointer to monitor data
 * Output:  the new xml node
 *
 * Ex:
 *<MONITOR>
 *  <ADDRESS afi="1">202.167.228.44</ADDRESS>
 *  <PORT>179</PORT>
 *  <ASN2>10026</ASN2>
 *</MONITOR>
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr
genMonitorNode(const BMF bmf, bgp_monitor_data * mon_data)
{

	xmlNodePtr 	node = xmlNewNode(NULL, BAD_CAST "MONITOR");

	/* populate address */
	xmlNodePtr 	address = xmlNewChildString(node, "ADDRESS", mon_data->monitor_addr);
	int 		afi = get_afi(mon_data->monitor_addr);
	if (afi == -1) {
		/* handle error */
		xmlFreeNode(node);
		return NULL;
	}
	xmlNewPropInt(address, "afi", afi);
	/* populate port */
	xmlNewChildInt(node, "PORT", mon_data->monitor_port);
	/* populate ASN2 or ASN4 */
	if (mon_data->monitor_asn_length == 2)
		xmlNewChildUnsignedInt(node, "ASN2", mon_data->monitor_asn);
	else
		xmlNewChildUnsignedInt(node, "ASN4", mon_data->monitor_asn);

	return node;
}

/*
 * Purpose: generate DEST node
 * input:   bmf - pointer to BMF structure, and pointer to monitor data
 * Output:  the new xml node
 *
 * Ex:
 *<MONITOR>
 *  <ADDRESS afi="1">202.167.228.44</ADDRESS>
 *  <PORT>179</PORT>
 *  <ASN2>10026</ASN2>
 *</MONITOR>
 */
xmlNodePtr
genDestNode(const BMF bmf, bgp_monitor_data * mon_data)
{

	xmlNodePtr 	node = xmlNewNode(NULL, BAD_CAST "DEST");

	/* populate address */
	xmlNodePtr 	address = xmlNewChildString(node, "ADDRESS", mon_data->dest_addr);
	int 		afi = get_afi(mon_data->dest_addr);
	if (afi == -1) {
		/* handle error */
		xmlFreeNode(node);
		return NULL;
	}
	xmlNewPropInt(address, "afi", afi);
	/* populate port */
	xmlNewChildInt(node, "PORT", mon_data->dest_port);
	/* populate ASN2 or ASN4 */
	if (mon_data->dest_asn_length == 2)
		xmlNewChildUnsignedInt(node, "ASN2", mon_data->dest_asn);
	else
		xmlNewChildUnsignedInt(node, "ASN4", mon_data->dest_asn);

	return node;
}

/*
 * Purpose: generate OBSERVED_TIME node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 * Pei-chun Cheng @ Dec 20, 2008
 * He Yan @ Jun 22, 2008
 * Jason Bartlett @ 16 Sep 2010
 *
 * Ex:
 *<OBSERVED_TIME precision="false">
 *  <TIMESTAMP>1366748694</TIMESTAMP>
 *  <DATETIME>2013-04-23T20:24:54Z</DATETIME>
 *</OBSERVED_TIME>
 */
xmlNodePtr
genObservedTimeNode(const BMF bmf)
{

	xmlNodePtr 	time_node = xmlNewNode(NULL, BAD_CAST "OBSERVED_TIME");
	xmlNewPropString(time_node, "precision", "false");
	xmlNewChildUnsignedInt(time_node, "TIMESTAMP", bmf->timestamp);
	xmlNewChildGmtTime(time_node, "DATETIME", bmf->timestamp);
	return time_node;
}
/*
 * Purpose: generate OBSERVED_TIME node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 *
 * Ex:
 * <SEQUENCE_NUMBER>1</SEQUENCE_NUMBER>
 */
xmlNodePtr
genSequenceNumNode(const BMF bmf, bgp_monitor_data * state_data)
{

	xmlNodePtr 	sequence_node = xmlNewNode(NULL, BAD_CAST "SEQUENCE_NUMBER");
	char 		sequence_str[11] = {0};
	snprintf(sequence_str, 11, "%d", state_data->sequence);
	xmlNodeSetContent(sequence_node, BAD_CAST sequence_str);
	return sequence_node;
}

xmlNodePtr
genSkipAheadStatusNode(const BMF bmf)
{

	/* Getting the skip ahead information */
	SAM            *skipAheadInfo = (SAM *) bmf->data;

	/* Creating the skip ahead message for the node */
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	snprintf(buffer, XML_TEMP_BUFFER_LEN, "%lu messages were skipped in queue %s", skipAheadInfo->numMsgsSkipped, skipAheadInfo->queueName);

	/* Creating the XML node */
	xmlNodePtr 	status_node = xmlNewNode(NULL, BAD_CAST "STATUS");
	xmlNewPropString(status_node, "Author_Xpath", "/BGP_MONITOR_MESSAGE/MONITOR");
	/* Giving the type of SKIP_AHEAD */
	xmlNodePtr 	type_node = xmlNewNode(NULL, BAD_CAST "TYPE");
	xmlAddChild(status_node, type_node);
	xmlNodeSetContent(type_node, BAD_CAST "SKIP_AHEAD");
	/* Adding the mesage */
	xmlNodePtr 	msg_node = xmlNewNode(NULL, BAD_CAST "MESSAGE");
	xmlAddChild(status_node, msg_node);
	xmlNodeSetContent(msg_node, BAD_CAST buffer);

	/* Returning skip node */
	return status_node;

}

/*
 * Purpose: generate STATUS node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 *
 * Ex:
 * <STATUS Author_Xpath="/BGP_MONITOR_MESSAGE/MONITOR"> BGPMON_START </STATUS>
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr
genStatusNode(const BMF bmf, uint16_t type)
{

	xmlNodePtr 	status_node = xmlNewNode(NULL, BAD_CAST "STATUS");
	xmlNewPropString(status_node, "Author_Xpath", "/BGP_MONITOR_MESSAGE/MONITOR");
	xmlNodePtr 	type_node = xmlNewNode(NULL, BAD_CAST "TYPE");
	xmlAddChild(status_node, type_node);


	char           *msg = NULL;
	switch (type) {
	case BMF_TYPE_MSG_TO_PEER:
		msg = "MSG_TO_PEER";
		break;
	case BMF_TYPE_MSG_FROM_PEER:
		msg = "MSG_FROM_PEER";
		break;
	case BMF_TYPE_MSG_LABELED:
		msg = "MSG_LABELED";
		break;
	case BMF_TYPE_TABLE_TRANSFER:
		msg = "TABLE_TRANSFER";
		break;
	case BMF_TYPE_TABLE_START:
		msg = "TABLE_START";
		break;
	case BMF_TYPE_TABLE_STOP:
		msg = "TABLE_STOP";
		break;
	case BMF_TYPE_FSM_STATE_CHANGE:
		msg = "FSM_STATE_CHANGE";
		break;
	case BMF_TYPE_CHAINS_STATUS:
		msg = "CHAINS_STATUS";
		break;
	case BMF_TYPE_QUEUES_STATUS:
		msg = "QUEUES_STATUS";
		break;
	case BMF_TYPE_SESSION_STATUS:
		msg = "SESSION_STATUS";
		break;
	case BMF_TYPE_MRT_STATUS:
		msg = "MRT_STATUS";
		break;
	case BMF_TYPE_BGPMON_START:
		msg = "BGPMON_START";
		break;
	case BMF_TYPE_BGPMON_STOP:
		msg = "BGPMON_STOP";
		break;
	case BMF_TYPE_CLIENT_SKIP_AHEAD:
		msg = "CLIENT_SKIP_AHEAD";
		break;
	default:
		xmlFreeNode(status_node);
		return NULL;
	}

	/* writing to buffer */
	char           *status_str = NULL;
	int 		status_str_size = 0;
	if (bmfHasMessage(bmf)) {
		status_str_size = asprintf(&status_str, "%s %s", msg, bmf->message);
	} else {
		status_str_size = asprintf(&status_str, "%s", msg);
	}

	/* making sure we have something written to the buffer */
	if (status_str == NULL) {
		log_err("xml_gen: genStatus: tried to write status to buffer and failed to get memory.");
		xmlFreeNode(status_node);
		return NULL;
	} else {
		/* setting the content in the XML */
		xmlNodeSetContent(type_node, BAD_CAST status_str);

		/* returning */
		return status_node;
	}
}




/*
 * Purpose: generate a BGP Message node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr
genBGPMSGNode(const BMF bmf, const xmlNsPtr ns, const int asn_len)
{

	/* creating types that we could have */
	const char     *msg_strings[5];
	msg_strings[1] = "OPEN";
	msg_strings[2] = "UPDATE";
	msg_strings[3] = "NOTIFICATION";
	msg_strings[4] = "KEEP_ALIVE";

	/* make sure that we know the type */
	PBgpHeader 	hdr = (PBgpHeader) (bmf->message);
	if (hdr->type < 1 || hdr->type > 4) {
		log_err("XML genBGPMSGNode: Unable to recognize type\n");
		return NULL;
	}
	/* generate the XML common to all messages first */
	const uint16_t 	message_length = ntohs(*((uint16_t *) (bmf->message + 16)));
	uint16_t 	message_pos = 0;

	xmlNodePtr 	node = xmlNewNode(ns, BAD_CAST msg_strings[hdr->type]);
	if (node == NULL)
		log_fatal("Failed to alloc new node in genBGPMSGNode");	/* dsp@ exit for now for
									 * safety */
	xmlNewPropInt(node, "bgp_message_type", hdr->type);
	switch (hdr->type) {
		/* OPEN */
	case 1:
		{
			return node;
		}
		/* UPDATE */
	case 2:
		{
			u_char         *update = bmf->message + BGP_HEADER_LEN;
			message_pos += BGP_HEADER_LEN;

			/* resetting variables for parsing errors */
			parse_error = 0;
			parse_error_length = 0;

			/* withdraw section */
			const int 	wlen = ntohs(*((uint16_t *) update));
			int 		pos = 0;
			while (wlen > pos) {
				xmlNodePtr 	withd = genWithNode(update + 2 + pos, &pos, ns);
				if (parse_error) {
					if (withd != NULL) {
						xmlFreeNode(withd);
					}
					/* create parse error message */
					xmlNodePtr 	errMsg = genParseError((pos + parse_error_length), ns);

					/* adding to the node to the main */
					xmlAddChild(node, errMsg);

					/* alerting the logs that an error occured */
					log_err("Parse Error while making Wtih node!  Created respective xml message.");
					return NULL;
				}
				xmlAddChild(node, withd);
			}
			update = update + (2 + wlen);
			message_pos += 2 + wlen;

			/* attribute section */
			if (message_pos >= message_length) {
				return node;
			}
			pos = 0;
			const int 	alen = ntohs(*((uint16_t *) update));

			/* Generating the list of all attributes */
			xmlNodePtr     *pathAtts = NULL;
			xmlNodePtr     *expandedPathAtts = NULL;
			int 		pathAttCount = 0;

			/* resetting previous_type for parsing error catching */
			previous_type = -1;

			/* generating attribute section */
			while (alen > pos) {
				xmlNodePtr 	currentAtt =
				genAttNode(update + 2 + pos, &pos, ns, asn_len, alen);

				/* handling parsing errors */
				if (parse_error) {
					if (currentAtt != NULL) {
						xmlFreeNode(currentAtt);
					}
					/* remove other att nodes that were created */
					int 		pathCount;
					for (pathCount = 0; pathCount < pathAttCount; ++pathCount) {
						if (pathAtts[pathCount] != NULL) {
							xmlFreeNode(pathAtts[pathCount]);
						}
					}
					free(pathAtts);
					pathAtts = NULL;
					expandedPathAtts = NULL;

					/* create parse error message */
					log_err("Parse error. creating message with pos: %d and parse error length: %d\n", pos, parse_error_length);
					xmlNodePtr 	errMsg = genParseError((pos + parse_error_length), ns);

					/* adding to the node to the main */
					xmlAddChild(node, errMsg);

					/* alerting the logs that an error occured */
					log_err("Parse Error!  Created respective xml message.");
					/*
					 * xmlChar* parseNodeStr =
					 * xmlXPathCastNodeToString(errMsg);
					 */
					log_err("ParseErrPosition: %d", pos + parse_error_length);

					return node;
				}
				if (currentAtt == NULL) {
					continue;
				}
				/* adding attribute to the list of all attributes created */
				pathAttCount++;
				expandedPathAtts = realloc(pathAtts, pathAttCount * sizeof(xmlNodePtr));
				if (expandedPathAtts == NULL) {
					/* couldn't make the new memory */
					log_err("realloc failed for making path attributes");
					free(pathAtts);
					pathAtts = NULL;
					return NULL;
				} else {
					pathAtts = expandedPathAtts;
					pathAtts[pathAttCount - 1] = currentAtt;
				}
			}


			/* OUT OF WHILE LOOP */
			/* Ordering the path attributes by type and adding NLRI */

			/* ordering path attributes */
			if (pathAttCount > 1) {
				sortPathAtts(pathAtts, pathAttCount);
			}
			/* adding path attributes to node */
			int 		current;
			for (current = 0; current < pathAttCount; ++current) {
				xmlAddChildList(node, pathAtts[current]);
			}
			free(pathAtts);
			pathAtts = NULL;

			update = update + (2 + alen);
			message_pos += 2 + alen;

			/* NLRI section */
			if (message_pos >= message_length)
				return node;
			pos = 0;
			int 		nlri_len = message_length - 23 - wlen - alen;
			while (nlri_len > pos) {
				xmlNodePtr 	nlriNode = genNLRINode(update + pos, &pos, ns);
				if (nlriNode == NULL) {
					log_err("Parsing error in NLRI section!");
					parse_error = 1;
					return node;
				}
				xmlAddChild(node, nlriNode);
			}
			return node;
		}
	case 3:
	case 4:
		return node;
	}
	return NULL;
}


/**
 * Purpose: Will create the <PARSE_ERROR> tag for XML messages.  This will
 *          only be called if a parse error occurs, and this will just
 *          make a node with the position of the error.
 * input:   position - the position in the octet message where we failed
 *                     to parse.
 *          ns - the name space for the parse error tag
 * output:  the <PARSE_ERROR> tag
 * M. Lawrence Weikum - October 2013
**/
xmlNodePtr
genParseError(int position, const xmlNsPtr ns)
{
	xmlNodePtr 	parseError = xmlNewNode(ns, BAD_CAST "PARSE_ERROR");
	xmlNewPropInt(parseError, "position", position);
	return parseError;
}


/**
 * Purpose: Will sort all of the path attribute elements as we find that
 *          some messages don't have their path atributes sorted even though
 *          they should (as defined by the RFC).  Sort happens by thier type.
 *          Sort is a simple bubble sort and SHOULD BE ENHANCED LATER!  This
 *          will sort in the array given.
 * input:   pathAttrs - array of path attributes that have been created.
 *          array_size - the number of paht attributes found in the array.
 * output:  None
 * M. Lawrence Weikum - October 2013
**/
void
sortPathAtts(xmlNodePtr * pathAtts, const int array_size)
{
	int 		i;
	for (i = 0; i < array_size - 1; ++i) {
		int 		j        , min;
		xmlNodePtr 	temp;
		min = i;
		for (j = i + 1; j < array_size; ++j) {
			uint16_t 	jtype = atoi((char *)
					       pathAtts[j]->properties->next->next->next->next->children->content);
			uint16_t 	mintype = atoi((char *)
						 pathAtts[min]->properties->next->next->next->next->children->content);
			if (jtype < mintype)
				min = j;
		}
		temp = pathAtts[i];
		pathAtts[i] = pathAtts[min];
		pathAtts[min] = temp;
	}
}



/*
 * Purpose: generate a WITHDRAW node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 *
 * Ex:
 * <bgp:WITHDRAW afi="1">1.2.3.0/24</bgp:WITHDRAW>
 */
xmlNodePtr
genWithNode(const u_char * start, int *pos, const xmlNsPtr ns)
{
	xmlNodePtr 	node = xmlNewNode(ns, BAD_CAST "WITHDRAW");
	char 		prefix_str[XML_TEMP_BUFFER_LEN] = {0};
	int 		ret = getPrefixString(start, prefix_str, XML_TEMP_BUFFER_LEN, 1);
	if (ret == 0) {
		log_err("Error parsing withdraw node!");
		parse_error = 1;
		xmlFreeNode(node);
		return NULL;
	}
	*pos += ret;
	xmlNodeSetContent(node, BAD_CAST prefix_str);
	xmlNewPropInt(node, "afi", 1);
	return node;
}

/**
 * Purpose: Will generate the attributes for every path attribute, be it
 *          optional, trasitive, partial, extended, and type (number).
 * input:   node - the node to give the attributes to.
 *          flags - the octet flags that were given to the path attribute.
 *          type - the type (number) of the path attribute.
 * output:  None
 * M. Lawrence Weikum - October 2013
**/
void
genNodeAtts(xmlNodePtr node, const uint8_t flags, const uint8_t type)
{

	/* Bit masks to test for various attributes */
	const uint8_t 	opt_mask = 128;
	const uint8_t 	tran_mask = 64;
	const uint8_t 	part_mask = 32;
	const uint8_t 	ex_mask = 16;

	/* Testing for the optional make */
	if (flags & opt_mask)
		xmlNewPropString(node, "optional", "true");
	else
		xmlNewPropString(node, "optional", "false");

	/* Testing for transitive mask */
	if (flags & tran_mask)
		xmlNewPropString(node, "transitive", "true");
	else
		xmlNewPropString(node, "transitive", "false");

	/* Testing for partial mask */
	if (flags & part_mask)
		xmlNewPropString(node, "partial", "true");
	else
		xmlNewPropString(node, "partial", "false");

	/* Testing for extended length mask */
	if (flags & ex_mask)
		xmlNewPropString(node, "extended", "true");
	else
		xmlNewPropString(node, "extended", "false");

	/* Adding attribute type */
	xmlNewPropInt(node, "attribute_type", type);
}



/*
 * Purpose: generates attribute name as per attribute type
 * input:   the number of the attribute type
 * Output:  string of the attribute
 * M. Lawrence Weikum - October 2013
 */
char           *
getAttType(const uint8_t type)
{

	switch (type) {
		case 0:return "RESERVED";
	case 1:
		return "ORIGIN";
	case 2:
		return "AS_PATH";
	case 3:
		return "NEXT_HOP";
	case 4:
		return "MULTI_EXIT_DISC";
	case 5:
		return "LOCAL_PREF";
	case 6:
		return "ATOMIC_AGGREGATE";
	case 7:
		return "AGGREGATOR";
	case 8:
		return "COMMUNITY";
	case 9:
		return "ORIGINATOR_ID";
		/* case 10: return "CLUSTER_LIST"; */
		/* case 11: return "DPA";  */
		/* case 12: return "ADVERTISER";  */
		/* case 13: return "RCID_PATH / CLUSTER_ID"; */
	case 14:
		return "MP_REACH_NLRI";
	case 15:
		return "MP_UNREACH_NLRI";
	case 16:
		return "EXTENDED_COMMUNITIES";
	case 17:
		return "AS4_PATH";
	case 18:
		return "AS4_AGGREGATOR";
		/* case 19: return "SAFI";  */
		/* case 20: return "Connector"; */
		/* case 21: return "AS_PATHLIMIT"; */
		/* case 22: return "PMSI_TUNNEL"; */
		/* case 23: return "Tunnel Encapsulation"; */
		/* case 24: return "Traffic Engineering"; */
		/* case 25: return "IPv6 Address Specific Extended Community"; */
		/* case 26: return "AIGP"; */
		/* case 27: return "PE Distinguisher Labels"; */
		/* case 28: return "BGP Entropy Label Capatibility"; */
		/* 29-127 as unassigned */
		/* case 128: return "ATTR_SET"; */
		/* 129 - 254 unassigned */
		/* case 255: return "RESERVED FOR DEPLOYMENT"; */
	default:
		return "UNKNOWN_ATTRIBUTE";
	}
}

/*
 * Purpose: generate an ORIGIN
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * Ex:
 * <bgp:ORIGIN optional="false" transitive="true" partial="false"
 * extended="false" attribute_type="1">IGP</bgp:ORIGIN>
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 1 */
genOriginNode(xmlNodePtr node, const uint16_t length,
	      const u_char * start, uint16_t local_pos)
{
	uint8_t 	idx = 0;
	if (length != 1) {
		log_err("xml create origin, invalid length, size = %u", length);
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	idx = start[local_pos];
	local_pos++;
	char           *origin_type;
	switch (idx) {
	case 0:
		origin_type = "IGP";
		break;
	case 1:
		origin_type = "EGP";
		break;
	case 2:
		origin_type = "INCOMPLETE";
		break;
	default:
		origin_type = "OTHER";
		break;
	}
	xmlNodeSetContent(node, BAD_CAST origin_type);
	return node;
}

/*
 * Purpose: generate an AS_PATH or AS4_PATH node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace, as length
 * Output:  completed attribute node if attribute was valid
 *
 * Ex:
 * <bgp:AS_PATH optional="false" transitive="true" partial="false"
 * extended="false" attribute_type="2"><bgp:AS_SEQUENCE><bgp:ASN4>199432134
 * </bgp:ASN4><bgp:ASN4>1492454242</bgp:ASN4><bgp:ASN4>13700933</bgp:ASN4>
 * <bgp:ASN4>256184133</bgp:ASN4><bgp:ASN4>1073939521</bgp:ASN4>
 * <bgp:ASN4>830563776</bgp:ASN4><bgp:ASN4>135269347</bgp:ASN4><bgp:ASN4>134115
 * </bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH>
 * M. Lawrence Weikum - October 2013
 * Cathie - October 2013
 */
xmlNodePtr			/* type 2 and type 17 */
genASpathNode(xmlNodePtr asPathNode, const uint16_t length, const u_char * start,
	      uint16_t local_pos, const xmlNsPtr ns, const int asn_len)
{

	const char     *as_path_types[4];
	as_path_types[0] = "AS_SET";
	as_path_types[1] = "AS_SEQUENCE";
	as_path_types[2] = "AS_CONFED_SQUENCE";
	as_path_types[3] = "AS_CONFED_SET";

	if (length < 4) {
		log_err("xml create AS_PATH, invalid length");
		xmlFreeNode(asPathNode);
		parse_error = 1;
		return NULL;
	}
	while (local_pos < length) {
		const uint8_t 	segType = start[local_pos];
		local_pos++;
		const uint8_t 	segLength = start[local_pos];
		local_pos++;
		xmlNodePtr 	as_seg_node;
		if (segType > 4 || segType < 1) {
			log_err("xml create AS_PATH, invalid segment type: %u", segType);
			xmlFreeNode(asPathNode);
			parse_error = 1;
			return NULL;
		}
		as_seg_node = xmlNewNode(ns, BAD_CAST as_path_types[segType - 1]);
		xmlAddChild(asPathNode, as_seg_node);

		uint8_t 	idy;
		for (idy = 0; idy < segLength; idy += 1) {
			xmlNodePtr 	as_path_node;
			char 		asn_str  [XML_TEMP_BUFFER_LEN];
			if (asn_len == 2) {
				const uint16_t 	asn = ntohs(*((uint16_t *) (start + local_pos)));
				local_pos += asn_len;
				as_path_node = xmlNewNode(ns, BAD_CAST "ASN2");
				sprintf(asn_str, "%u", asn);
			} else if (asn_len == 4) {
				const uint32_t 	asn = ntohl(*((uint32_t *) (start + local_pos)));
				local_pos += asn_len;
				as_path_node = xmlNewNode(ns, BAD_CAST "ASN4");
				sprintf(asn_str, "%u", asn);
			} else {
				log_err("xml create as path, invalid asn length. Length: %u", asn_len);
				xmlFreeNode(asPathNode);
				parse_error = 1;
				return NULL;
			}
			xmlNodeSetContent(as_path_node, BAD_CAST asn_str);
			xmlAddChild(as_seg_node, as_path_node);
		}
	}
	return asPathNode;
}

/*
 * Purpose: generate a NEXT_HOP node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * Ex: <bgp:NEXT_HOP optional="false" transitive="true" partial="false"
 *     extended="false" attribute_type="3" afi="1">65.49.129.101</bgp:NEXT_HOP>
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 3 */
genNextHopNode(xmlNodePtr node, const uint16_t length,
	       const u_char * start, uint16_t local_pos)
{
	if (length != 4) {
		log_err("xml create next hop, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const u_char   *ipInt = (u_char *) (start + local_pos);
	local_pos += 4;
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	int 		buffer_str_len = getXMLAddressString(ipInt, buffer, XML_TEMP_BUFFER_LEN, 1);
	if (buffer_str_len == 0) {
		log_err("genNextHopNode: failed to generate address");
		parse_error = 1;
		xmlFreeNode(node);
		return NULL;
	}
	xmlNodeSetContent(node, BAD_CAST buffer);

	/* adding afi to the next hop */
	xmlNewPropInt(node, "afi", 1);

	return node;
}

/*
 * Purpose: generate a MED node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 4 */
genMEDNode(xmlNodePtr node, const uint16_t length, const u_char * start,
	   uint16_t local_pos)
{
	if (length != 4) {
		log_err("xml create multi exit discriminator, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const uint32_t 	pref = ntohl(*((uint32_t *) (start + local_pos)));
	local_pos += 4;
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	snprintf(buffer, XML_TEMP_BUFFER_LEN, "%u", pref);

	xmlNodeSetContent(node, BAD_CAST buffer);
	return node;
}

/*
 * Purpose: generate a LOCAL_PREF node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 5 */
genLocalPrefNode(xmlNodePtr node, const uint16_t length,
		 const u_char * start, uint16_t local_pos)
{
	if (length != 4) {
		log_err("xml create local pref, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const uint32_t 	pref = *((uint32_t *) (start + local_pos));
	local_pos += 4;
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	snprintf(buffer, XML_TEMP_BUFFER_LEN, "%u", pref);

	xmlNodeSetContent(node, BAD_CAST buffer);

	return node;
}

/*
 * Purpose: generate am AGGREGATOR node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 7 */
genAggregatorNode(xmlNodePtr node, const uint16_t length,
		  u_char * start, uint16_t local_pos, const xmlNsPtr ns)
{
	if (!(length == 6 || length == 8)) {
		log_err("xml create aggregator, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	uint32_t 	asn;
	char 		asn_str  [XML_TEMP_BUFFER_LEN] = {0};
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	xmlNodePtr 	as_node = NULL;
	if (length == 6) {
		asn = (uint32_t) ntohs(*((uint16_t *) (start + local_pos)));
		snprintf(asn_str, XML_TEMP_BUFFER_LEN, "%u", asn);
		local_pos += 2;
		as_node = xmlNewNode(ns, BAD_CAST "ASN2");
	} else if (length == 8) {
		asn = ntohl(*((uint32_t *) (start + local_pos)));
		snprintf(asn_str, XML_TEMP_BUFFER_LEN, "%u", asn);
		local_pos += 4;
		as_node = xmlNewNode(ns, BAD_CAST "ASN4");
	}
	int 		buffer_str_len = getXMLAddressString(start + local_pos, buffer, XML_TEMP_BUFFER_LEN, 1);
	if (buffer_str_len == 0) {
		log_err("genAggregatorNode: failed to generate the address string");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	local_pos += 4;

	xmlAddChild(node, as_node);
	xmlNodeSetContent(as_node, BAD_CAST asn_str);

	xmlNodePtr 	id_node = xmlNewNode(ns, BAD_CAST "IPv4_ADDRESS");
	xmlAddChild(node, id_node);
	xmlNodeSetContent(id_node, BAD_CAST buffer);
	xmlNewPropInt(id_node, "afi", 1);

	return node;
}

/*
 * Purpose: generate a COMMUNITY node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace, attribute flags,
 *          attribute type
 * Output:  completed attribute node if attribute was valid
 *
 * Ex:  <bgp:COMMUNITY optional="true" transitive="true" partial="false"
 *      extended="false" attribute_type="8"><bgp:ASN2>3043</bgp:ASN2>
 *      <bgp:VALUE>2</bgp:VALUE></bgp:COMMUNITY><bgp:COMMUNITY optional="true"
 *      transitive="true" partial="false" extended="false" attribute_type="8">
 *      <bgp:ASN2>3043</bgp:ASN2><bgp:VALUE>1001</bgp:VALUE></bgp:COMMUNITY>
 *      <bgp:COMMUNITY optional="true" transitive="true" partial="false"
 *      extended="false" attribute_type="8"><bgp:ASN2>3043</bgp:ASN2>
 *      <bgp:VALUE>6112</bgp:VALUE></bgp:COMMUNITY><bgp:COMMUNITY
 *      optional="true" transitive="true" partial="false" extended="false"
 *      attribute_type="8"><bgp:ASN2>3043</bgp:ASN2><bgp:VALUE>6300</bgp:VALUE>
 *      </bgp:COMMUNITY>
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 8 */
genCommunityNode(xmlNodePtr node, const uint16_t length, const u_char * start,
		 uint16_t local_pos, const xmlNsPtr ns, uint8_t flags,
		 const uint8_t type)
{
	if (length < 4 || length % 4 != 0) {
		log_err("xml create community, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const uint16_t 	num_commun = length / 4;
	uint16_t 	current_comm;
	xmlNodePtr 	toReturn = node;
	for (current_comm = 0; current_comm < num_commun; current_comm++) {
		const uint16_t 	asn = (uint16_t) ntohs(*((uint16_t *) (start + local_pos)));
		char 		asn_str  [XML_TEMP_BUFFER_LEN] = {0};
		snprintf(asn_str, XML_TEMP_BUFFER_LEN, "%u", asn);
		local_pos += 2;

		const uint16_t 	value = (uint16_t) ntohs(*((uint16_t *) (start + local_pos)));
		char 		value_str[XML_TEMP_BUFFER_LEN] = {0};
		snprintf(value_str, XML_TEMP_BUFFER_LEN, "%u", value);
		local_pos += 2;

		xmlNodePtr 	asn_node = xmlNewNode(ns, BAD_CAST "ASN2");
		xmlNodePtr 	value_node = xmlNewNode(ns, BAD_CAST "VALUE");
		xmlAddChild(node, asn_node);
		xmlAddChild(node, value_node);
		xmlNodeSetContent(asn_node, BAD_CAST asn_str);
		xmlNodeSetContent(value_node, BAD_CAST value_str);

		if (current_comm + 1 < num_commun) {
			xmlNodePtr 	tempNode = xmlNewNode(ns, BAD_CAST getAttType(type));
			genNodeAtts(tempNode, flags, type);
			xmlAddSibling(node, tempNode);
			node = tempNode;
		}
	}
	return toReturn;
}

/*
 * Purpose: generate an ORIGINATOR_ID node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 9 */
genOriginatorNode(xmlNodePtr node, const uint16_t length,
		  const u_char * start, uint16_t local_pos)
{
	if (length != 4) {
		log_err("xml create originator id, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	/* getting address */
	const uint32_t *ipInt = (uint32_t *) (start + local_pos);
	local_pos += 4;
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	int 		buffer_str_len = getXMLAddressString((u_char *) ipInt, buffer, XML_TEMP_BUFFER_LEN, 1);
	if (buffer_str_len == 0) {
		log_err("genOriginatorNode: failed to generate address");
		xmlFreeNode(node);
		return NULL;
	}
	xmlNodeSetContent(node, BAD_CAST buffer);

	/* adding afi to the originator id */
	xmlNewPropInt(node, "afi", 1);

	return node;
}

/*
 * Purpose: generate an CLUSTER_LIST node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 10 */
genClusterListNode(xmlNodePtr node, const uint16_t length,
		const u_char * start, uint16_t local_pos, const xmlNsPtr ns)
{
	if (length < 4) {	/* min # of bytes for one ipv4 is 4 */
		log_err("xml create cluster_list, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	if (length % 4 != 0) {
		log_err("xml create cluster_list, invalid length - not divisible");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	uint16_t 	current;
	const uint16_t 	tot = length / 4;
	for (current = 0; current < tot; current++) {

		const uint32_t *ipInt = (uint32_t *) (start + local_pos);
		local_pos += 4;

		char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
		int 		buffer_str_len = getXMLAddressString((u_char *) ipInt, buffer, XML_TEMP_BUFFER_LEN, 1);
		if (buffer_str_len == 0) {
			log_err("genClusterListNode: couldn't generate address");
			parse_error = 1;
			xmlFreeNode(node);
			return NULL;
		}
		xmlNodePtr 	cluster_id = xmlNewNode(ns, BAD_CAST "CLUSTER_ID");
		xmlNodeSetContent(cluster_id, BAD_CAST buffer);

		/* adding this to the main node */
		xmlAddChild(node, cluster_id);
	}
	return node;
}

/*
 * Purpose: generate an MP_REACH node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute node if attribute was valid
 *
 * Cathie - October 2013
 */
xmlNodePtr			/* type 14 */
genMPReachNode(xmlNodePtr node, const uint16_t length,
	       const u_char * start, uint16_t local_pos, const xmlNsPtr ns)
{


	/* Getting AFI and SAFI */
	const uint16_t 	afi = ntohs(*((uint16_t *) (start + local_pos)));
	local_pos += 2;
	if (!(afi == 1 || afi == 2)) {
		log_err("MPReachNode: Found Invalid AFI - %d", afi);
		parse_error = 1;
		xmlFreeNode(node);
		return NULL;
	}
	const uint8_t 	safi = start[local_pos];
	xmlNewPropInt(node, "safi", safi);
	local_pos += 1;

	/* Getting the next hop */
	const uint8_t 	nh_len = start[local_pos];
	local_pos += 1;
	xmlNodePtr 	nh = xmlAddChild(node, xmlNewNode(ns, BAD_CAST "MP_NEXT_HOP"));
	char 		str      [XML_TEMP_BUFFER_LEN] = {0};
	uint8_t 	ip_value[nh_len];
	memcpy(ip_value, start + local_pos, nh_len);
	local_pos += nh_len;
	if (afi == 1) {
		if (inet_ntop(AF_INET, ip_value, str, ADDR_MAX_CHARS) == NULL) {
			log_err("MP_REACH_NLRI - error parsing next hop IPv4");
			parse_error = 1;
			xmlFreeNode(node);
			return NULL;
		}
	} else if (afi == 2) {
		if (inet_ntop(AF_INET6, ip_value, str, ADDR_MAX_CHARS) == NULL) {
			log_err("MP_REACH_NLRI - error parsing next hop IPv6");
			parse_error = 1;
			xmlFreeNode(node);
			return NULL;
		}
	}
	xmlNodeSetContent(nh, BAD_CAST str);
	xmlNewPropInt(nh, "afi", afi);


	/* 1 reserved byte */
	local_pos += 1;

	/* NLRI Section */
	while (local_pos < length) {
		char 		address  [XML_TEMP_BUFFER_LEN] = {0};
		int 		bytesRead = getPrefixString(start + local_pos, address, XML_TEMP_BUFFER_LEN, afi);
		if (bytesRead == 0) {
			log_err("Unable to parse MP_REACH_NLRI NLRI");
			xmlFreeNode(node);
			parse_error = 1;
			return NULL;
		}
		local_pos += bytesRead;
		xmlNodePtr 	nlri = xmlAddChild(node, xmlNewNode(ns, BAD_CAST "MP_NLRI"));
		xmlNodeSetContent(nlri, BAD_CAST address);
		xmlNewPropInt(nlri, "afi", afi);
	}
	return node;
}

/*
 * Purpose: generate an MP_UNREACH node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute node if attribute was valid
 *
 * Cathie - October 2013
 */
xmlNodePtr			/* type 15 */
genMPUnreachNode(xmlNodePtr node, const uint16_t length,
		 const u_char * start, uint16_t local_pos, const xmlNsPtr ns)
{
	/* afi (2 octets) */
	const uint16_t 	afi = ntohs(*((uint16_t *) (start + local_pos)));
	local_pos += 2;
	/* safi (1 octet) */
	const uint8_t 	safi = start[local_pos];
	local_pos += 1;

	xmlNewPropInt(node, "safi", safi);

	/* MP_NLRI */
	do {
		char 		address  [XML_TEMP_BUFFER_LEN] = {0};
		int 		readBytes = getPrefixString(start + local_pos, address, XML_TEMP_BUFFER_LEN, afi);
		if (readBytes == 0) {
			log_err("Unable to parse MP_UNREACH_NLRI");
			xmlFreeNode(node);
			parse_error = 1;
			return NULL;
		}
		local_pos += readBytes;
		xmlNodePtr 	nlri = xmlAddChild(node, xmlNewNode(ns, BAD_CAST "MP_NLRI"));
		xmlNodeSetContent(nlri, BAD_CAST address);
		xmlNewPropInt(nlri, "afi", afi);
	} while (local_pos < length);
	return node;
}

/*
 * Purpose: generate an EXTENDED_COMMUNITIES node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute node if attribute was valid
 *
 *  iana.org/assignments/bgp-extended-communities/bgp-extended-communities.xml
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 16  */
genExtendCommNode(xmlNodePtr node, const uint16_t length, u_char * start,
		  uint16_t local_pos, const xmlNsPtr ns)
{

	if (length < 8) {
		log_err("xml create extended_communities, length to small.");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	if (length % 8 != 0) {
		log_err("xml create extended_communities, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const int 	num = length / 8;
	int 		i;
	for (i = 0; i < num; ++i) {
		const uint8_t 	type = *((uint8_t *) start + local_pos);
		local_pos++;
		const uint8_t 	subtype = *((uint8_t *) start + local_pos);
		local_pos++;

		switch (type) {
			/* 0x00 and 0x40 */
		case 0:	/* Two-octet AS Specific Extended Community */
		case 64:
			{

				xmlNewPropString(node, "extended_communities_type",
				"Two-Octet AS Specific Extended Community");
				switch (subtype) {
					/* Supported Types */
				case 2:
					xmlNewPropString(node, "extended_communities_subtype",
							 "Route Target");
					break;	/* rfc 4360 */
				case 3:
					xmlNewPropString(node, "extended_communities_subtype",
							 "Route Origin");
					break;	/* rfc4360 */
				case 5:
					xmlNewPropString(node, "extended_communities_subtype",
						  "OSPF Domain Identifier");
					break;	/* rfc4577 */
				case 8:
					xmlNewPropString(node, "extended_communities_subtype",
						     "BGP Data Collection");
					break;	/* rfc4384 */
				case 9:
					xmlNewPropString(node, "extended_communities_subtype",
							 "Source AS");
					break;	/* rfc6514 */
					/* Unsupported Types */
					/*
					 * case 10: xmlNewPropString(node,
					 * "extended_communities_subtype",
					 */
					/* "Layer 2 VPN Identifier");break; */
					/*
					 * case 16: xmlNewPropString(node,
					 * "extended_communities_subtype",
					 */
					/* "Cisco VPN-Distinguisher");break; */
				default:
					xmlNewPropString(node, "extended_communities_subtype",
							 "Unknown");
					break;
				}
				const uint16_t 	global_admin =
				(uint16_t) ntohs(*((uint16_t *) (start + local_pos)));
				char 		global_ad_str[XML_TEMP_BUFFER_LEN] = {0};
				snprintf(global_ad_str, XML_TEMP_BUFFER_LEN, "%u", global_admin);
				local_pos += 2;

				char 		local_admin[XML_TEMP_BUFFER_LEN] = {0};
				uint8_t 	idx;
				for (idx = 0; idx < 4; idx++) {
					sprintf(local_admin + (idx * 2), "%02X", start[local_pos]);
					local_pos++;
				}
				xmlNodePtr 	asn2 = xmlNewNode(ns, BAD_CAST "ASN2");
				xmlNodeSetContent(asn2, BAD_CAST global_ad_str);
				xmlNodePtr 	value = xmlNewNode(ns, BAD_CAST "VALUE");
				xmlNodeSetContent(value, BAD_CAST local_admin);
				xmlAddChild(node, asn2);
				xmlAddChild(node, value);
				return node;
			}

			/* 0x01 */
		case 1:	/* IPv4 Address Specific Extended Community */
		case 65:
			{
				xmlNewPropString(node, "extended_communities_type",
				"IPv4 Address Specific Extended Community");
				switch (subtype) {
					/* Supported */
				case 2:
					xmlNewPropString(node,
							 "extended_communities_subtype", "Route Target");
					break;
				case 3:
					xmlNewPropString(node,
							 "extended_communities_subtype", "Route Origin");
					break;
					/* Unsupported */
					/* case 5: xmlNewPropString(node,  */
					/*
					 * "extended_communities_subtype", "OSPF Domain
					 * Identifier");break;
					 */
					/* case 7: xmlNewPropString(node,  */
					/* "extended_communities_subtype", "OSPF Router ID");break; */
					/* case 10: xmlNewPropString(node,  */
					/*
					 * "extended_communities_subtype", "Layer 2 VPN
					 * Identifier");break;
					 */
					/* case 11: xmlNewPropString(node,  */
					/*
					 * "extended_communities_subtype", "VRF Route
					 * Import");break;
					 */
					/* case 16: xmlNewPropString(node,  */
					/*
					 * "extended_communities_subtype", "Cisco VPN
					 * Distinguisher");break;
					 */
				default:
					xmlNewPropString(node,
							 "extended_communities_subtype", "Unknown");
					break;
				}
				char 		global_admin[XML_TEMP_BUFFER_LEN] = {0};
				int 		global_admin_str_len = getXMLAddressString(start + local_pos, global_admin, XML_TEMP_BUFFER_LEN, 1);
				if (global_admin_str_len == 0) {
					log_err("genExtendCommNode: couldn't get global admin address");
					parse_error = 1;
					xmlFreeNode(node);
					return NULL;
				}
				local_pos += 4;

				/* making hex */
				char 		local_admin[XML_TEMP_BUFFER_LEN] = {0};
				uint8_t 	idx;
				for (idx = 0; idx < 2; idx++) {
					sprintf(local_admin + (idx * 2), "%02X", start[local_pos]);
					local_pos++;
				}

				xmlNodePtr 	ip = xmlNewNode(ns, BAD_CAST "IPv4_ADDRESS");
				xmlNodeSetContent(ip, BAD_CAST global_admin);
				xmlNewPropInt(ip, "afi", 1);	/* dsp@ patch for failed
								 * schema validation */
				xmlNodePtr 	value = xmlNewNode(ns, BAD_CAST "VALUE");
				xmlNodeSetContent(value, BAD_CAST local_admin);
				xmlAddChild(node, ip);
				xmlAddChild(node, value);
				return node;
			}
			/* 0x02 and 0x42 */
		case 2:	/* Four-octet AS Specific Extended Community */
		case 66:
			{
				xmlNewPropString(node, "extended_communities_type",
				"Four-Octet AS Specific Extended Community");
				switch (subtype) {
					/* Supported */
					/* rfc5668 */
				case 2:
					xmlNewPropString
						(node, "extended_communities_subtype", "Route Target");
					break;

					/* rfc5668 */
				case 3:
					xmlNewPropString
						(node, "extended_communities_subtype", "Route Origin");
					break;
					/* Unsupported */
					/* case 4: xmlNewPropString(node,  */
					/*
					 * "extended_communities_subtype", "Transitive
					 * Generic");break;
					 */
					/*
					 * case 5: xmlNewPropString(node,
					 * "extended_communities_subtype",
					 */
					/* "OSPF Domain Identifier");break; */
					/*
					 * case 9: xmlNewPropString(node,
					 * "extended_communities_subtype",
					 */
					/* "Source AS");break; */
					/*
					 * case 16: xmlNewPropString(node,
					 * "extended_communities_subtype",
					 */
					/* "Cisco VPN Distinguisher");break; */
				default:
					xmlNewPropString(node,
							 "extended_communities_subtype", "Unknown");
					break;
				}
				const uint32_t 	global_admin =
				(uint32_t) ntohl(*((uint32_t *) (start + local_pos)));
				char 		global_ad_str[XML_TEMP_BUFFER_LEN] = {0};
				snprintf(global_ad_str, XML_TEMP_BUFFER_LEN, "%u", global_admin);
				local_pos += 4;

				char 		local_admin[XML_TEMP_BUFFER_LEN] = {0};
				uint8_t 	idx;
				for (idx = 0; idx < 2; idx++) {
					sprintf(local_admin + (idx * 2), "%02X", start[local_pos]);
					local_pos++;
				}
				xmlNodePtr 	asn4 = xmlNewNode(ns, BAD_CAST "ASN4");
				xmlNodeSetContent(asn4, BAD_CAST global_ad_str);
				xmlNodePtr 	value = xmlNewNode(ns, BAD_CAST "VALUE");
				xmlNodeSetContent(value, BAD_CAST local_admin);
				xmlAddChild(node, asn4);
				xmlAddChild(node, value);
				return node;

			}
			/* 0x03 and 0x43 */
		case 3:	/* Opaque Extended Community */
		case 67:
			{
				xmlNewPropString
					(node, "extended_communities_type", "Opaque Extended Community");
				/* putting hte names in first */

				switch (subtype) {
				case 0:
				case 1:
				case 2:
					xmlNewPropString
						(node, "extended_communities_subtype", "Unassigned");
					break;
				case 6:
					xmlNewPropString
						(node, "extended_communities_subtype", "OSPF Route Type");
					break;
				case 11:
					xmlNewPropString
						(node, "extended_communities_subtype", "Color");
					break;
				case 12:
					xmlNewPropString
						(node, "extended_communities_subtype",
					"Encapsulation Extended Community");
					break;
				default:
					xmlNewPropString
						(node, "extended_communities_subtype", "Unknown");
					break;
				}
				/* dealing with the parsing */
				char 		value    [XML_TEMP_BUFFER_LEN] = {0};
				uint8_t 	idx;
				for (idx = 0; idx < 6; idx++) {
					sprintf(value + (idx * 2), "%02X", start[local_pos]);
					local_pos++;
				}
				xmlNodePtr 	val = xmlNewNode(ns, BAD_CAST "VALUE");
				xmlNodeSetContent(val, BAD_CAST value);
				xmlAddChild(node, val);

				return node;
			}

			/* 0x04 and 0x44 */
		case 4:	/* QoS Marking */
		case 68:
			/* 0x05 */
		case 5:	/* CoS Capability */
			/* 0x06 and 0x08 */
		case 6:	/* BGP Extended Communities Type - extended,
				 * transitive */
		case 8:
			/* 0x80 */
		case 128:	/* BGP Extended Communities Type -
				 * Experimental Use */

		default:
			return genUnknownExtendCommNode(node, length, start, ns);
		}
	}
	return node;
}


/*
 * Purpose: generate an AS4_AGGREGATOR node
 * input:   an attribute node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute node if attribute was valid
 *
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr			/* type 17 */
genAS4AggregatorNode(xmlNodePtr node, const uint16_t length,
		     u_char * start, uint16_t local_pos, const xmlNsPtr ns)
{


	if (length != 8) {
		log_err("xml create as4_aggregator, invalid length");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	const uint32_t 	asn = ntohl(*((uint32_t *) (start + local_pos)));
	local_pos += 4;
	char 		asn_str  [XML_TEMP_BUFFER_LEN] = {0};
	snprintf(asn_str, XML_TEMP_BUFFER_LEN, "%u", asn);
	char 		buffer   [XML_TEMP_BUFFER_LEN];
	int 		buffer_len = getXMLAddressString(start + local_pos, buffer, XML_TEMP_BUFFER_LEN, 1);
	if (buffer_len == 0) {
		log_err("genAS4AggregatorNode: couldn't get Address String!");
		parse_error = 1;
		xmlFreeNode(node);
		return NULL;
	}
	local_pos += 4;

	xmlNodePtr 	as_node = xmlNewNode(ns, BAD_CAST "ASN4");
	xmlAddChild(node, as_node);
	xmlNodeSetContent(as_node, BAD_CAST asn_str);

	xmlNodePtr 	id_node = xmlNewNode(ns, BAD_CAST "IPv4_ADDRESS");
	xmlAddChild(node, id_node);
	xmlNodeSetContent(id_node, BAD_CAST buffer);
	xmlNewPropInt(id_node, "afi", 1);

	return node;
}



/*
 * Purpose: generate an HEX_STRING node for the EXTENDED_COMMUNITIES node.
 * input:   an EXTENDED_COMMUNITEIS node, length of the attribute, hex string,
 *          current posistion in hex string, namespace
 * Output:  completed attribute with  hex string representation of the
 *          unknown extended community attribute
 * M. Lawrence Weikum - October 2013
 */
xmlNodePtr
genUnknownExtendCommNode(xmlNodePtr node,
	     const uint16_t length, const u_char * start, const xmlNsPtr ns)
{

	xmlNewPropString(node, "extended_communities_type", "UNKNOWN");
	char 		hex_string[XML_TEMP_BUFFER_LEN] = {0};
	uint16_t 	idx;
	for (idx = 0; idx < length + 1; idx++) {
		sprintf(hex_string + (idx * 2), "%02X", start[idx]);
	}
	xmlNodePtr 	hs = xmlNewNode(ns, BAD_CAST "HEX_STRING");
	xmlNodeSetContent(hs, BAD_CAST hex_string);
	xmlAddChild(node, hs);
	return node;
}




/*
 * Purpose: generate an ATTRIBUTE node
 * input:   start - a pointer to the attribute in a message
 *          pos - a pointer to the position in the message
 *          ns  - the namespace
 * Output:  the new xml node

 *
 * Ex:
 * M. Lawrence Weikum - October 2013
 * Cathie - Octobe 2013
 */
xmlNodePtr
genAttNode(u_char * start, int *pos, const xmlNsPtr ns, int asn_len, int alen)
{
	/* copying the starting postion incase we need it in unkown attribute creation */
	int 		starting_pos = *pos;

	/* get the attribute flags, type, and length out of the message */
	const uint8_t 	ex_mask = 16;
	uint8_t 	local_pos = 0;
	const uint8_t 	flags = start[local_pos];
	local_pos++;
	const uint8_t 	type = start[local_pos];
	local_pos++;
	uint16_t 	length;
	uint8_t 	extended = 0;
	if (flags & ex_mask) {	/* tests if the extended length bit is set */
		length = ntohs(*((uint16_t *) (start + local_pos)));
		local_pos += 2;
		*pos += 2;
		extended = 1;
	} else {
		length = (uint8_t) start[local_pos];
		local_pos += 1;
		*pos += 1;
	}

	/* increases the end pos so the document creator knows to skip over this  */
	/* attribute and is able to start parsing the next */
	*pos += 2 + length;

	/* create the node along with the attributes from the flags field */
	xmlNodePtr 	node = xmlNewNode(ns, BAD_CAST getAttType(type));
	genNodeAtts(node, flags, type);


	/* switching previous types for error checking */
	uint8_t 	prev_type = previous_type;
	previous_type = type;


	switch (type) {
		/* reserved - throw an error */
	case 0:{
			log_err("Error parsing attribute: Type 0!");
			xmlFreeNode(node);
			parse_error = 1;
			return NULL;
		}
		/* origin type */
	case 1:
		return genOriginNode(node, length, start, local_pos);
		/* as path type */
	case 2:
		return genASpathNode(node, length, start, local_pos, ns, asn_len);
		/* next hop type */
	case 3:
		return genNextHopNode(node, length, start, local_pos);
		/* med type */
	case 4:
		return genMEDNode(node, length, start, local_pos);
		/* local pref type is a 4 octet unsigned integer */
	case 5:
		return genLocalPrefNode(node, length, start, local_pos);
		/* attomic aggregate type */
	case 6:
		return node;	/* nothing to do */
		/* aggregator type */
	case 7:
		return genAggregatorNode(node, length, start, local_pos, ns);
		/* community */
	case 8:
		return genCommunityNode(node, length, start, local_pos, ns,
					flags, type);
		/* originator id */
	case 9:
		return genOriginatorNode(node, length, start, local_pos);
		/* cluster list */
	case 10:
		return genClusterListNode(node, length, start, local_pos, ns);
		/* MP_REACH */
	case 14:
		return genMPReachNode(node, length, start, local_pos, ns);
		/* MP_UNREACH */
	case 15:
		return genMPUnreachNode(node, length, start, local_pos, ns);
		/* Extended communities - rfc 4360 */
	case 16:
		return genExtendCommNode(node, length, start, local_pos, ns);
		/* AS4_PATH */
	case 17:
		return genASpathNode(node, length, start, local_pos, ns, 4);
		/* AS4_AGGREGATOR - rfc 4893 */
	case 18:
		return genAS4AggregatorNode(node, length, start, local_pos, ns);
		/* PMSI Tunnel */
		/* case 22://TODO */
		/* Tunnel Encapsulation */
		/* case 23://TODO */
		/* Traffic Eng */
		/* case 24://TODO */
		/* IPv6 addr specificiations extended community */
		/* case 25://TODO */
		/* PE Dist */
		/* case 27://TODO */
		/* BGP Entropy */
		/* case 28://TODO */
		/* ADDR_SET */
		/* case 128://TODO */

	default:
		{
			/* adjusting attribute length so it coveres the flags, type,and lenth. */
			/* remember, the length is 2xlong if flags have the extended-length bit */
			int 		totLen = length;
			totLen += extended ? 4 : 3;

			/* Making sure the length is correct */
			if ((*pos - starting_pos != totLen)) {
				log_err("Error making hex string for unkown attibute - StartPos: %u totLen: %u, MaxAttLen: %u", starting_pos, totLen, alen);
				xmlFreeNode(node);
				parse_error = 1;
				return NULL;
			}
			/* making sure a malformed mpreach didn't casue us to get off */
			if (prev_type == 14) {
				log_err("Error parsing BGP message - possible malformed MP_REACH_NLRI");
				xmlFreeNode(node);
				parse_error = 1;
				return NULL;
			}
			/* creating hex for the attribute */
			/* // 2*totLen b/c each octet = 2 hex chars, +1 for the ending */
			int 		idx;
			char 		hex_string[2 * totLen + 1];
			/* hex_string[2*totLen+1] = '\0'; */
			memset(hex_string, '\0', 2 * totLen + 1);
			for (idx = 0; idx < totLen; ++idx) {
				sprintf(hex_string + (idx * 2), "%02X", start[idx]);
			}
			xmlNodeSetContent(node, BAD_CAST hex_string);

			if (type != 20) {	/* this is just to shut off
						 * the unknonw attribute
						 * messages for Connector
						 * Attribute //TODO MAKE THIS
						 * PRSING LATER FOR THE NEXT
						 * VERSION OF BGPMON - WILL
						 * NEED TO ADD TO THE XSD. */
				log_err("Unknown Attribute: %s", hex_string);
			}
			return node;
		}
	}
}
/*
 * Purpose: generate an NLRI node
 * input:   bmf - pointer to BMF structure
 * Output:  the new xml node
 *
 * Ex:
 * <bgp:NLRI afi="1">1.2.3.0/24</bgp:NLRI>
 */
xmlNodePtr
genNLRINode(const u_char * start, int *pos, const xmlNsPtr ns)
{
	xmlNodePtr 	node = xmlNewNode(ns, BAD_CAST "NLRI");
	char 		prefix_str[XML_TEMP_BUFFER_LEN] = {0};
	int 		ret = getPrefixString(start, prefix_str, XML_TEMP_BUFFER_LEN, 1);
	if (ret == 0) {
		log_err("Failed to parse NLRI node!");
		xmlFreeNode(node);
		parse_error = 1;
		return NULL;
	}
	*pos += ret;
	xmlNodeSetContent(node, BAD_CAST prefix_str);
	xmlNewPropInt(node, "afi", 1);
	return node;
}
/*
 * Purpose: generate the OCTET_MESSAGE node
 * input:   BMF message
 * Output:  the XML node
 */
xmlNodePtr
genOctetsNode(const BMF bmf)
{
	xmlNodePtr 	octet_node = NULL;
	PBgpHeader 	hdr = NULL;
	uint32_t 	bgpMsgLen = 0;

	/* Due to the labels at the end of BMF,  */
	/* we needs to know the real length of raw bgp update */
	hdr = (PBgpHeader) (bmf->message);
	/* bgpType   = hdr->type; */
	bgpMsgLen = getBGPHeaderLength(hdr);

	/* OCTET_MSG node */
	octet_node = xmlNewNode(NULL, BAD_CAST "OCTET_MESSAGE");
	char 		buffer   [9000] = {0};
	int 		i;
	for (i = 0; i < bgpMsgLen; i++)
		sprintf(buffer + (2 * i), "%02X", (uint8_t) bmf->message[i]);
	xmlNodeSetContent(octet_node, BAD_CAST buffer);

	return octet_node;
}

void
addMetaData(const BMF bmf, xmlDocPtr doc, xmlNodePtr msgNode, xmlNodePtr bgp, bgp_monitor_data *mon_state)
{
	/* only labeled messages get a METADATA tag */
	/*XXX dsp@: why? i'm changing that. now the loop below will check */
	/*if (bmf->type != BMF_TYPE_MSG_LABELED) {
		return;
	}*/
	/* get ready to walk the labels */
	/* +16 below makes it land to the length of the BGP message after the marker */
	const uint16_t 	message_length = ntohs(*((uint16_t *) (bmf->message + 16)));
	u_char         *labels = (u_char *) (bmf->message + message_length);

	/* use xpath to find all nodes that can have labels */
	/* in xpath 2 we will get these results in document order */
	/* therefore they will line up with the labels */
	char           *xpathExpr = "//bgp:UPDATE/bgp:WITHDRAW | //bgp:MP_NLRI | //bgp:NLRI";
	char           *pathNodeStringPre;	/* bgp:UPDATE */
	char           *pathNodeStringPost;	/* bgp:WITHDRAW */
	char 		pathNodeString[XML_TEMP_BUFFER_LEN];
	xmlXPathContextPtr xpathCtx;
	xmlXPathObjectPtr xpathObj;
	xpathCtx = xmlXPathNewContext(doc);
	xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS);
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);

	/* this set should be all labelled prefixes */
	xmlNodeSetPtr 	nodes = xpathObj->nodesetval;
	int 		size = (nodes) ? nodes->nodeNr : 0;
	int 		i;
	xmlChar        *value;
	/* move that over here (instead of the loop) cause we need the metadata tag even when there are no labels */
	xmlNodePtr 	node = xmlNewNode(NULL, BAD_CAST "METADATA");
	for (i = 0; i < size && bmf->type == BMF_TYPE_MSG_LABELED; i++) {
		int 		label = *labels;
		labels += 1;
		char           *label_str;

		if (nodes->nodeTab[i]->type == XML_ELEMENT_NODE) {
			char           *name = (char *) nodes->nodeTab[i]->name;
			if (strcmp(name, "WITHDRAW") == 0) {
				pathNodeStringPre = "//bgp:UPDATE[\"";
				pathNodeStringPost = "\"]/bgp:WITHDRAW";
			} else if (strcmp(name, "MP_NLRI")) {
				if (strcmp((char *) nodes->nodeTab[i]->parent->name, "MP_REACH")) {
					pathNodeStringPre = "//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"";
					pathNodeStringPost = "\"]/MP_NLRI";
				} else {
					pathNodeStringPre = "//bgp:UPDATE/bgp:MP_UNREACH[MP_NLRI\"";
					pathNodeStringPost = "\"]/MP_NLRI";
				}
			} else if (strcmp(name, "NLRI")) {
				pathNodeStringPre = "//bgp:UPDATE/bgp:MP_REACH";
				pathNodeStringPost = "]/NLRI";
			} else {
				pathNodeStringPre = "ERROR";
				pathNodeStringPost = "ERROR";
			}
			value = xmlNodeGetContent(nodes->nodeTab[i]);
			sprintf(pathNodeString, "%s%s%s", pathNodeStringPre, value,
				pathNodeStringPost);
			free(value);
			value = NULL;

			switch (label) {
			case BGPMON_LABEL_NULL:
				label_str = "NULL";
				break;
			case BGPMON_LABEL_WITHDRAW:
				label_str = "WITH";
				break;
			case BGPMON_LABEL_WITHDRAW_DUPLICATE:
				label_str = "DUPW";
				break;
			case BGPMON_LABEL_ANNOUNCE_NEW:
				label_str = "NANN";
				break;
			case BGPMON_LABEL_ANNOUNCE_DUPLICATE:
				label_str = "DANN";
				break;
			case BGPMON_LABEL_ANNOUNCE_DPATH:
				label_str = "DPATH";
				break;
			case BGPMON_LABEL_ANNOUNCE_SPATH:
				label_str = "SPATH";
				break;
			default:
				label_str = "UNKNOWN";
			}
			/* create a metadata node */
			xmlNodePtr 	path = xmlAddChild(node, xmlNewNode(NULL, BAD_CAST "NODE_PATH"));
			xmlNodePtr 	lNode = xmlAddChild(node, xmlNewNode(NULL, BAD_CAST "ANNOTATION"));
			
			xmlNodeSetContent(path, BAD_CAST pathNodeString);
			xmlNodeSetContent(lNode, BAD_CAST label_str);
		}
	}
	xmlNodePtr 	destloc = xmlAddChild(node, xmlNewNode(NULL, BAD_CAST "DESTINATION_GEOLOCATION"));
	xmlNodePtr 	sourceloc = xmlAddChild(node, xmlNewNode(NULL, BAD_CAST "SOURCE_GEOLOCATION"));
	xmlNodeSetContent(destloc, BAD_CAST geodb_resolve(&geolist, mon_state->dest_addr));
	xmlNodeSetContent(sourceloc, BAD_CAST geodb_resolve(&geolist, mon_state->source_addr));
	xmlAddChild(msgNode, node);
	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);
	return;
}

/*
 * Purpose: generate the string version of a prefix
 * input:   a pointer to the raw data 2 bytes len, var bytes data
 *          a pointer to space to put the string
 *          the afi
 * Output:  the number of bytes read
 * M. Lawrence Weikum April 2014
 */
int
getPrefixString(const u_char * prefix, char *prefix_str,
		const uint32_t prefix_str_len, const int afi)
{

	uint8_t 	prefix_octs = 0;
	uint8_t 	bits = 0;
	char 		str      [XML_TEMP_BUFFER_LEN] = {0};
	uint8_t 	prefix_value[16] = {0};

	/* Get prefix string */
	bits = prefix[0];
	prefix_octs = (bits + 7) >> 3;

	/* 1 to get to over the length oct.` */
	memcpy(prefix_value, &prefix[1], prefix_octs);

	/* IPv4  */
	if (afi == 1) {
		if (inet_ntop(AF_INET, prefix_value, str, ADDRESS_STRING_LEN) == NULL) {
			log_err("getPrefixString: could not convert IPv4 prefix");
			/* strcat(prefix_str, "0"); */
			return 0;
		}
	}
	/* IPV6 */
	else if (afi == 2) {
		if (inet_ntop(AF_INET6, prefix_value, str, ADDRESS_STRING_LEN) == NULL) {
			log_err("getPrefixString: could not convert IPv6 prefix");
			/* strcat(prefix_str, "0"); */
			return 0;
		}
	} else {
		log_err("getPrefixString: could not convert prefix with unknown afi");
		/* strcat(prefix_str, "0"); */
		return 0;
	}

	/* Printing the address and mask to the buffer */
	int 		numCouldWrite = snprintf(prefix_str, prefix_str_len, "%s/%d", str, bits);

	/* Checking for overflow */
	if (numCouldWrite > prefix_str_len) {
		log_err("getPrefixString: could not write address to buffer - buffer too small");
		return 0;
	}
	return prefix_octs + 1;
}

/*
 * Purpose: generate the string version of a address
 * input:   a pointer to the raw data 2 bytes len, var bytes data
 *          a pointer to space to put the string
 *          the afi
 * Output:  the length of the string
 */
int
getXMLAddressString(const u_char * addr, char *addr_str,
		    const uint32_t addr_str_len, const int afi)
{

	char 		str      [XML_TEMP_BUFFER_LEN] = {0};
	uint8_t 	addr_value[16] = {0};

	/* IPv4  */
	if (afi == 1) {
		memcpy(addr_value, addr, 4);
		if (inet_ntop(AF_INET, addr_value, str, ADDRESS_STRING_LEN) == NULL) {
			log_err("getXMLAddressString: could not convert IPv4 address");
			/* strcat(addr_str, "0"); */
			return 0;
		}
		/* IPV6 */
	} else if (afi == 2) {
		memcpy(addr_value, addr, 16);
		if (inet_ntop(AF_INET6, addr_value, str, ADDRESS_STRING_LEN) == NULL) {
			log_err("getXMLAddressString could not convert IPv6 address");
			return 0;
		}
	} else {
		log_err("getXMLAddressString: coudl not convert address with unknown afi.");
		return 0;
	}

	/* Writing the address to the buffer */
	int 		numCouldWrite = snprintf(addr_str, XML_TEMP_BUFFER_LEN, "%s", str);

	/* Checking for overflow */
	if (numCouldWrite > addr_str_len) {
		log_err("getXMLAddressString: could not write address to buffer - buffer too small");
		return 0;
	}
	/* returning amount + null character */
	return numCouldWrite + 1;
}
