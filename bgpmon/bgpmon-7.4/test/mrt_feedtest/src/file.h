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
 *  File: file.h
 *      Authors: Dan Massey
 *      opens an timestamped output file for storing MRT results 
 *  Date: Nov 7, 2011
 */

#include <stdio.h>
#include <string.h>
#include <time.h>
#include <limits.h>

// a timestamp and suffix are appended to file names

// the timestamp looks like YYYY:MM:DD:HH:MI:SS followed by "end of string" 
// YYYY=year,  MM=month,  DD=day,  HH=hour,  MI=minute, and SS=seconds
#define TIMESTAMP_SIZE 20

// define file suffixes
#define BIN_SUFFIX ".bin"
#define TXT_SUFFIX ".txt"
// suffix is .txt for headers and .bin for binary
#define SUFFIX_SIZE 5


/*----------------------------------------------------------------------------------------
 * Purpose: create a unique file that can be used to store data
 * Input: the base name for the file and a filetype which can be
 *        either DATA for storing MRT binary data or SUMMARY for
 *        storing MRT header summary information
 * Output:  the file descriptor or NULL on error 
 * Mikhail Strizhov @ Nov 3, 2011
 * -------------------------------------------------------------------------------------*/
FILE *openFile(char *filename,  int filetype) ;

