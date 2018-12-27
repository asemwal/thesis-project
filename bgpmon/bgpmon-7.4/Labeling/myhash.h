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
 *  File: myhash.h
 * 	Authors: Yan Chen
 *  Data: May 31, 2007 
 * EDITED BY LAWRENCE 2014
 */

#ifndef MYHASH_H_
#define MYHASH_H_


#include <stdint.h>

#ifndef UNSIGNED_CHAR_EASY
#define UNSIGNED_CHAR_EASY
typedef unsigned char u_char;
#endif /*UNSIGNED_CHAR_EASY*/

typedef uint32_t INDEX;

INDEX attr_hash ( const u_char *, uint16_t, uint32_t );
INDEX prefix_hash ( const u_char *, uint16_t, uint32_t);

#endif /*MYHASH_H_*/
