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
 *	OTHER DEALINGS IN THE SOFTWARE.
 * 
 * 
 *  File: chaininstance.h
 * 	Authors:  M. Lawrence Weikum
 *  Date: April, 2014
 */

#include <arpa/inet.h>
#include <netinet/in.h>
#include <netdb.h>

#ifndef CHAININSTANCE_H_
#define CHAININSTANCE_H_

/* needed for ADDR_MAX_CHARS (maximum address size) */
#include "../Util/bgpmon_defaults.h"

/* needed so chain can write to XML queue */
#include "../Queues/queue.h"

/* needed for system types such as time_t */
#include <sys/types.h>

/* needed for the circular buffer to read and parse xml from socket */
//#include "../Util/expandable_buffer.h"
#include "../Util/backlogUtil.h"

//5 min is the maximum time to try to reconnect a chain
#define MAX_CHAIN_RECONNECT_TIMEOUT 300


#define XML_BF_LEN  1024000ULL
struct ChainStruct
{
	int		chainID;					

	// configuration settings
	char	addr[ADDR_MAX_CHARS];
	int		Uport;
	int		Rport;
	int		enabled;
	int		connectRetryInterval;
	int		initialConnectRetryInterval;

	// thread control
	int deleteChain;
	int reconnectFlag;
	int runningFlag;
	time_t lastAction;
	pthread_t chainThreadID;
	
	// socket related fields 
  int Usocket;
	int Userrno;
	int UconnectRetryCounter;
	int UconnectionState;
	int Rsocket;
	int Rserrno;
	int RconnectRetryCounter;
	int RconnectionState;

	// up time, peer reset counter, the number of received message
	time_t UestablishedTime;
	time_t UlastDownTime;
	int UresetCounter;
	int UmessageRcvd;
	time_t RestablishedTime;
	time_t RlastDownTime;
	int RresetCounter;
	int RmessageRcvd;

	// periodic check for configuration changes
	int periodicCheckInt;

	// write data to the xml queue
	QueueWriter	UxmlQueueWriter;
	QueueWriter	RxmlQueueWriter;

  // backlog for the queues
  Backlog* uBacklog;
  Backlog* rBacklog;

};
typedef struct ChainStruct * Chain_structp;

/* array of BGP chaining structures for receiving dat from other
 * BGPmon instances.  This BGPmon instance acts as a client
 * and connects to other BGPmon instances to form chains.
 */
Chain_structp Chains[MAX_CHAIN_IDS];

/*-----------------------------------------------------------------------------
 * Purpose: Create a chain data structure
 * Input:  address, update port, RIB port, enabled flag and retry interval.
 * Output: 1 on error, 0 on success
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int createChainStruct(char *addr, int Uport, int Rport, 
                      int enabled, int connectRetryInterval);

/*-----------------------------------------------------------------------------
 * Purpose: entry function of a chain thread.  Will create other chain threads
 *          and will join them if the chain is deleted or BGPmon closes
 *
 * Input:  pointer to a chain structure
 * Output: 
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
void* mainChainThread( void *arg );

/*-----------------------------------------------------------------------------
 * Purpose: entry function of a thread to handle the update stream of a chain.  
 *          Will establish a connection, handle reconnects, read from the
 *          socket to the backlog, and read messages out of the backlog to the
 *          XML queue until the chain is disabled.
 *
 * Input:  pointer to a chain structure
 * Output: 
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
void* updateThread(void* arg);

/*-----------------------------------------------------------------------------
 * Purpose: entry function of a thread to handle the RIB stream of a chain.  
 *          Will establish a connection, handle reconnects, read from the
 *          socket to the backlog, and read messages out of the backlog to the
 *          XML queue until the chain is disabled.
 *
 * Input:  pointer to a chain structure
 * Output: 
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
void* ribThread(void* arg);

/*-----------------------------------------------------------------------------
 * Purpose: Will read all complete messages out of a backlog into an XML queue.  
 * Input:  pointer to the respective chian, pointer to the backlog to read
 *         from; pointer to the XML queue to write to
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int handleBacklogRead(Chain_structp chain, Backlog* bl, QueueWriter q);

/*-----------------------------------------------------------------------------
 * Purpose: Updates the lastAction of the given chain to the current time
 * Input: Chain instance
 * Output:
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
void updateLastAction(Chain_structp chain);

/*-----------------------------------------------------------------------------
 * Purpose: Attempts to connect to the update port of the BGPmon instance.
 * Input: Chain instance
 * Output: 0 on success
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int establishUConnection(Chain_structp chain);

/*-----------------------------------------------------------------------------
 * Purpose: Attempts to connect to the rib port of the BGPmon instance.
 * Input: Chain instance
 * Output: 0 on success
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int establishRConnection(Chain_structp chain);


/*-----------------------------------------------------------------------------
 * Purpose: Generic call for establishUconnection or establishRconnection.
 * Input:   Will take in the chain struct, a port to connect to, the 
 *          address of the socket in memory, the address of the connecitonState
 *          in memory, and the address of the connection counter in memory.
 * Output: 0 on success, 1 on error
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int establishConnection (Chain_structp chain, int port, int* sock, 
                         int* connectionState, int* counter );

/*-----------------------------------------------------------------------------
 * Purpose: Wrapper to manage the connection for a chain's update connection.
 *          Is designed to call manageConnection
 * Input:  pointer to the respective chian
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int manageUConnection(Chain_structp chain);

/*-----------------------------------------------------------------------------
 * Purpose: Wrapper to manage the connection for a chain's rib connection.
 *          Is designed to call manageConnection
 * Input:  pointer to the respective chian
 * Output: 1 on success, 0 on error
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int manageRConnection(Chain_structp chain);

/*----------------------------------------------------------------------------- 
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
 * --------------------------------------------------------------------------*/
