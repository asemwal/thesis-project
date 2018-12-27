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
 *  File: clientinstance.c
 * 	Authors: He Yan, Dan Massey
 *
 *  Date: Oct 7, 2008
 *
 *  Authors: M. Lawrence Weikum
 *  Date October, 2013, 2014
 */

/*
 * Maintain a connection to a BGPmon client
 */

/* externally visible structures and functions for clients */
#include "clients.h"

/* internal structures of ClientControls module */
#include "clientscontrol.h"

/* internal structures and functions for this module */
#include "clientinstance.h"

/* required for logging functions */
#include "../Util/log.h"

/* needed for address management  */
#include "../Util/address.h"

/* needed for writen function  */
#include "../Util/unp.h"

/* needed for malloc and free */
#include <stdlib.h>

/* needed for strncpy and strdup */
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

/*#define DEBUG */

int 		fileID = 0;

/*
 * Purpose: Get an array of IDs of all active clients
 * Input: a pointer to an unallocated array
 * Output: the length of the array or -1 on failure
 * Note: 1. The caller doesn't need to allocate memory.
 *       2. The caller must free the array after using it.
 * He Yan @ Sep 22, 2008
 * Updated: M. Lawrence Weikum, April 2014
 */
int
getActiveClientsIDs(long **clientIDs, int client_listener)
{
	int 		err = -1;
	/* for UPDATA */
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		/* lock the client list */
		if (pthread_mutex_lock(&(ClientControls.clientULock)))
			log_fatal("lock client list failed");

		/* allocate an array whose size depends on the active clients */
		long           *IDs = (long *) calloc(ClientControls.activeUClients, sizeof(long));
		if (IDs == NULL) {
			log_err("Failed to allocate memory for getActiveClientIDs");
			*clientIDs = NULL;
			return -1;
		}
		/* for each active client, add its ID to the array */
		ClientNode     *cn = ClientControls.firstUNode;
		int 		i = 0;
		while (cn != NULL) {
			IDs[i] = cn->id;
			i++;
			cn = cn->next;
		}
		*clientIDs = IDs;

		/* sanity check how many IDs we found */
		if (i != ClientControls.activeUClients) {
			log_err("Unable to get Active Client IDs!");
			free(IDs);
			*clientIDs = NULL;
			i = -1;
		}
		/* unlock the client list */
		if (pthread_mutex_unlock(&(ClientControls.clientULock)))
			log_fatal("unlock client list failed");

		return i;
	}
	/* for RIB */
	if (client_listener == CLIENT_LISTENER_RIB) {

		/* lock the client list */
		if (pthread_mutex_lock(&(ClientControls.clientRLock)))
			log_fatal("lock client list failed");

		/* allocate an array whose size depends on the active clients */
		long           *IDs = (long *) calloc(ClientControls.activeRClients, sizeof(long));
		if (IDs == NULL) {
			log_err("Failed to allocate memory for getActiveClientIDs");
			*clientIDs = NULL;
			return -1;
		}
		/* for each active client, add its ID to the array */
		ClientNode     *cn = ClientControls.firstRNode;
		int 		i = 0;
		while (cn != NULL) {
			IDs[i] = cn->id;
			i++;
			cn = cn->next;
		}
		*clientIDs = IDs;

		/* sanity check how many IDs we found */
		if (i != ClientControls.activeRClients) {
			log_err("Unable to get Active Client IDs!");
			free(IDs);
			*clientIDs = NULL;
			i = -1;
		}
		/* unlock the client list */
		if (pthread_mutex_unlock(&(ClientControls.clientRLock)))
			log_fatal("unlock client list failed");

		return i;
	}
	return err;

}

/*
 * Purpose: Get the remote client port (port on the client machine)
 * Input: ID of the client
 * Output: port of this client
 *         or -1 if there is no client with this ID
 * He Yan @ Sep 22, 2008
 */
int
getClientPort(long ID, int client_listener)
{
	int 		err = -1;
	/* UPDATA */
	if (client_listener == CLIENT_LISTENER_UPDATA) {

		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->port;
			else
				cn = cn->next;
		}

		log_err("getClientPort: couldn't find a client with ID: %d", ID);
		return -1;
	}
	/* RIB */
	if (client_listener == CLIENT_LISTENER_RIB) {

		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->port;
			else
				cn = cn->next;
		}

		log_err("getClientPort: couldn't find a client with ID: %d", ID);
		return -1;
	}
	return err;
}

