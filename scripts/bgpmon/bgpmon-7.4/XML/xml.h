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
 *  File:    xml.h
 *  Authors: He Yan
 *           Pei-chun (Payne) Cheng
 *  Date:    Jun 22, 2008 
 */

#ifndef XML_H_
#define XML_H_
#include <pthread.h>

/* label thread last action time */
struct XMLControls_struct_st {
	time_t		lastAction;
	pthread_t 	xmlThread;
	int		    shutdown;
};
typedef struct XMLControls_struct_st XMLControls_struct;

XMLControls_struct XMLControls;

/*
 * Purpose: launch xml converter thread, called by main.c
 * Input:   none
 * Output:  none
 * He Yan @ July 22, 2008
 */
void launchXMLThread();


/*
 * Purpose: get the last action time of the XML thread
 * Input:
 * Output: last action time
 * Mikhail Strizhov @ Jun 25, 2009
 */
time_t getXMLThreadLastAction();

/*
 * Purpose: Intialize the shutdown process for the xml module
 * Input:  none
 * Output: none
 * Kevin Burnett @ July 10, 2009
 */
void signalXMLShutdown();

/*
 * Purpose: wait on all xml pieces to finish closing before returning
 * Input:  none
 * Output: none
 * Kevin Burnett @ July 10, 2009
 */
void waitForXMLShutdown();

#endif /*XML_H_*/
