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
 *  File: utils.h
 * 	Authors:  Kevin Burnett, Dan Massey
 *  Date: July 21, 2008 
 */

#ifndef UTILS_H_
#define UTILS_H_

// needed for addrinfo struct
#include <netdb.h>

// needed for FILE handle
#include <stdio.h>

#include <time.h>
#include <unistd.h>

struct BGPmonAddr_Struct {
   struct addrinfo *addr;
   char *addrstring;
   int isLocal;
   int isValid;
};

typedef struct BGPmonAddr_Struct BGPmonAddr; 


/* sleep for the required time, but wake up and update thread status 
   occasionally */
void sleepWithBreaks(int seconds,time_t *threadStatus,int *shutdown);

void bin2hexstr(const void *mem, int length, char *str, int max);

#endif /*UTILS_H_*/