/*
 * Purpose: Get the remote address of a client (address of client machine)
 * Input: ID of the client
 * Output: address of this client in a char array.
 *         or NULL if there is no client with this ID
 * Note: 1. The caller doesn't need to allocate memory.
 *       2. The caller must free the string after using it.
 * He Yan @ Sep 22, 2008
 */
char           *
getClientAddress(long ID, int client_listener)
{
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				char           *ans = strdup(cn->addr);
				if (ans == NULL) {
					log_err("getClientAddress: couldn't allocate string memory");
					return NULL;
				}
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientAddress: couldn't find a client with ID: %d", ID);
		return NULL;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {
		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				char           *ans = strdup(cn->addr);
				if (ans == NULL) {
					log_err("getClientAddress: couldn't allocate string memory");
					return NULL;
				}
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientAddress: couldn't find a client with ID: %d", ID);
		return NULL;
	}
	return NULL;
}

/*
 * Purpose: Get the connected time of a client
 * Input: ID of the client
 * Output: connected time of this client
 * 		  or time = 0 if there is no client with this ID
 * He Yan @ Sep 22, 2008
 */
time_t
getClientConnectedTime(long ID, int client_listener)
{
	time_t 		err = 0;
	if (client_listener == CLIENT_LISTENER_UPDATA) {

		time_t 		ans = 0;
		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->connectedTime;
			else
				cn = cn->next;
		}

		log_err("getClientConnectedTime: couldn't find a client with ID: %d", ID);
		return ans;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {
		time_t 		ans = 0;
		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->connectedTime;
			else
				cn = cn->next;
		}

		log_err("getClientConnectedTime: couldn't find a client with ID: %d", ID);
		return ans;
	}
	return err;
}

/*
 * Purpose: Get the number of read items for a client
 * Input: ID of the client
 * Output: the number of read items for  this client
 * 	   or -1 if there is no client with this ID
 * He Yan @ Sep 22, 2008
 */
long
getClientReadItems(long ID, int client_listener)
{
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				QueueReader 	reader = cn->qReader;
				char           *qname = getQueueNameForReader(reader);
				if (qname == NULL)
					return -1;
				long 		index = getQueueIndexForReader(reader);
				if (index == -1) {
					free(qname);
					return -1;
				}
				long 		ans = getReaderReadItems(qname, index);
				free(qname);
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientReadItems: couldn't find a client with ID:%d", ID);
		return -1;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {

		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				QueueReader 	reader = cn->qReader;
				char           *qname = getQueueNameForReader(reader);
				if (qname == NULL)
					return -1;
				long 		index = getQueueIndexForReader(reader);
				if (index == -1) {
					free(qname);
					return -1;
				}
				long 		ans = getReaderReadItems(qname, index);
				free(qname);
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientReadItems: couldn't find a client with ID:%d", ID);
		return -1;
	}
	return -1;
}

/*
 * Purpose: Get the number of unread items for a client
 * Input: ID of the client
 * Output: the number of unread items for  this client
 * 	   or -1 if there is no client with this ID
 * He Yan @ Sep 22, 2008
 */
long
getClientUnreadItems(long ID, int client_listener)
{
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				QueueReader 	reader = cn->qReader;
				char           *qname = getQueueNameForReader(reader);
				if (qname == NULL)
					return -1;
				long 		index = getQueueIndexForReader(reader);
				if (index == -1) {
					free(qname);
					return -1;
				}
				long 		ans = getReaderUnreadItems(qname, index);
				free(qname);
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientUnreadItems: couldn't find a client with ID:%d", ID);
		return -1;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {
		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID) {
				QueueReader 	reader = cn->qReader;
				char           *qname = getQueueNameForReader(reader);
				if (qname == NULL)
					return -1;
				long 		index = getQueueIndexForReader(reader);
				if (index == -1) {
					free(qname);
					return -1;
				}
				long 		ans = getReaderUnreadItems(qname, index);
				free(qname);
				return ans;
			} else
				cn = cn->next;
		}

		log_err("getClientUnreadItems: couldn't find a client with ID:%d", ID);
		return -1;
	}
	return -1;
}

