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
 *  Date: March 2012
 */

#ifndef MRTUTILS_H_
#define MRTUTILS_H_

#include "mrt.h"
#include "mrtMessage.h"
#include "../Queues/queue.h" // QueueWriter
#include "../Util/backlogUtil.h"
#include "../Util/log.h"
#include "../Util/unp.h"
#include <stdlib.h>
#include <pthread.h>


/* structure holding mrt information  */
struct MrtStruct
{
        int             id;                     // mrt ID number
        char            addr[ADDR_MAX_CHARS];   // mrt's address
        int             port;                   // mrt's port
        int             socket;                 // mrt's socket for reading
        time_t          connectedTime;          // mrt's connected time
        time_t          lastAction;             // mrt's last action time
        QueueWriter     qWriter;                // mrt's Peer queue writer 
        int             deleteMrt;              // flag to indicate delete
        int             labelAction;            // default label action for
        pthread_t       mrtThreadID1;            // thread reference
        pthread_t       mrtThreadID2;
        Backlog         backlog;
        struct MrtStruct *      next;           // pointer to next mrt node
};
typedef struct MrtStruct MrtNode;




/******************************************************************************
 * MRT_readMessage
 * Input: socket, pointer to the MRT header to populate, pointer to space
 *        for the raw message
 * Return: -1 on read error
 *          n on success; n= the number of messages fast forwarded over
 *                        to get to the next valid header
 *          0 on total sucess > 0 with some failures, but can proceed
 *****************************************************************************/
int MRT_readMessage(int socket,MRTheader *mrtHeader,uint8_t *rawMessage);

/******************************************************************************
 * MRT_readMessageNoHeader
 * Input: socket, pointer to the MRT header to populate, pointer to space
 *        for the raw message
 * Return: -1 on read error
 *          n on success; n= the number of messages fast forwarded over
 *                        to get to the next valid header
 *          0 on total sucess > 0 with some failures, but can proceed
 *****************************************************************************/
int MRT_readMessageNoHeader(int socket,MRTheader mrtHeader,uint8_t *rawMessage);

/*--------------------------------------------------------------------------------------
 * Purpose: read in the mrt header
 * Input:  the socket to read from, a pointer the MRT header struct to populate
 * Output: 1 for success
 *         0 for failure --> should result in closing the MRT session
 * Cathie Olschanowsky @ 8/2011
 * first read the MRT common header http://tools.ietf.org/search/draft-ietf-grow-mrt-15#section-2
 * expected format
 *0                   1                   2                   3
 *0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                           Timestamp                           |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|             Type              |            Subtype            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                             Length                            |
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *|                      Message... (variable)
 *+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
--------------------------------------------------------------------------------------*/
int MRT_parseHeader(int socket,MRTheader* mrtHeader);

/*--------------------------------------------------------------------------------------
 * Purpose: fast forward reading from the socket, the given number of bytes
 * Input:  the socket to read from, the number of bytes to skip
 * Output: 1 for success
 *         0 for failure
--------------------------------------------------------------------------------------*/
int MRT_fastForward(int socket, int length);

/*--------------------------------------------------------------------------------------
 * Purpose: fast forward reading from the socket to the next valid BGP header
 * Input:  the socket to read from
 * Output: 1 for success
 *         0 for failure
 * we are searching for 16 255s in a row here.
 * the magic 18 is because 16 bytes + 2 bytes for length = 18 bytes
 * the lenght is inclusive in the BGP header
--------------------------------------------------------------------------------------*/
int MRT_fastForwardToBGPHeader(int socket);

#endif
