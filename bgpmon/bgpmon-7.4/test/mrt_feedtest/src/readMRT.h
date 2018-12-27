/*
 *
 *      Copyright (c) 2011 Colorado State University
 *
 *      Permission is hereby granted, free of charge, to any person
 *      obtaining a copy of this software and associated documentation
 *      files (the "Software"), to deal in the Software without
 *      restriction, including without limitation the rights to use,
 *      copy, modify, merge, publish, distribute, sublicense, and/or
 *      sell copies of the Software, and to permit persons to whom
 *      the Software is furnished to do so, subject to the following
 *      conditions:
 *
 *      The above copyright notice and this permission notice shall be
 *      included in all copies or substantial portions of the Software.
 *
 *      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *      EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 *      OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *      NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 *      HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 *      WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *      FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 *      OTHER DEALINGS IN THE SOFTWARE.\
 *
 *
 *  File: readMRT.h
 *      Authors: Dan Massey
 *      read MRT data from a socket,  store the data in a file,
 *      and validate the data pass simple MRT header checks
 *  Date: Nov 7, 2011
 */

#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <arpa/inet.h>

// define valid and invalid strings for summary output
#define VALID    "valid"
#define INVALID  "invalid"

// define the size of marker+length in BGP message: 16 bytes marker + 2 bytes for length = 18 bytes
#define MRKR_BGPLEN_SIZE 18

// MRT header structure
struct MrtObjStruct
{
  u_int32_t time;     // timestamp
  u_int16_t type;     // type
  u_int16_t subtype;  // subtype
  u_int32_t length;   // length of MRT message
};
typedef struct MrtObjStruct MrtHdr;

/*----------------------------------------------------------------------------------------
 * Purpose: read MRT data from a socket,  store the data in a file,
 *          and validate the data pass simple MRT header checks 
 * Input: socket providing MRT data,  a file to write the MRT data,
 *        and a file for writing summary information about headers
 * Output:  return 0 if all data read and the sender closed the socket
 *          -1 on an error
 * Mikhail Strizhov @ Nov 3, 2011
 * -------------------------------------------------------------------------------------*/
int readMRTdata(int new_fd, FILE *mrtData,  FILE *mrtSummary); 