/*
 * Purpose: Get the last action time for this thread
 * Input: ID of the client
 * Output: a timevalue indicating the last time the thread was active
 *         or time = 0 if there is no client with this ID
 * He Yan @ Sep 22, 2008
 */
time_t
getClientLastAction(long ID, int client_listener)
{
	time_t 		err = 0;
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		time_t 		ans = 0;
		ClientNode     *cn = ClientControls.firstUNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->lastAction;
			else
				cn = cn->next;
		}
		log_err("getClientLastAction: couldn't find a client with ID: %d", ID);
		return ans;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {
		time_t 		ans = 0;
		ClientNode     *cn = ClientControls.firstRNode;
		while (cn != NULL) {
			if (cn->id == ID)
				return cn->lastAction;
			else
				cn = cn->next;
		}
		log_err("getClientLastAction: couldn't find a client with ID: %d", ID);
		return ans;
	}
	return err;
}

/*
 * Purpose: kill a client, close the thread and free all associated memory
 * Input: ID of the client
 * He Yan @ Sep 22, 2008
 */
void
deleteClient(long ID, int client_listener)
{
	if (client_listener == CLIENT_LISTENER_UPDATA) {
		ClientNode     *cn = ClientControls.firstUNode;
		log_msg("deleteClient Called!");
		while (cn != NULL) {
			if (cn->id == ID) {
				cn->deleteClient = TRUE;
				return;
			} else
				cn = cn->next;
		}
		log_err("deleteClient: couldn't find a client with ID:%d", ID);
	}
	if (client_listener == CLIENT_LISTENER_RIB) {
		ClientNode     *cn = ClientControls.firstRNode;
		log_msg("deleteClient Called!");
		while (cn != NULL) {
			if (cn->id == ID) {
				cn->deleteClient = TRUE;
				return;
			} else
				cn = cn->next;
		}
		log_err("deleteClient: couldn't find a client with ID:%d", ID);
	}
}

/*
 * Purpose:  destroy the socket and memory associated with a client ID
 * Input:  the client ID to destroy
 * Output: none
 * He Yan @ July 22, 2008
 */
void
destroyClient(long id, int client_listener)
{
#ifdef DEBUG
	log_err("Client id (%d) is in destroyClient", id);
#endif
	if (client_listener == CLIENT_LISTENER_UPDATA) {
#ifdef DEBUG
		log_err("Client id (%d) is in UPDATE", id);
#endif
		/* lock the client list */
		if (pthread_mutex_lock(&(ClientControls.clientULock)))
			log_fatal("lock client list failed");

		ClientNode     *prev = NULL;
		ClientNode     *cn = ClientControls.firstUNode;

		while (cn != NULL) {
			if (cn->id == id) {
				/* close this client connection */
				log_err("Deleting client id (%d)", cn->id);
				/* close the client socket */
				close(cn->socket);

#ifdef DEBUG
				log_err("Client id (%d) UPDATE CLOSED", id);
#endif
				/* remove from the client list */
				ClientControls.activeUClients--;
				if (prev == NULL)
					ClientControls.firstUNode = cn->next;
				else
					prev->next = cn->next;
				/* clean up the memory */
				destroyQueueReader(cn->qReader);
				free(cn);
				/* unlock the client list */
				if (pthread_mutex_unlock(&(ClientControls.clientULock)))
					log_fatal("unlock client list failed");
				return;
			} else {
				prev = cn;
				cn = cn->next;
			}
		}

		log_err("destroyClient: couldn't find a client with ID:%d", id);
		/* unlock the client list */
		if (pthread_mutex_unlock(&(ClientControls.clientULock)))
			log_fatal("unlock client list failed");
		return;
	}
	if (client_listener == CLIENT_LISTENER_RIB) {

#ifdef DEBUG
		log_err("Client id (%d) is in RIB", id);
#endif
		/* lock the client list */
		if (pthread_mutex_lock(&(ClientControls.clientRLock)))
			log_fatal("lock client list failed");

		ClientNode     *prev = NULL;
		ClientNode     *cn = ClientControls.firstRNode;

		while (cn != NULL) {
			if (cn->id == id) {
				/* close this client connection */
				log_msg("Deleting client id (%d)", id);
				/* close the client socket */
				close(cn->socket);
#ifdef DEBUG
				log_err("Client id (%d) RIB CLOSED", id);
#endif
				/* remove from the client list */
				ClientControls.activeRClients--;
				if (prev == NULL)
					ClientControls.firstRNode = cn->next;
				else
					prev->next = cn->next;
				/* clean up the memory */
				destroyQueueReader(cn->qReader);
				free(cn);
				/* unlock the client list */
				if (pthread_mutex_unlock(&(ClientControls.clientRLock)))
					log_fatal("unlock client list failed");
				return;
			} else {
				prev = cn;
				cn = cn->next;
			}
		}

		log_err("destroyClient: couldn't find a client with ID:%d", id);
		/* unlock the client list */
		if (pthread_mutex_unlock(&(ClientControls.clientRLock)))
			log_fatal("unlock client list failed");
		return;
	}
}