int manageConnection(Chain_structp chain, int* socket, int port, Backlog* bl);

/*----------------------------------------------------------------------------- 
 * Purpose: Will try up to 5 times to do a furst read from the socket after a
 *          new connection is made.  This will read the '<xml>' start tag and
 *          dismiss it.
 * Input:  pointer to the chain, pointer to the socket, current try number
 * Output: returns 0 on success
 *         returns 1 on error
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int handleFirstRead(Chain_structp chain, int* socket, int tryNumber);

/*-----------------------------------------------------------------------------
 * Purpose: Double the current retry interval time and make sure it doesn't
 *          go over our maximum retry interval.  Sleep that much time.
 * Input:  the chain structure
 * Output: 1 if trouble sleeping
 *         0 if no problem
 * M. Lawrence Weikum @ January 20, 2014
 * --------------------------------------------------------------------------*/
int handleThreadSleep( Chain_structp chain);

/*-----------------------------------------------------------------------------
 * Purpose: Resets the chain's timeout interval to the default timeout.
 * Input:  the chain structure
 * Output: 0 if no problem
 * M. Lawrence Weikum @ January 20, 2014
 * --------------------------------------------------------------------------*/
int resetChainSleepInterval( Chain_structp chain);

/*-----------------------------------------------------------------------------
 * Purpose: Will read data off of the socket into the respective backlog.
 * Input:  the chain structure, socket to read from, backlog to write to
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
int readMessage(Chain_structp chain, int socket, Backlog* bl);

/*---------------------------------------------------------------------------- 
 * Purpose: Creates and inits backlog in memory for the update portion
 *          of the chain
 * Input:  the chain structure 
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014 
 * --------------------------------------------------------------------------*/
int createUBacklog(Chain_structp chain);

/*---------------------------------------------------------------------------- 
 * Purpose: Creates and inits backlog in memory for the rib portion
 *          of the chain
 * Input:  the chain structure 
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014 
 * --------------------------------------------------------------------------*/
int createRBacklog(Chain_structp chain);


/*---------------------------------------------------------------------------- 
 * Purpose: Closes the update socket if it was connected.  Resets connection
 *          state to idle, resets messages received, and deletes the backlog
 *          for the update portion of the chain.
 * Input:  the chain structure 
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014 
 * --------------------------------------------------------------------------*/
void closeUChain(Chain_structp chain);

/*---------------------------------------------------------------------------- 
 * Purpose: Closes the rib socket if it was connected.  Resets connection
 *          state to idle, resets messages received, and deletes the backlog
 *          for the rib portion of the chain.
 * Input:  the chain structure 
 * Output: 1 on error
 *         0 on success
 * M. Lawrence Weikum April, 2014 
 * --------------------------------------------------------------------------*/
void closeRChain(Chain_structp chain);

/*---------------------------------------------------------------------------- 
 * Purpose: Forces all data on a socket to stop and closes it.
 * Input:  Socket in question
 * Output: 
 * M. Lawrence Weikum April, 2014 
 * --------------------------------------------------------------------------*/
void closeChainSocket(int socket);

/*-----------------------------------------------------------------------------
 * Purpose: destroy the memory associated with a chain
 * Input:   the chain structure to destroy
 * Output:
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/
void destroyChain( Chain_structp chain);

/*---------------------------------------------------------------------------- 
 * Purpose: Cleanup a chain data structure so the thread can be closed
 *           sets the state to IDLE, clears counters and timers
 * Input:  the chain structure to cleanup
 * Output: 0 on success 
 *         1 on failure
 * M. Lawrence Weikum April, 2014
 * --------------------------------------------------------------------------*/

int cleanupChainStruct( Chain_structp chain );

#endif /*CHAININSTANCE_H_*/



