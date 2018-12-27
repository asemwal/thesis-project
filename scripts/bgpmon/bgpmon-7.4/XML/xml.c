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
 *  File:    xml.c
 *  Authors: M. Lawrence Weikum
 *  Date:    October 2013 - June 2014
 *
 *  Adapted from
 *  Authors: He Yan
 *           Pei-chun (Payne) Cheng
 *  Date:    Jun 22, 2008
 */


/* needed for queues*/
#include "../Queues/queue.h"

/* needed for TRUE/FALSE definitions */
#include "../Util/bgpmon_defaults.h"

/* needed for BMF types */
#include "../Util/bgpmon_formats.h"

/* needed for GMT_TIME_STAMP and ASCII_MESSAGES flags */
#include "../site_defaults.h"

/* needed for logging definitions */
#include "../Util/log.h"

/* needed for parsing bgp messages */
#include "../Peering/peersession.h"
#include "../Util/bgppacket.h"
#include "../Peering/bgpmessagetypes.h"

/* needed for getSessionString */
#include "../Labeling/label.h"

#include "xml.h"

/* needed for internal functions */
#include "xmlinternal.h"

/* For XML conversion */
#include "xml_gen.h"

/*needed for sequence number management */
#include "../Clients/clientscontrol.h"

/*needed for loop cache */
#include "../Chains/chains.h"

/*needed for copying xml messages for queues */
#include "../Util/xml_help.h"

/*#define DEBUG */


/*
 * Purpose: Entry function of xml thread
 * Input:
 * Output:
 * He Yan @ Jun 22, 2008
 * M. Lawrence Weikum @ October 13, 2013
 */
void           *
xmlThread(void *arg)
{
	log_err("XML thread started");
	char           *xml = malloc(XML_BUFFER_LEN);
	if (xml == NULL)
		log_fatal("failed to allocate XML buffer");
	XMLControls.shutdown = FALSE;

	QueueReader 	labeledQueueReader = createQueueReader(&labeledQueue, 1);
	if (labeledQueueReader == NULL) {
		log_msg("labeledQueueReader in xmlThread init function is NULL");
		return NULL;
	}
	QueueWriter 	xmlUQueueWriter = createQueueWriter(xmlUQueue);
	if (xmlUQueueWriter == NULL) {
		log_msg("xmlUQueueWriter in xmlThread init function is NULL");
		return NULL;
	}
	QueueWriter 	xmlRQueueWriter = createQueueWriter(xmlRQueue);
	if (xmlRQueueWriter == NULL) {
		log_msg("xmlRQueueWriter in xmlThread init function is NULL");
		return NULL;
	}
	while (XMLControls.shutdown == FALSE) {
		/* updating the last active time for this thread */
		XMLControls.lastAction = time(NULL);

		BMF 		bmf = NULL;
		int 		numUnreadItems = readQueue(labeledQueueReader);
		if (numUnreadItems == READER_SLOT_AVAILABLE) {
			log_err("xmlThread: FAILED READING FROM BMF QUEUE - READER SLOT AVAILABLE");
		} else if (numUnreadItems == 0) {
			log_msg("xmlThread: no items to be handled.");
			continue;
		}
		bmf = (BMF) labeledQueueReader->items[0];

		/* update time - make sure thread is alive */
		XMLControls.lastAction = time(NULL);



		int 		type = bmf->type;
		bgp_monitor_data state_data = {};
		if (type == BMF_TYPE_MSG_TO_PEER || type == BMF_TYPE_MSG_LABELED ||
		    type == BMF_TYPE_MSG_FROM_PEER || type == BMF_TYPE_TABLE_TRANSFER ||
		    type == BMF_TYPE_TABLE_START || type == BMF_TYPE_TABLE_STOP ||
		    type == BMF_TYPE_FSM_STATE_CHANGE) {
			/* now that we have a new BMF get the state data needed */
			Session_structp sp = getSessionByID(bmf->sessionID);
			strcpy(state_data.source_addr, sp->configInUse.remoteAddr);
			state_data.source_asn = sp->configInUse.remoteAS2;
			state_data.source_port = sp->configInUse.remotePort;
			state_data.source_asn_length = sp->fsm.ASNumlen;
			strcpy(state_data.monitor_addr, sp->configInUse.localAddr);
			strcpy(state_data.dest_addr, sp->sessionRealSrcAddr);
			state_data.dest_port = sp->configInUse.localPort;
			state_data.dest_asn = sp->configInUse.localAS2;
			state_data.dest_asn_length = sp->fsm.ASNumlen;
			state_data.sequence = ClientControls.seq_num;
			state_data.asn_size = sp->fsm.ASNumlen;
		}
		int 		len = 0;

		/* Convert BMF internal structure to XMl text string  */
		len = BMF2XML(bmf, xml, XML_BUFFER_LEN, (void *) &state_data);

		if (len > 0) {
			switch (bmf->type) {
				/* write out newly-generated messages and increment sequence number */
			case BMF_TYPE_MSG_TO_PEER:
			case BMF_TYPE_MSG_LABELED:
			case BMF_TYPE_MSG_FROM_PEER:
				{
					u_char         *xmlData = NULL;
					copyXMLmsg((void **) &xmlData, xml);
					if (xmlData == NULL) {
						log_err("Failed to copy xml message to buffer.");
						continue;
					}
					writeQueue(xmlUQueueWriter, xmlData);
					break;
				}
			case BMF_TYPE_TABLE_TRANSFER:
			case BMF_TYPE_TABLE_START:
			case BMF_TYPE_TABLE_STOP:
			case BMF_TYPE_FSM_STATE_CHANGE:
				{
					u_char         *xmlData = NULL;
					copyXMLmsg((void **) &xmlData, xml);
					if (xmlData == NULL) {
						log_err("Failed to copy xml message to buffer.");
						continue;
					}
					writeQueue(xmlRQueueWriter, xmlData);
					break;
				}

			case BMF_TYPE_CHAINS_STATUS:
			case BMF_TYPE_QUEUES_STATUS:
			case BMF_TYPE_SESSION_STATUS:
			case BMF_TYPE_MRT_STATUS:
			case BMF_TYPE_BGPMON_START:
			case BMF_TYPE_BGPMON_STOP:
			case BMF_TYPE_SKIP_AHEAD:
				{
					u_char         *UxmlData = NULL;
					u_char         *RxmlData = NULL;
					copyXMLmsg((void **) &UxmlData, xml);
					copyXMLmsg((void **) &RxmlData, xml);
					if (UxmlData == NULL) {
						log_err("Failed to copy xml message to buffer.");
						if (RxmlData != NULL) {
							free(RxmlData);
							RxmlData = NULL;
						}
						continue;
					}
					if (RxmlData == NULL) {
						log_err("Failed to copy xml message to buffer.");
						free(UxmlData);
						UxmlData = NULL;
						continue;
					}
					writeQueue(xmlUQueueWriter, UxmlData);
					writeQueue(xmlRQueueWriter, RxmlData);
					break;
				}

			default:
				{
					log_err("BMF2XML: unknown type!!!!!!!!!!!!!!!%u", bmf->type);
					break;
				}

			}
			/* increment sequence number, wrap around if necessary */
			if (ClientControls.seq_num != UINT_MAX)
				ClientControls.seq_num++;
			else
				ClientControls.seq_num = 0;
		}
		/* delete the session structure of closed session  */
		if (bmf->type == BMF_TYPE_FSM_STATE_CHANGE) {
			if (checkStateChangeMessage(bmf)) {
				destroySession(bmf->sessionID);
				log_err("Successfully destroy the session %d!", bmf->sessionID);
			}
		}
		/* Delete bmf structure  */
		destroyBMF(bmf);
	}
	destroyQueueReader(labeledQueueReader);
	destroyQueueWriter(xmlUQueueWriter);
	destroyQueueWriter(xmlRQueueWriter);
	log_err("XML thread exiting");

	return NULL;
}