/*
 * Purpose: Create a new UPDATE ClientNode structure.
 * Input:  the client ID, address (as string), port, and socket
 * Output: a pointer to the new ClientNode structure
 *         or NULL if an error occurred.
 * He Yan @ July 22, 2008
 */
ClientNode     *
createClientUNode(long ID, char *addr, int port, int socket)
{
	/* create a client node structure */
	ClientNode     *cn = malloc(sizeof(ClientNode));
	if (cn == NULL) {
		log_err("Failed to allocate memory for new client.");
		return NULL;
	}
	cn->id = ID;
	strncpy(cn->addr, addr, strlen(addr));
	cn->port = port;
	cn->socket = socket;
	cn->connectedTime = time(NULL);
	cn->lastAction = time(NULL);
	cn->qReader = createQueueReader(&xmlUQueue, 1);
	cn->deleteClient = FALSE;
	cn->next = NULL;
	return cn;
}
/*
 * Purpose: Create a new RIB ClientNode structure.
 * Input:  the client ID, address (as string), port, and socket
 * Output: a pointer to the new ClientNode structure
 *         or NULL if an error occurred.
 * He Yan @ July 22, 2008
 */

ClientNode     *
createClientRNode(long ID, char *addr, int port, int socket)
{
	/* create a client node structure */
	ClientNode     *cn = malloc(sizeof(ClientNode));
	if (cn == NULL) {
		log_err("Failed to allocate memory for new client.");
		return NULL;
	}
	cn->id = ID;
	strncpy(cn->addr, addr, strlen(addr));
	cn->port = port;
	cn->socket = socket;
	cn->connectedTime = time(NULL);
	cn->lastAction = time(NULL);
	cn->qReader = createQueueReader(&xmlRQueue, 1);
	cn->deleteClient = FALSE;
	cn->next = NULL;
	return cn;
}

/*
 * Purpose: The main function of a thread handling one client
 * Input:  the client node structure for this client
 * Output: none
 * He Yan @ July 22, 2008
 */
