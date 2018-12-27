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
 *  File: bgpmon_formats.h
 * 	Authors: He Yan
 *  Date: Jun 20, 2008
 */


#ifndef BGPMON_FORMATS_H_
#define BGPMON_FORMATS_H_

#include <sys/types.h>
#include <string.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/time.h>


/*
 *  The BGPmon internal message format (BMF) exchanged between BGPmon modules.
 */

#define BMF_MAX_MSG_LEN 		8192
#define BMF_HEADER_LEN 			16

/* BGP header length: Marker(16) + Length(2) + Type(1) */
#define BGP_HEADER_LEN 			19

struct BGPmonInternalMessageFormatStruct 
{
	uint32_t		timestamp;
	uint32_t		precisiontime;
	uint16_t	  sessionID;
	uint16_t		type;
	uint32_t		length;
	u_char			message[BMF_MAX_MSG_LEN];
	void*  data;
};
typedef struct BGPmonInternalMessageFormatStruct* BMF;

/* bgpmon internal message format types */
#define BMF_TYPE_RESERVED 100
#define BMF_TYPE_MSG_TO_PEER 200
#define BMF_TYPE_MSG_FROM_PEER 300
#define BMF_TYPE_MSG_LABELED 400
#define BMF_TYPE_TABLE_TRANSFER 500
#define BMF_TYPE_SESSION_STATUS 600
#define BMF_TYPE_QUEUES_STATUS 700
#define BMF_TYPE_CHAINS_STATUS 800
#define BMF_TYPE_FSM_STATE_CHANGE 900
#define BMF_TYPE_BGPMON_START 1000
#define BMF_TYPE_BGPMON_STOP 2000
#define BMF_TYPE_MRT_STATUS 3000
#define BMF_TYPE_TABLE_START 4000
#define BMF_TYPE_TABLE_STOP 5000
#define BMF_TYPE_CLIENT_SKIP_AHEAD 6000
#define BMF_TYPE_MRT_TABLE_DUMP 7000
#define BMF_TYPE_MRT_TABLE_DUMP_V2 8000
#define BMF_TYPE_SKIP_AHEAD 9000

/* Create a BMF instance by allocating memory and setting time */
/* time is set to the current time and is the main purpose of this function */  
/* sessionID, and type are specified as parameters,  length is 0 */
BMF createBMF( uint16_t sessionID, uint16_t type, const void *message, uint32_t len);

/*****************************************************************************
 *
 * Crates a normal BMF data structure with no message attached ot it. 
 * Instead, it will assign the data passed into it to the data pointer of
 * the BMF strucutre.  
 *
 * Input: sessionID
 *        type - BMF type (use enums)
 *        data - pointer to a strucutre on the heap (required!)
 * Output: BMF - on success
 *         NULL - on failure
 *
 * Author: M. Lawrence Weikum 5/28/14
 *
*****************************************************************************/
BMF createBMFWithData(uint16_t sessionID, uint16_t type, void* givenData);

/* Append additional data to an existing BMF instance  */
/* to append data, specify the length of the data to add and the data   */
int bgpmonMessageAppend(BMF m, const void *message, uint32_t len);

/* Destroy a BMF instance  */
void destroyBMF( BMF bmf );

/*Checks to see if there is a message*/
int bmfHasMessage(BMF bmf);

/*****************************************************************************
 *
 * Checks to see if data was assigned to this BMF or not.
 *
 * Input: BMF
 * Output: 1 on true, 0 on false
 *
 * Author: M. Lawrence Weikum 5/28/14
 *
*****************************************************************************/
int bmfHashData(BMF bmf);

#endif

