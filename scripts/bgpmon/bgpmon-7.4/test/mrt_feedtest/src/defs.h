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
 *  File: defs.h
 *      Authors: Mikhail Strizhov
 *  Date: Nov 7, 2011
 */

// define MAX macro 
#ifndef MAX
#define MAX( a, b ) ( ((a) > (b)) ? (a) : (b) )
#endif


// MRT header types
#define OSPFv2         11
#define TABLE_DUMP     12
#define TABLE_DUMP_V2  13
#define BGP4MP         16
#define BGP4MP_ET      17
#define ISIS           32
#define ISIS_ET        33
#define OSPFv3         48
#define OSPFv3_ET      49
  
// TABLE_DUMP_V2 subtypes 
  
#define PEER_INDEX_TABLE   1
#define RIB_IPV4_UNICAST   2
#define RIB_IPV4_MULTICAST 3
#define RIB_IPV6_UNICAST   4
#define RIB_IPV6_MULTICAST 5
#define RIB_GENERIC        6

// BGP4MP subtypes
#define BGP4MP_STATE_CHANGE      0
#define BGP4MP_MESSAGE           1
#define BGP4MP_MESSAGE_AS4       4
#define BGP4MP_STATE_CHANGE_AS4  5
#define BGP4MP_MESSAGE_LOCAL     6
#define BGP4MP_MESSAGE_AS4_LOCAL 7

// max BGP message size
#define BGPMSG_SIZE 4096

// STATE_CHANGE_SIZE subtype header: 
// 2 byte peer AS, 2 byte local AS, 2 byte index, 2 byte addr family
// 16 bytes of peer IP address, 16 bytes of local IP address
// 2 bytes of old state, 2 bytes of new state
#define BGP4MP_STATE_CHANGE_SIZE      44

// MESSAGE_SIZE subtype header:
// 2 byte peer AS, 2 byte local AS, 2 byte index, 2 byte addr family
// 16 bytes of peer IP address, 16 bytes of local IP address
#define BGP4MP_MESSAGE_SIZE           40

// MESSAGE_AS4_SIZE subtype header:
// 4 byte peer AS, 4 byte local AS, 2 byte index, 2 byte addr family
// 16 bytes of peer IP address, 16 bytes of local IP address
#define BGP4MP_MESSAGE_AS4_SIZE       44

// STATE_CHANGE_AS4_SIZE subtype header:
// 4 byte peer AS, 4 byte local AS, 2 byte index, 2 byte addr family
// 16 bytes of peer IP address, 16 bytes of local IP address
// 2 bytes of old state, 2 bytes of new state
#define BGP4MP_STATE_CHANGE_AS4_SIZE  48

// max size of MRT message provided by a collector
#define TABLE_BGPSIZE 8192

// define the max size of data
#define MAXDATASIZE MAX(BGPMSG_SIZE, BGPMSG_SIZE)

// max file name size
#define MAXNAME 512

// file types
#define DATA 1
#define SUMMARY 2

// server connection state of this program
#define UNCONNECTED 0
#define LISTEN      1
#define CONNECTED   2

// possible reasons to close the program
#define CONTINUE_LISTENING  0 // connection closed, go back to listening
#define MRT_DATA_FILE_ERROR -1 // unable to create data output file
#define MRT_SUMMARY_FILE_ERROR -2 // unable to create summary output file
#define ACCEPT_ERROR -2 // unable to create summary output file
// any user signal (values 1 or above) such as 2 for cntrl-C 
// will also close the program

// time_t type sizes
#define TIME_T_32 0
#define TIME_T_64 1

