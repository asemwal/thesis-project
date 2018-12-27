/*
 *  Copyright (c) 2010 Colorado State University
 *
 *  Permission is hereby granted, free of charge, to any person
 *      obtaining a copy of this software and associated documentation
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
 *    File: chaininstance.c
 *    Authors:  M. Lawrence Weikum
 *    Date: April, 2014
 * Implementation of chaining BGPMons together in order to achieve scalability.
 */

/* externally visible structures and functions for clients */
#include "chains.h"

/* internal structures and functions for launching chains */
#include "chaininstance.h"

/* required for logging functions */
#include "../Util/log.h"

/* needed for ADDR_MAX_CHARS */
#include "../site_defaults.h"

/* required for TRUE/FALSE and chainXMLBufferLength  */
#include "../Util/bgpmon_defaults.h"

/* needed for address management  */
#include "../Util/address.h"

/* required for writing to the XML queue */
#include "../Queues/queue.h"

/* needed for writern and readn socket operations */
#include "../Util/unp.h"

/* needed for function getMsgIdSeq */
#include "../XML/xml.h"

/* needed for read_xml_message from socket */
#include "../Util/backlogUtil.h"

/* needed for XML_BUFFER_LEN */
#include "../XML/xmlinternal.h"

/* needed for malloc and free */
#include <stdlib.h>

/* needed for strncpy */
#include <string.h>

/* needed for system error codes */
#include <errno.h>

/* needed for system types such as time_t */
#include <sys/types.h>

/* needed for time function */
#include <time.h>

/* needed for pthread related functions */
#include <pthread.h>

/* needed for UINT_MAX */
#include <limits.h>

/*#define DEBUG */




/*
 * Purpose: Create a chain data structure
 * Input:  address, update port, RIB port, enabled flag and retry interval.
 * Output: 1 on error, 0 on success
 * Updated by: M. Lawrence Weikum April, 2014
 */
int
createChainStruct(char *addr, int Uport, int Rport,
		  int enabled, int connectRetryInterval)
{

	/* find a empty slot for this new chain */
	int 		i;
	for (i = 0; i < MAX_CHAIN_IDS; i++) {
		if (Chains[i] == NULL)
			break;
	}

	/* if the number of chains exceeds MAX_CHAIN_IDS, return -1 */
	if (i == MAX_CHAIN_IDS) {
		log_err("Unable to create new chain for %s:  max chains exceeded", addr);
		return 1;
	}
	/* Returns a new chain or NULL if not enough memory. */
	/* Chain_structp chain = malloc(sizeof( struct ChainStruct)); */
	Chain_structp 	chain = malloc(sizeof(struct ChainStruct));
	memset(chain, 0, sizeof(struct ChainStruct));
	if (chain == NULL) {
		log_err("createChain: malloc failed");
		return 1;
	}
	/* set the structure values */
	chain->chainID = i;

	/* configuration settings */
	strncpy(chain->addr, addr, ADDR_MAX_CHARS);
	chain->Uport = Uport;
	chain->Rport = Rport;
	chain->enabled = enabled;
	chain->connectRetryInterval = connectRetryInterval;
	chain->initialConnectRetryInterval = connectRetryInterval;

	/* thread control */
	chain->deleteChain = FALSE;
	chain->reconnectFlag = FALSE;
	chain->runningFlag = FALSE;
	chain->lastAction = 0;

	/* socket related fields */
	chain->Usocket = -1;
	chain->Userrno = 0;
	chain->UconnectRetryCounter = 0;
	chain->UconnectionState = chainStateIdle;

	chain->Rsocket = -1;
	chain->Rserrno = 0;
	chain->RconnectRetryCounter = 0;
	chain->RconnectionState = chainStateIdle;

	/* up time, peer reset counter, number of messages */
	chain->UestablishedTime = 0;
	chain->UlastDownTime = 0;
	chain->UresetCounter = 0;
	chain->UmessageRcvd = 0;

	chain->RestablishedTime = 0;
	chain->RlastDownTime = 0;
	chain->RresetCounter = 0;
	chain->RmessageRcvd = 0;

	/* periodic check for configuration changes */
	/* chain->periodicCheckInt = THREAD_CHECK_INTERVAL; */
	/* temp change to 5 seconds */
	chain->periodicCheckInt = 5;

	/* xml queue writer */
	chain->UxmlQueueWriter = NULL;
	chain->RxmlQueueWriter = NULL;

	/* Backlogs - to be set by updateThread and ribThread */
	chain->uBacklog = NULL;
	chain->rBacklog = NULL;

	/* setting itself */
	Chains[i] = chain;

#ifdef DEBUG
	log_msg("Created chain structure for %s and assigned id %d", addr, i);
#endif

	return 0;
}





