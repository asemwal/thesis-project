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
 *  File: gen_skip_msg.c
 *  Authors: M. Lawrnece Weikum
 *  Date: June 18, 2014
 */



#include "gen_skip_msg.h"



/*
 * Purpose: If a reader is skipped ahead, this will generate the appropriate
 *          response depending on the queueName (and the data it handels).
 *          For XML queues, this will generate a char* of XML that is a
 *          Skip Ahead message.  For other queues, this will create a BMF
 *          with type SKIP_AHEAD so XML may be generated and dispersed later.
 * input:   queueName - name of the queue - item from queue struct
 *          numSkipped - number of messages skipped to place into item
 *          return pointer - location of pointer you would like the resulting
 *                           item to be stored in
 * output:  0 if successful
 *          1 if memory allocation was unsuccessful
 *          2 if the name of the queue wasn't recognized
 * M. Lawrence Weikum - June 19, 2014
 */
const int
genSkipAheadMessage(char *queueName, const long numSkipped, void **returnPointer)
{


	/* Cannot do a switch statement on a string in C, but we can do strcmp's */

	/* Finding if we need to return an XML message */
	if (strcmp(queueName, XML_U_QUEUE_NAME) == 0 ||
	    strcmp(queueName, XML_R_QUEUE_NAME) == 0) {

		/* Making message for skip ahead for xml node */
		char           *skipmsg = NULL;
		int 		slen = asprintf(&skipmsg, "Skipped %ld messages in queue %s.", numSkipped, queueName);
		if (skipmsg == NULL || slen < 0) {
			log_err("genSkipAheadMessage: Couldn't print num messages skipped into string");
			return 1;
		}
		/* Creating the BMF for the XML module */
		BMF 		skipBMF = createBMF(0, BMF_TYPE_CLIENT_SKIP_AHEAD, NULL, 0);
		bgpmonMessageAppend(skipBMF, skipmsg, slen + 1);

		/* creating state data for BMF2XML creation  */
		/* - commented out pieces not needed for this message */
		bgp_monitor_data state_data;
		Session_structp sp = getSessionByID(skipBMF->sessionID);
		strcpy(state_data.source_addr, sp->configInUse.remoteAddr);
		/* state_data.source_asn = sp->configInUse.remoteAS2; */
		/* state_data.source_port = sp->configInUse.remotePort; */
		/* state_data.source_asn_length = sp->fsm.ASNumlen; */
		strcpy(state_data.monitor_addr, sp->configInUse.localAddr);
		strcpy(state_data.dest_addr, sp->sessionRealSrcAddr);
		/* state_data.dest_port = sp->configInUse.localPort; */
		/* state_data.dest_asn = sp->configInUse.localAS2; */
		/* state_data.dest_asn_length = sp->fsm.ASNumlen; */
		state_data.sequence = ClientControls.seq_num;
		state_data.asn_size = sp->fsm.ASNumlen;

		/* translate to XML */
		char           *skipXMLp = (char *) calloc(XML_BUFFER_LEN, sizeof(char));
		int 		len = BMF2XML(skipBMF, skipXMLp, XML_BUFFER_LEN, (void *) &state_data);

		/* Cleaning up memory used for creating the message */
		free(skipmsg);
		skipmsg = NULL;

		/* cleaning BMF */
		destroyBMF(skipBMF);

		/* Making sure the message was created successfully */
		if (len < 1) {
			log_err("genSkipAheadMessage: Failed to copy xml message from buffer!");
			return 1;
		}
		/* Setting return value */
		*returnPointer = (void *) skipXMLp;
	}
	/* Finding if we need to return a BMF message */
	else if (strcmp(queueName, MRT_QUEUE_NAME) == 0 ||
		 strcmp(queueName, LABEL_QUEUE_NAME) == 0 ||
		 strcmp(queueName, PEER_QUEUE_NAME) == 0) {

		/* making structure to give to BMF  */
		/* - don't need memset b/c we're setting all values in just a few lines */
		SAM            *dataStruct = malloc(sizeof(SAM));
		if (dataStruct == NULL) {
			log_err("genSkipAheadMessage: Could not get memory to make bmfSkipAhead structure.");
			return 1;
		}
		/* assigning data */
		dataStruct->queueName = queueName;
		dataStruct->numMsgsSkipped = numSkipped;

		/* Creating BMF */
		BMF 		toReturn = createBMFWithData(0, BMF_TYPE_SKIP_AHEAD, dataStruct);
		if (toReturn == NULL) {
			log_err("genSkipAheadMessage: Call to createBMFWithData failed.");
			return 1;
		}
		/* Setting return value */
		*returnPointer = (void *) toReturn;
	}
	/* Unknown Queue type */
	else {
		log_err("genSkipAheadMessage: Did not recognize Queue Name: %s", queueName);
		return 2;
	}

	/* All is well */
	return 0;
}
