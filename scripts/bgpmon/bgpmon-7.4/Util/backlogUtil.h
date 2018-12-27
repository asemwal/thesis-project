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
 *  File: bgplogUtil.h
 * 	Authors: M. Lawrence Weikum
 *
 *  Date: April 2014
 */

#ifndef BACKLOGUTIL_H_
#define BACKLOGUTIL_H_

#include "../Mrt/mrt.h"
#include "../Mrt/mrtMessage.h"
#include "log.h"
//#include "unp.h" - may not need
#include <stdlib.h>
#include <pthread.h>

#define START_BACKLOG_SIZE 1048576 // the default starting size (bytes) for 
                                     // backlog
#define READ_2BYTES(a,b) a=ntohs(*((uint16_t*)&b)) // read and convert
#define READ_4BYTES(a,b) a=ntohl(*((uint32_t*)&b)) // read and convert

struct backlog_struct{
  uint8_t         *buffer;        // a pointer to the backlog
  uint32_t        size;           // starts out as 0 (in bytes)
  uint32_t        start_size;      // starts out as 0 (in bytes)
  uint32_t        start_pos; 
  uint32_t        end_pos;
  pthread_mutex_t lock;


  uint32_t        start_wrap;
  uint32_t        end_wrap;
  pthread_mutex_t wrap_lock;  


};
typedef struct backlog_struct Backlog;

/******************************************************************************
* backlog_init
* Purpose: allocate the buffer and provide initial values
* Uses the default size defined by START_BACKLOG_SIZE
* Returns: 0 for success, 1 on failure
******************************************************************************/
int backlog_init(Backlog *backlog); 
int backlog_init_size(Backlog* backlog, uint32_t size);

/******************************************************************************
* backlog_destroy
* Purpose: free allocated space, and destroy the lock
* Returns: 0 for success, 1 on failure
******************************************************************************/
int backlog_destroy(Backlog *backlog); 

/******************************************************************************
* backlog_write
* Purpose: Write some number of bytes from a buffer to the backlog 
* Notes: This code assumes that the backlog lock has already been obtained!! 
*        If expansion of the buffer is needed, and not possible, messages
*        may be dropped.
* Returns: 0 for success, 1 on failure
******************************************************************************/
int backlog_write_MRT(Backlog *backlog, uint8_t* buffer, uint32_t bytes);

/******************************************************************************
* backlog_expand
* Purpose: Attempt to expand the buffer to be twice the size it was
* Notes:  Assumes the backlog lock has been aquired
*        
*        
* Returns: 0 for success, other on failure
******************************************************************************/
int backlog_expand(Backlog *backlog);

/******************************************************************************
* backlog_shrink
* Purpose: Attempt to shrink the buffer back down to the default starting
*          size
* Notes: Assumes the lock has already been obtained
*        Assumes that the buffer is empty
*        
* Returns: 0 for success, other on failure
******************************************************************************/
int backlog_shrink(Backlog *backlog,uint32_t new_size);

/******************************************************************************
* backlog_read
* This function reads a single mrt message from the backlog
* If the message that is next to be read will not fit in the space
* provided the lenght of that message is returned.
* Otherwise, 0 on success, -1 on failure
* The function can be called again with a larger buffer
******************************************************************************/
int backlog_read_MRT(Backlog* backlog, MRTheader* mrtHeader, 
                     uint8_t* rawMessage, uint16_t bytes);



int lock_XML_buffer(Backlog* b);
int unlock_XML_buffer(Backlog* b);
int get_XML_buffer_write_pos(Backlog* b, char** pos, uint32_t* space);
int record_XML_buffer_write(Backlog* b, uint32_t length);
int backlog_read_XML(Backlog* b,char* dest, uint32_t max_length, uint32_t* return_len);



//int backlog_write_XML(Backlog* backlog, char* buffer, uint32_t bytes);
/******************************************************************************
* MRT_backlog_fastforward_BGP
* This function attempts to find the next BGP header and then backup to the
* start of the MRT header before the BGP header
* Assumptions: The buffer is full of MRT data
*              The lock has already been acquired
* Returns: 0 if a fast forward took place, 1 if a fast forward was no possible
******************************************************************************/
int MRT_backlog_fastforward_BGP(Backlog *backlog);


/**

Returns positive integer to number of XML messages skipped, 0 if none, -1 on error
**/
int XML_backlog_fastforward(Backlog* backlog);
#endif