/*
 * Purpose: entry function of a chain thread.  Will create other chain threads
 *          and will join them if the chain is deleted or BGPmon closes
 *
 * Input:  pointer to a chain structure
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void           *
mainChainThread(void *arg)
{

	Chain_structp 	chain = arg;
	log_msg("thread started for chain %d to %s Update port %d, RIB port %d",
		chain->chainID, chain->addr, chain->Uport, chain->Rport);

	/* create the xml queue writers */
	chain->UxmlQueueWriter = createQueueWriter(xmlUQueue);
	if (chain->UxmlQueueWriter == NULL) {
		log_err("chain thead %d failed to create Update Queue Writer. chain thread exiting.", chain->chainID);
		chain->runningFlag = FALSE;
		pthread_exit(NULL);
	}
	chain->RxmlQueueWriter = createQueueWriter(xmlRQueue);
	if (chain->RxmlQueueWriter == NULL) {
		log_err("chain thead %d failed to create RIB Queue Writer. chain thread exiting.", chain->chainID);
		chain->runningFlag = FALSE;
		pthread_exit(NULL);
	}
	/* set the running flag */
	chain->runningFlag = TRUE;
	updateLastAction(chain);


	/* creating threads */
	pthread_t 	threads[2];
	short 		continueCreation = 1;
	if (pthread_create(&threads[0], NULL, updateThread, (void *) chain)) {
		continueCreation = 0;
	}
	if (continueCreation && pthread_create(&threads[1], NULL, ribThread, (void *) chain)) {
		continueCreation = 0;
	}
	/* Seeing if we need to do some cleanup work or if we can release the barrier */
	if (!continueCreation) {
		cleanupChainStruct(chain);
		pthread_exit(NULL);
	}
	/* joining all threads */
	int 		i;
	for (i = 0; i < 2; ++i) {
		if (pthread_join(threads[i], NULL)) {
			log_err("Failed to join thread for chain %d", chain->chainID);
		}
	}

	/* if the chain is to be destroyed, wipe out everything */
	if (chain->deleteChain == TRUE) {
		destroyChain(chain);
	}
	/* otherwise just cleanup the chain structure */
	else {
		cleanupChainStruct(chain);
	}

	pthread_exit(NULL);
}



/*
 * Purpose: entry function of a thread to handle the update stream of a chain.
 *          Will establish a connection, handle reconnects, read from the
 *          socket to the backlog, and read messages out of the backlog to the
 *          XML queue until the chain is disabled.
 *
 * Input:  pointer to a chain structure
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void           *
updateThread(void *arg)
{
	Chain_structp 	chain = arg;
	log_msg("Update thread started for chain %d", chain->chainID);

	while (chain->enabled == TRUE) {

		/* If we're connected, run a read from the socket and put into backlog */
		if (chain->UconnectionState == chainStateConnected) {

			/* Going to mange the select and read from the socket now. */
			if (manageUConnection(chain)) {
				log_msg("Chain %d update thread manageUConn failed", chain->chainID);

				/* closing the socket so we will reconnect later */
				closeUChain(chain);
			}
			/* Going to read from the backlog and put msgs into the queue */
			else if (handleBacklogRead(chain, chain->uBacklog, chain->UxmlQueueWriter)) {
				log_err("error transferring xml from update backlog to queue writer for chain %d", chain->chainID);
				/* closing the socket and backlog */
				closeUChain(chain);
			}
		} else {
			log_msg("Chain %d update thread connecting", chain->chainID);

			/* establish the connection again */
			if (establishUConnection(chain)) {
				closeUChain(chain);
				/* connection failed, sleep and try again */
				log_err("Failed to connect to update port for chain %d. Sleeping",
					chain->chainID);
				if (handleThreadSleep(chain)) {
					/* sleep failed for some reason */
					/* TODO decide what to do then. continue? */
				}
				continue;
			}
			log_msg("Chain %d update thread connected", chain->chainID);

			/* reconnect was successful.  Can reset the retry interval */
			resetChainSleepInterval(chain);

			/* creating the backlog */
			if (createUBacklog(chain)) {
				log_err("Failed to create backlog for update chain %d",
					chain->chainID);
				closeUChain(chain);
			}
		}
	}


	log_msg("closing read update socket thread for chain %d", chain->chainID);
	closeUChain(chain);

	/* returning */
	pthread_exit(NULL);

}