void           *
clientUThread(void *arg)
{
	ClientNode     *cn = arg;	/* the client node structure */
	int 		readresult;	/* result of reading from queue */
	u_char         *xmlDataOut = NULL;	/* the data read in from the
						 * queue */
	ssize_t 	readlength;	/* the length of data read from queue */
	ssize_t 	wrotelength;	/* the length of data written to
					 * client */

	/* detach the thread so the resources may be returned  */
	/* when the thread exits */
	pthread_detach(pthread_self());

	/* write a open tag <xml> when connection starts */
	wrotelength = writen(cn->socket, "<xml>", 5);

	/* get the xml queue reader */
	QueueReader 	xmlQueueReader = cn->qReader;

	/* LAWRENCE EDIT - GOING TO WRITE EVERYTHING TO A TEMP FILE TO ENSURE SKIP */
	/* AHEAD MESSAGE WAS GIVEN */
	/*
	 * char filename[50] = {0}; snprintf(filename, 50, "/tmp/clientOutput%d.txt", fileID);
	 * fileID ++; FILE *f = fopen(filename, "w"); if (f == NULL) { log_fatal("LAWRENCE Error
	 * opening file!\n"); } log_err("LAWRENCE - OPENED FILE FOR OUTPUT - %s", filename);
	 */


	/* while the client is alive, read data from xml and write to client */
	while (cn->deleteClient == FALSE) {

		/* update the last action time */
		cn->lastAction = time(NULL);
		/* read from the queue */
		readresult = readQueue(xmlQueueReader);
		xmlDataOut = (u_char *) xmlQueueReader->items[0];
		/* if reader has been canceled or ceased, close client */
		if (readresult == READER_SLOT_AVAILABLE) {
			cn->deleteClient = TRUE;
			/* fprintf(f, "DESTROYING CLIENT"); */
		}
		/* otherwise write data to client */
		else {
			readlength = strlen((char *) xmlDataOut);
			wrotelength = writen(cn->socket, xmlDataOut, readlength);

#ifdef DEBUG
			log_err("Client UPDATE id (%d) read %d write %d ", cn->id, readlength, wrotelength);
#endif
			/* if write fails, close client */
			if (wrotelength != readlength) {	/* socket connection
								 * lost */
				cn->deleteClient = TRUE;
#ifdef DEBUG
				log_err("Client UPDATE id (%d) is being deleted - write failed", cn->id);
#endif
			}
			/* free the message we just wrote and get next msg */
			free(xmlDataOut);
			xmlDataOut = NULL;
		}
	}

	/* log_err("LAWRENCE - CLOSING FILE %s", filename); */
	/* fclose(f); */

	/* destroy the client   */
#ifdef DEBUG
	log_err("Client UPDATE id (%d) is calling destoryClient", cn->id);
#endif
	destroyClient(cn->id, CLIENT_LISTENER_UPDATA);

	/* free any messages that haven't been written to the queue	 */
	if (xmlDataOut != NULL)
		free(xmlDataOut);

#ifdef DEBUG
	log_err("Client RIB id (%d) is exiting", cn->id);
#endif
	pthread_exit((void *) 1);
}


/*
 * Purpose: The main function of a thread handling one client
 * Input:  the client node structure for this client
 * Output: none
 * He Yan @ July 22, 2008
 */
void           *
clientRThread(void *arg)
{
	ClientNode     *cn = arg;	/* the client node structure */
	int 		readresult;	/* result of reading from queue */
	u_char         *xmlDataOut = NULL;	/* the data read in from the
						 * queue */
	ssize_t 	readlength;	/* the length of data read from queue */
	ssize_t 	wrotelength;	/* the length of data written to
					 * client */

	/* detach the thread so the resources may be returned  */
	/* when the thread exits */
	pthread_detach(pthread_self());

	/* write a open tag <xml> when connection starts */
	wrotelength = writen(cn->socket, "<xml>", 5);

	/* get the xml queue reader */
	QueueReader 	xmlQueueReader = cn->qReader;

	/* while the client is alive, read data from xml and write to client */
	while (cn->deleteClient == FALSE) {
		/* update the last action time */
		cn->lastAction = time(NULL);
		/* read from the queue */
		readresult = readQueue(xmlQueueReader);
		xmlDataOut = (u_char *) xmlQueueReader->items[0];
		/* if reader has been canceled or ceased, close client */
		if (readresult == READER_SLOT_AVAILABLE)
			cn->deleteClient = TRUE;
		/* otherwise write data to client */
		else {
			readlength = strlen((char *) xmlDataOut);
			wrotelength = writen(cn->socket, xmlDataOut, readlength);
			/* if write fails, close client */
			if (wrotelength != readlength) {	/* socket connection
								 * lost */
#ifdef DEBUG
				log_err("Client RIB id (%d) is being deleted - write failed", cn->id);
#endif
				cn->deleteClient = TRUE;
			}
			/* free the message we just wrote and get next msg */
			free(xmlDataOut);
			xmlDataOut = NULL;
		}
	}

	/* destroy the client   */
#ifdef DEBUG
	log_err("Client RIB id (%d) is calling destoryClient", cn->id);
#endif
	destroyClient(cn->id, CLIENT_LISTENER_RIB);


	/* free any messages that haven't been written to the queue	 */
	if (xmlDataOut != NULL)
		free(xmlDataOut);

#ifdef DEBUG
	log_err("Client RIB id (%d) is exiting", cn->id);
#endif
	pthread_exit((void *) 1);
}
