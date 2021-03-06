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
 *  File: mrtinstance.h
 * 	Authors: He Yan, Dan Massey
 *  Date: Oct 7, 2008 
 */

#ifndef MRTINSTANCE_H_
#define MRTINSTANCE_H_

#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>

#include "mrtMessage.h"
#include "mrtUtils.h"
#include "../Util/backlogUtil.h"
#include "mrtProcessMSG.h"
#include "../Peering/peersession.h"

#define TABLE_TRANSFER_SLEEP 30


/*--------------------------------------------------------------------------------------
 * Purpose: The main function of a thread handling one mrt connection
 * Input:  the mrt node structure for this mrt
 * Output: none
 * Cathie Olschanowsky March 2012
 *
 * The main function is required to 
 * 1 - instantiate a backlog
 * 2 - check the first message and choose which type of secondary thread to start
 *     this can be a table dump thread or an update stream thread
 * 3 - create the thread.
 * 4 - Enter a loop and repeatedly read from the socket and write to the backlog.
 * -------------------------------------------------------------------------------------*/
void* mrtThread( void *arg );


#endif /*MRTINSTANCE_H_*/