/*
 * Purpose: entry function of a thread to handle the RIB stream of a chain.
 *          Will establish a connection, handle reconnects, read from the
 *          socket to the backlog, and read messages out of the backlog to the
 *          XML queue until the chain is disabled.
 *
 * Input:  pointer to a chain structure
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void           *
ribThread(void *arg)
{
	Chain_structp 	chain = arg;
	log_msg("RIB thread started for chain %d", chain->chainID);

	while (chain->enabled == TRUE) {

		/* If we're connected, run a read from the socket and put into backlog */
		if (chain->RconnectionState == chainStateConnected) {

			/* Going to mange the select and read from the socket now. */
			if (manageRConnection(chain)) {
				log_msg("Chain %d rib thread manageUConn failed", chain->chainID);

				/* closing the socket so we will reconnect later */
				closeRChain(chain);
			}
			/* Going to read from the backlog and put msgs into the queue */
			else if (handleBacklogRead(chain, chain->rBacklog, chain->RxmlQueueWriter)) {
				log_err("error transferring xml from rib backlog to queue writer for chain %d", chain->chainID);
				/* closing the socket and backlog */
				closeRChain(chain);
			}
		} else {
			log_msg("Chain %d rib thread connecting", chain->chainID);

			/* establish the connection again */
			if (establishRConnection(chain)) {
				closeRChain(chain);
				/* connection failed, sleep and try again */
				log_err("Failed to connect to rib port for chain %d. Sleeping",
					chain->chainID);
				if (handleThreadSleep(chain)) {
					/* sleep failed for some reason */
					/* TODO decide what to do then. continue? */
				}
				continue;
			}
			log_msg("Chain %d rib thread connected", chain->chainID);

			/* reconnect was successful.  Can reset the retry interval */
			resetChainSleepInterval(chain);

			/* creating the backlog */
			if (createRBacklog(chain)) {
				log_err("Failed to create backlog for rib chain %d",
					chain->chainID);
				closeRChain(chain);
			}
		}
	}


	log_msg("closing read rib socket thread for chain %d", chain->chainID);
	closeRChain(chain);

	/* returning */
	pthread_exit(NULL);

}



/*
 * Purpose: Will read all complete messages out of a backlog into an XML queue.
 * Input:  pointer to the respective chian, pointer to the backlog to read
 *         from; pointer to the XML queue to write to
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 */
int
handleBacklogRead(Chain_structp chain, Backlog * bl, QueueWriter q)
{

	/* Checking if exists a full XML message in the buffer to parse and handle  */
	short 		c = 1;	/* a constant value that multiplies the buf
				 * len on next line */
	char           *msg;
	uint32_t 	msgLen = 0;

	/* Will read from the circular buffer as long as there is a message to be read. */
	/* Will break if there is no message or an error occurs. */
	short 		error = 0;
	while (1) {
		msgLen = 0;
		msg = (char *) calloc(c * XML_BF_LEN, sizeof(char));
		int 		retval = backlog_read_XML(bl, msg, c * XML_BF_LEN, &msgLen);
		if (retval == 1) {	/* buf is empty */
			free(msg);
			msg = NULL;
			break;
		} else if (retval == 2) {	/* unknown error from reading
						 * from buffer */
			error = 1;
			free(msg);
			msg = NULL;
			log_err("Chain %d update has unknown error reading from backlog.",
				chain->chainID);
			break;
		} else if (retval == 3) {	/* making buffer bigger and
						 * trying again */
			c++;
			free(msg);
			msg = NULL;
			continue;
		} else if (retval == 4) {	/* corrupt data coming in */
			error = 1;
			free(msg);
			msg = NULL;
			log_err("Chain %d was found to have corrupt data in backlog.",
				chain->chainID);
			break;
		} else {	/* retval == 0 - got a message. write to
				 * queue, read another */
			writeQueue(q, msg);
		}
	}

	/* An error occured, returning failure */
	if (error) {
		return 1;
	}
	/* all is well */
	return 0;
}






