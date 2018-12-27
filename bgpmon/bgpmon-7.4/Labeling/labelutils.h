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
 *  File: labelutils.h
 * 	Authors: He Yan
 *  Date: May 31, 2008
 */

#ifndef LABELUTILS_H_
#define LABELUTILS_H_

#include <sys/types.h>

typedef struct struct_mstream {
    u_char  *start;
    uint16_t  position;
    uint32_t  len;
} MSTREAM;

void mstream_init(MSTREAM *s, u_char *buffer,uint32_t len);
int mstream_getc(MSTREAM *s, u_char *d);
int mstream_getw(MSTREAM *s, uint16_t *d);
int mstream_getl(MSTREAM *s, uint32_t *d);
int64_t mstream_can_read(MSTREAM *s);
int mstream_get (MSTREAM *s, void *d, uint32_t len);
int mstream_delete (MSTREAM *s, uint16_t start_pos, uint16_t end_pos);
int mstream_add (MSTREAM *s, void *data, uint16_t len);
u_char * mstream_current_address (MSTREAM *); 

#endif /*LABELUTILS_H_*/