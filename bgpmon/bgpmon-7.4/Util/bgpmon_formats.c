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
 *  File: bgpmon_formats.c
 * 	Authors: He Yan
 *  Date: May 6, 2008
 *
 *  Edited: March, 6, 2014
 *  Editor: M. Lawrence Weikum
 */

/*
 *  Utility functions that work for our internal struct BMF
 */

#include "bgpmon_formats.h"
#include "log.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <assert.h>

#include <sys/types.h>
#include <sys/time.h>

#define DEBUG

BMF
createBMF(uint16_t sessionID, uint16_t type, const void *message, uint32_t length)
{
	struct timeval 	tv;

	BMF 		m = malloc(sizeof(struct BGPmonInternalMessageFormatStruct));

	if (m == NULL) {
		log_err("CreateBgpmonMessage: malloc failed");
		/* RETURN NULL TO BE IMPLEMENTED LATER */
		return NULL;
	}
	gettimeofday(&tv, NULL);
	m->timestamp = (u_int32_t) tv.tv_sec;
	m->precisiontime = (u_int32_t) tv.tv_usec;
	m->sessionID = sessionID;
	m->type = type;
	m->length = 0;
	m->data = NULL;

	if (message != NULL) {
		if (length > 0) {
			if (bgpmonMessageAppend(m, message, length)) {
				log_err("Error adding message to BMF");
				free(m);
				m = NULL;
				return NULL;
			}
		} else {
			log_err("Adding message to BMF failed, length of 0 given");
			free(m);
			m = NULL;
			return NULL;
		}
	} else if (length > 0) {
		log_err("Adding message to BMF failed, length given but no messge was");
		free(m);
		m = NULL;
		return NULL;
	}
	return m;
}




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
BMF
createBMFWithData(uint16_t sessionID, uint16_t type, void *givenData)
{

	if (givenData == NULL) {
		log_err("createBMFWithData: no data given to BMF");
		return NULL;
	}
	BMF 		toReturn = createBMF(sessionID, type, NULL, 0);

	if (toReturn == NULL) {
		log_err("createBMFWithData: create BMF error");
		return NULL;
	}
	toReturn->data = givenData;

	return toReturn;
}

int
bgpmonMessageAppend(BMF m, const void *message, uint32_t len)
{
	/*
	 * appends to message buffer
	 */
	if (message != NULL && len > 0 && m->length + len <= BMF_MAX_MSG_LEN) {
		memcpy(&m->message[m->length], message, len);
		m->length += len;
	} else {
		if (len >= BMF_MAX_MSG_LEN) {
			log_err("BgpmonMessageAppend: length error. Length is %lu, BMF_MAX_MSG_LEN is %lu", len, BMF_MAX_MSG_LEN);
			return -1;
		} else {
			log_err("bgpmonMessageAppend: Invalid BMF or message supplied!");
			return -1;
		}
	}
	return 0;
}

void
destroyBMF(BMF bmf)
{
	if (bmf != NULL) {
		if (bmf->data != NULL) {
			free(bmf->data);
			bmf->data = NULL;
		}
		free(bmf);
		bmf = NULL;
	}
}

int
bmfHasMessage(BMF bmf)
{
	return bmf->length > 0;
}

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
int 
bmfHashData(BMF bmf)
{
	return bmf->data != NULL;
}