/*
 * Purpose: Updates the lastAction of the given chain to the current time
 * Input: Chain instance
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void 
updateLastAction(Chain_structp chain)
{
	chain->lastAction = time(NULL);

}



/*
 * Purpose: Attempts to connect to the update port of the BGPmon instance.
 * Input: Chain instance
 * Output: 0 on success
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 */
int 
establishUConnection(Chain_structp chain)
{

	log_msg("Establishing connection for update port for chain %d",
		chain->chainID);
	/* Updating the most recent action for the chain */
	updateLastAction(chain);

	/* Trying to connect to the other BGPmon instance's update socket */
	if (establishConnection(chain, chain->Uport, &(chain->Usocket),
				&(chain->UconnectionState),
				&(chain->UconnectRetryCounter))) {
		log_msg("Establishing connection failed!");
		return 1;
	}
	/* Updating state, time, and messages */
	chain->UconnectionState = chainStateConnected;
	chain->UestablishedTime = time(NULL);
	chain->UmessageRcvd = 0;

	/* handling first read */
	return handleFirstRead(chain, &(chain->Usocket), 0);
}

/*
 * Purpose: Attempts to connect to the update rib of the BGPmon instance.
 * Input: Chain instance
 * Output: 0 on success
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 */
int 
establishRConnection(Chain_structp chain)
{
	log_msg("Establishing connection for rib port for chain %d",
		chain->chainID);
	/* Updating the most recent action for the chain */
	updateLastAction(chain);

	/* Trying to connect to the other BGPmon instance's update socket */
	if (establishConnection(chain, chain->Rport, &(chain->Rsocket),
				&(chain->RconnectionState),
				&(chain->RconnectRetryCounter))) {
		log_msg("Establishing connection failed!");
		return 1;
	}
	/* Updating state, time, and messages */
	chain->RconnectionState = chainStateConnected;
	chain->RestablishedTime = time(NULL);
	chain->RmessageRcvd = 0;


	/* handling first read */
	return handleFirstRead(chain, &(chain->Rsocket), 0);
}



/*
 * Purpose: Will connect to a source given a port.  Is generic so that
 *          establishUConnection and establishRConnection will share this code.
 * Input:  pointer to the respective chian, port number to connect to,
 *         pointer to the socket to store, pointer to the connection state
 *         of the chian, pointer to the retry counter.
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 */
int
establishConnection(Chain_structp chain, int port, int *sock,
		    int *connectionState, int *counter)
{
	int optval = 1;
	log_msg("Establishing connection for chain %d to %s port %d",
		chain->chainID, chain->addr, port);

	/* Change state to connecting */
	*connectionState = chainStateConnecting;

	/* Increase counter of connection tries */
	*counter += 1;

	/* create addrinfo struct */
	struct addrinfo *res = createAddrInfo(chain->addr, port);
	if (res == NULL) {
		log_err("Unable to create address for chain %d to %s, port %d",
			chain->chainID, chain->addr, port);
		*connectionState = chainStateIdle;
		return 1;
	}
	/* create the socket */
	*sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
	if (*sock == -1) {
		log_err("Unable to create socket for chain %d to %s port %d",
			chain->chainID, chain->addr, port);
		*connectionState = chainStateIdle;
		return 1;
	}
	/* setup a receive timeout on the socket - this means we can use */
	/* recv without having to worry about select */
	struct timeval 	tv;
	tv.tv_sec = chain->periodicCheckInt;
	tv.tv_usec = 0;
	if (setsockopt(*sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
		log_err("setsockopt in chain rcvtime");
	}
	if (setsockopt(*sock, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval)) < 0) {
		log_err("setsockopt in chain keepalive");
	}

	/* connect to the remote chain   */
	int 		connection = connect(*sock, res->ai_addr, res->ai_addrlen);
	freeaddrinfo(res);
	res = NULL;
	if (connection == -1) {
		log_err("Unable to connect chain %d to %s!",
			chain->chainID, chain->addr, port);
		return 1;
	}
	log_msg("Established connection for chain %d to %s port %d",
		chain->chainID, chain->addr, port);

	return 0;
}