/*
 * Purpose: launch xml converter thread, called by main.c
 * Input:   none
 * Output:  none
 * He Yan @ July 22, 2008
 * M. Lawrence Weikum @ October 13, 2013
 */
void 
launchXMLThread()
{
	int 		error;
	pthread_t 	XMLThreadID;

	if ((error = pthread_create(&XMLThreadID, NULL, xmlThread, NULL)) > 0)
		log_fatal("Failed to create XML thread: %s\n", strerror(error));

	XMLControls.xmlThread = XMLThreadID;
#ifdef DEBUG
	debug(__FUNCTION__, "Created XML thread!");
#endif

	if (pthread_detach(XMLThreadID))
		log_fatal("Error detaching XML thread.");
}

/*
 * Purpose: get the last action time of the XML thread
 * Input:
 * Output: last action time
 * Mikhail Strizhov @ Jun 25, 2009
 */
time_t 
getXMLThreadLastAction()
{
	return XMLControls.lastAction;
}

/*
 * Purpose: Intialize the shutdown process for the xml module
 * Input:  none
 * Output: none
 * Kevin Burnett @ July 10, 2009
 */
void 
signalXMLShutdown()
{
#ifdef DEBUG
	log_err("shutdown XML");
#endif
	XMLControls.shutdown = TRUE;
}

/*
 * Purpose: wait on all xml pieces to finish closing before returning
 * Input:  none
 * Output: none
 * Kevin Burnett @ July 10, 2009
 */
void 
waitForXMLShutdown()
{
	void           *status = NULL;
	/* wait for xml control thread exit */
	pthread_join(XMLControls.xmlThread, status);
}
