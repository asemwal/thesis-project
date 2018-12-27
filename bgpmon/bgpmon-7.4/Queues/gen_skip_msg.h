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
 *  File: gen_skip_msg.h
 *  Authors: M. Lawrnece Weikum
 *  Date: June 19, 2014
 */

#ifndef GENSKIP_H_
#define GENSKIP_H_


/* needed for malloc */
#include "stdlib.h"

/* Needed for queue name */
#include "queue.h"

/* needed for creating BMF and for BMF types */
#include "../Util/bgpmon_formats.h"

/* required for logging functions */
#include "../Util/log.h"

/* Needed for translating BMF to XML string */
#include "../XML/xml_gen.h"
#include "../Peering/peersession.h"

//needed for sequence number management
#include "../Clients/clientscontrol.h"


/* This structure will be given to the BMF->data to hold information
   regarding a skip ahead. */
typedef struct BmfSkipAhead{
  char* queueName;
  long numMsgsSkipped;
}SAM;



/*-----------------------------------------------------------------------------
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
 * --------------------------------------------------------------------------*/
const int genSkipAheadMessage(char* queueName, const long numSkipped, 
                              void** returnPointer);








#endif