/*
 * Purpose: Wrapper to manage the connection for a chain's update connection.
 *          Is designed to call manageConnection
 * Input:  pointer to the respective chian
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 */
int
manageUConnection(Chain_structp chain)
{

	return manageConnection(chain, &(chain->Usocket),
				chain->Uport, chain->uBacklog);

}

/*
 * Purpose: Wrapper to manage the connection for a chain's rib connection.
 *          Is designed to call manageConnection
 * Input:  pointer to the respective chian
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 */
int
manageRConnection(Chain_structp chain)
{

	return manageConnection(chain, &(chain->Rsocket),
				chain->Rport, chain->rBacklog);

}

/*
 * Purpose: manage a chain connection.  Makes sure that the chain is still
 *          enabled and will read data off the socket if there is any.
 * Input:  pointer to the chain, pointer to the socket, port number, pointer
 *         backlog to write data in to
 * Output: returns 0 on success
 *         returns 1 on error
 * Note For Programmer: Can probably take out the port as it's only needed
 *                      for the log_err.  Maybe move log_err up or remove it
 *                      completely
 * M. Lawrence Weikum April, 2014
 */
int
manageConnection(Chain_structp chain, int *socket, int port, Backlog * bl)
{

	int 		sock = *socket;

	/* make sure we have a live socket */
	if (sock < 0) {
		log_warning("manage Connection forchain %d called without a valid socket connection", chain->chainID);
		return 1;
	}
	/* making sure we're enabled */
	if (!chain->enabled) {
		return 1;
	}
	/* updating time of this action */
	updateLastAction(chain);

	/* reading from the socket into the backlog */
	if (readMessage(chain, sock, bl)) {
		/* some sort of read error, return 1 to close connection */
		log_err("Socket read from chain %d at %s port %d failed",
			chain->chainID, chain->addr, port);
		return 1;
	}
	/* all went as expected */
	return 0;
}

/*
 * Purpose: Will try up to 5 times to do a furst read from the socket after a
 *          new connection is made.  This will read the '<xml>' start tag and
 *          dismiss it.
 * Input:  pointer to the chain, pointer to the socket, current try number
 * Output: returns 0 on success
 *         returns 1 on error
 * M. Lawrence Weikum April, 2014
 */
int
handleFirstRead(Chain_structp chain, int *socket, int tryNumber)
{

	/* Making sure we haven't overstepped our tries */
	if (tryNumber >= 5) {
		log_err("Handle first read for chain %d reached max tries!",
			chain->chainID);
		return 1;
	}
	/* Buffer to write into */
	char 		buf      [6] = {0};	/* for the <xml> tag at the
						 * beginning. */

	/* making sure we're connected */
	if (!chain->enabled) {
		return 1;
	}
	/* Peeking at the data on the socket.  Could time out */
	int 		numRec = recv(*socket, buf, 5, MSG_PEEK);

	/* Handleing errors */
	if (numRec < 0) {

		/* Making sure that it's not a timeout - that's fine - try again */
		if (errno == 11) {
			log_msg("Timeout occured while waiting for first read for chain %d",
				chain->chainID);
			return handleFirstRead(chain, socket, tryNumber + 1);
		}
		/* Seems we've gotten a different error and need to fail */
		log_err("Error with first readfor chain %d: %s.",
			chain->chainID, strerror(errno));
		return 1;
	}
	/* Connection was closed */
	else if (numRec == 0) {
		log_err("Chain %d has already closed the connection.",
			chain->chainID);
		return 1;
	}
	/* check if the first 5 bytes are <xml> */
	if (strcmp(buf, "<xml>") != 0) {
		/* did not receive "<xml>" like we should have - fail */
		return 1;
	}
	/* reading over it so that we can start reading messages */
	numRec = recv(*socket, buf, 5, 0);
	/* this call should have completed successfully since we reached here, but for */
	/* good measure, we're going to check anyway.  Should not have to deal */
	/* with the timeout */
	if (numRec < 0) {
		/* Received an error.  Making sure that it's not a timeout - that's fine */
		/* Seems we've gotten a different error and need to fail */
		log_err("Error with second readfor chain %d", chain->chainID);
		return 1;
	} else if (numRec == 0) {
		log_err("Chain %d has already closed the connection.",
			chain->chainID);
		return 1;
	}
	return 0;
}




/*
 * Purpose: Double the current retry interval time and make sure it doesn't
 *          go over our maximum retry interval.  Sleep that much time.
 * Input:  the chain structure
 * Output: 1 if trouble sleeping
 *         0 if no problem
 * M. Lawrence Weikum @ January 20, 2014
 */
int 
handleThreadSleep(Chain_structp chain)
{

#ifdef DEBUg
	log_msg("Handling sleep for chain %d", chain->chainID);
#endif

	/* Making sure it's not bigger than the maximum. Setting to max if it is */
	if (chain->connectRetryInterval >= MAX_CHAIN_RECONNECT_TIMEOUT)
		chain->connectRetryInterval = MAX_CHAIN_RECONNECT_TIMEOUT;

#ifdef DEBUG
	log_warning("Chain %d is sleeping for %d seconds before reconnecting.",
		    chain->chainID, chain->connectRetryInterval);
#endif

	/* sleeping */
	if (sleep(chain->connectRetryInterval)) {
		return 1;
	}
	/* Doubling the retry interval */
	chain->connectRetryInterval *= 2;

	return 0;
}

/*
 * Purpose: Resets the chain's timeout interval to the default timeout.
 * Input:  the chain structure
 * Output: 0 if no problem
 * M. Lawrence Weikum @ January 20, 2014
 */
int
resetChainSleepInterval(Chain_structp chain)
{

	chain->connectRetryInterval = chain->initialConnectRetryInterval;
	return 0;
}



/*
 * Purpose: Will read data off of the socket into the respective backlog.
 * Input:  the chain structure, socket to read from, backlog to write to
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 */
int
readMessage(Chain_structp chain, int socket, Backlog * bl)
{

	/* Getting the positions and size left in the buffer */
	char           *space;
	uint32_t 	size;

	/* Getting how much data we can write to the backlog */
	if (get_XML_buffer_write_pos(bl, &space, &size)) {
		log_err("Chain %d buffer for update stream is full!", chain->chainID);
		return 1;
	}
	/* Resetting the timeout for the socket */
	struct timeval 	tv;
	tv.tv_sec = chain->periodicCheckInt;
	tv.tv_usec = 0;
	if (setsockopt(socket, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv))) {
		log_err("readMessage: resetting timeout for socket failed.");
	}
	/* Reading in from the socket, writing to the backlog */
	int 		numRec = recv(socket, space, size, 0);
	if (numRec < 0) {
		/* Received an error.  Making sure that it's not a timeout - that's fine */
		if (errno == 11) {
			return 0;
		}
		/* Seems we've gotten a different error and need to fail */
		log_err("Error reading from for chain %d: %s.", chain->chainID,
			strerror(errno));
		return 1;
	} else if (numRec == 0) {
		log_err("Chain %d has already closed the connection.",
			chain->chainID);
		return 1;
	}
	/* updating the buffer positions */
	if (record_XML_buffer_write(bl, numRec)) {
		log_err("Buffer is full for chain.");
		return 1;
	}
	return 0;
}

/*
 * Purpose: Creates and inits backlog in memory for the update portion
 *          of the chain
 * Input:  the chain structure
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 */
int
createUBacklog(Chain_structp chain)
{
#ifdef DEBUG
	log_msg("Chain %d creating update backlog", chain->chainID);
#endif
	chain->uBacklog = (Backlog *) malloc(sizeof(Backlog));
	if (chain->uBacklog == NULL) {
		log_err("Failed to malloc space for update backlog chain %d",
			chain->chainID);
		return 1;
	}
	return backlog_init(chain->uBacklog);
}

/*
 * Purpose: Creates and inits backlog in memory for the rib portion
 *          of the chain
 * Input:  the chain structure
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 */
int
createRBacklog(Chain_structp chain)
{
#ifdef DEBUG
	log_msg("Chain %d creating rib backlog", chain->chainID);
#endif
	chain->rBacklog = (Backlog *) malloc(sizeof(Backlog));
	if (chain->rBacklog == NULL) {
		log_err("Failed to malloc space for rib backlog chain %d", chain->chainID);
		return -1;
	}
	return backlog_init(chain->rBacklog);
}

/*
 * Purpose: Closes the update socket if it was connected.  Resets connection
 *          state to idle, resets messages received, and deletes the backlog
 *          for the update portion of the chain.
 * Input:  the chain structure
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 */
void
closeUChain(Chain_structp chain)
{
	if (chain->Usocket != -1) {
		closeChainSocket(chain->Usocket);
	}
	chain->Usocket = -1;
	chain->UconnectionState = chainStateIdle;
	chain->UlastDownTime = time(NULL);
	chain->UresetCounter++;
	chain->UmessageRcvd = 0;
	if (chain->uBacklog != NULL) {
		backlog_destroy(chain->uBacklog);
		free(chain->uBacklog);
		chain->uBacklog = NULL;
	}
}

/*
 * Purpose: Closes the rib socket if it was connected.  Resets connection
 *          state to idle, resets messages received, and deletes the backlog
 *          for the rib portion of the chain.
 * Input:  the chain structure
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 */
void
closeRChain(Chain_structp chain)
{
	if (chain->Rsocket != -1) {
		closeChainSocket(chain->Rsocket);
	}
	chain->Rsocket = -1;
	chain->RconnectionState = chainStateIdle;
	chain->RlastDownTime = time(NULL);
	chain->RresetCounter++;
	chain->RmessageRcvd = 0;
	if (chain->rBacklog != NULL) {
		backlog_destroy(chain->rBacklog);
		free(chain->rBacklog);
		chain->rBacklog = NULL;
	}
}


/*
 * Purpose: Forces all data on a socket to stop and closes it.
 * Input:  Socket in question
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void
closeChainSocket(int socket)
{
	close(socket);
}

/*
 * Purpose: destroy the memory associated with a chain
 * Input:   the chain structure to destroy
 * Output:
 * M. Lawrence Weikum April, 2014
 */
void
destroyChain(Chain_structp chain)
{
	cleanupChainStruct(chain);
	Chains[chain->chainID] = NULL;
	free(chain);
	chain = NULL;
}

/*
 * Purpose: Cleanup a chain data structure so the thread can be closed
 *           sets the state to IDLE, clears counters and timers
 * Input:  the chain structure to cleanup
 * Output: 0 on success
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 */
int
cleanupChainStruct(Chain_structp chain)
{
	if (chain == NULL)
		return -1;

	/* clear the thread control settings */
	chain->reconnectFlag = FALSE;
	chain->runningFlag = FALSE;
	chain->lastAction = time(NULL);

	/* clear the socket related fields */
	if (chain->Usocket != -1) {
		closeChainSocket(chain->Usocket);
	}
	chain->Usocket = -1;
	chain->Userrno = 0;
	chain->UconnectionState = chainStateIdle;

	if (chain->Rsocket != -1) {
		closeChainSocket(chain->Rsocket);
	}
	chain->Rsocket = -1;
	chain->Rserrno = 0;
	chain->RconnectionState = chainStateIdle;

	/* clear the up time, peer reset, etc */
	chain->UestablishedTime = 0;
	chain->UlastDownTime = time(NULL);
	chain->UresetCounter++;
	chain->UmessageRcvd = 0;;

	chain->RestablishedTime = 0;
	chain->RlastDownTime = time(NULL);
	chain->RresetCounter++;
	chain->RmessageRcvd = 0;;


	/* xml queue writer cleanup */
	destroyQueueWriter(chain->UxmlQueueWriter);
	chain->UxmlQueueWriter = NULL;
	destroyQueueWriter(chain->RxmlQueueWriter);
	chain->RxmlQueueWriter = NULL;

	/* backlog cleanup */
	if (chain->uBacklog != NULL) {
		closeUChain(chain);
	}
	if (chain->rBacklog != NULL) {
		closeRChain(chain);
	}
	return 0;
}
