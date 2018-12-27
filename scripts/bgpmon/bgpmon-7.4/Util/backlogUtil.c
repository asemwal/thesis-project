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
 *  File: backlogUtil.h
 * 	Authors: M. Lawrence Weikum
 *
 *  Date: April 2014
 *
 *  Note to future authors: this code was taken from mrtUtils.c.
 *  Origianlly, this code was only for MRT, but it was my job to
 *  make it more general so that it can be used for chains.  Most of this
 *  code is verbatum what I received.  The original author is unknown.
 */

/* externally visible structures and functions for mrts */
#include "backlogUtil.h"
#include "../Util/utils.h"
#include "../XML/xmlinternal.h"

/*#define DEBUG */

/******************************************************************************
* backlog_init
* Purpose: allocate the buffer and provide initial values
* Uses the default size defined by START_BACKLOG_SIZE
* Returns: 0 for success, 1 on failure
******************************************************************************/
int
backlog_init(Backlog * backlog)
{
	return backlog_init_size(backlog, START_BACKLOG_SIZE);
}

int
backlog_init_size(Backlog * backlog, uint32_t size)
{
	/* Initializing position variables */
	backlog->start_size = size;
	backlog->size = size;
	backlog->start_pos = 0;
	backlog->end_pos = 0;

	backlog->start_wrap = 0;
	backlog->end_wrap = 0;
	/* Initializing locks */
	if (pthread_mutex_init(&backlog->wrap_lock, NULL)) {
		log_err("Unable to init mutex lock for the wrap of backlog");
		return -1;
	}
	/* initialize the lock for the backlog */
	if (pthread_mutex_init(&(backlog->lock), NULL)) {
		log_err("Unable to init mutex lock for backlog");
		return -1;
	}
	backlog->buffer = calloc(backlog->size, sizeof(uint8_t));
	if (backlog->buffer == NULL) {
		log_err("Unable to calloc space for backlog");
		return -1;
	}
	return 0;


}

/******************************************************************************
* backlog_destroy
* Purpose: free allocated space, and destroy the lock
* Returns: 0 for success, 1 on failure
******************************************************************************/
int
backlog_destroy(Backlog * backlog)
{
	if (backlog->buffer != NULL) {
		free(backlog->buffer);
	}
	return pthread_mutex_destroy(&(backlog->lock)) &&
		pthread_mutex_destroy(&(backlog->wrap_lock));;
}

/******************************************************************************
* backlog_write
* Purpose: Write some number of bytes from a buffer to the backlog
* Notes: This code assumes that the backlog lock has already been obtained!!
*        If expansion of the buffer is needed, and not possible, messages
*        may be dropped.
* Returns: 0 for success, 1 on failure
******************************************************************************/
int
backlog_write_MRT(Backlog * backlog, uint8_t * buffer, uint32_t bytes)
{

	/* if the backlog is empty, start it over at the beginning */
	if (backlog->end_pos == backlog->start_pos) {
		backlog->end_pos = backlog->start_pos = 0;
#ifdef DEBUG
		log_msg("write: end_pos: %d start:pos %d\n", backlog->end_pos,
			backlog->start_pos);
#endif
	}
	/* the first thing we do here is to check if the buffer is full */
	/* if it is full then we can attempt to extend the buffer */
	/* if that fails we will have to start losing data */

	uint32_t 	space = backlog->size - backlog->end_pos + backlog->start_pos;
	if (backlog->start_pos > backlog->end_pos) {
		space = backlog->start_pos - backlog->end_pos;
	}
	if (space <= bytes) {
		if (backlog_expand(backlog)) {
			/* extending the backlog failed --  */
			/* this may be due to being out of space, or hitting the max */
			/* this is where we go ahead and miss some messages */
			log_err("Skipping messages in backlog - could not expand");
			return 1;	/*
			       while(space <= bytes){
			 
			         uint8_t rawMessage[MAX_MRT_LENGTH];
			         MRTheader mrtHeader;
			         if(backlog_read(backlog,&mrtHeader,rawMessage,MAX_MRT_LENGTH)){
			           return 1;
			         }
			         space =  backlog->size - backlog->end_pos + backlog->start_pos;
			         if(backlog->start_pos > backlog->end_pos){
			           space = backlog->start_pos - backlog->end_pos;
			         }
			       }*/
		}
		/* LAWRENCE - WHY DID ORIG AUTHOR PUT RECURSION HERE? */
		return backlog_write_MRT(backlog, buffer, bytes);
	}
	/* at this point we can be sure that we have enough room to write */
	/* there are 3 cases */
	/* 1. no wrapping has happened and it is not needed */
	/* 2. no wrapping has happened, but we will start it here */
	/* 3. wrapping has happened */

	/* check to see that there has not been any wrapping */
	if (backlog->start_pos <= backlog->end_pos) {	/* no wrapping */
		/* check to see that there is room between the end of the current data */
		/* and the end of the backlog */
		if ((backlog->size - backlog->end_pos) > bytes) {
			/* case 1: no wrapping in past, none needed now */
#ifdef DEBUG
			log_msg("write no wrapping\n");
#endif
			memcpy(&(backlog->buffer[backlog->end_pos]), buffer, bytes);
			backlog->end_pos += bytes;
#ifdef DEBUG
			log_msg("write: end_pos: %d start:pos %d\n", backlog->end_pos,
				backlog->start_pos);
#endif
		} else {
#ifdef DEBUG
			log_msg("write wrapping\n");
#endif
			/* case 2: no wrapping in past, but we need it here */
			/* copy enough to fill up the end of the buffer */
			memcpy(&(backlog->buffer[backlog->end_pos]),
			       buffer, (backlog->size - backlog->end_pos));
			/* copy the rest to the beginning of the buffer */
			memcpy(&(backlog->buffer[0]),
			       buffer + (backlog->size - backlog->end_pos),
			       (bytes - (backlog->size - backlog->end_pos)));
			backlog->end_pos = (bytes - (backlog->size - backlog->end_pos));
#ifdef DEBUG
			log_msg("write: end_pos: %d start:pos %d\n", backlog->end_pos,
				backlog->start_pos);
#endif
		}
		/* case 3: there has been wrapping, but we still have a continuous section of  */
		/* memory to copy to */
	} else {
#ifdef DEBUG
		log_msg("wrote after wrapping\n");
#endif
		memcpy(&(backlog->buffer[backlog->end_pos]), buffer, bytes);
		backlog->end_pos += bytes;
#ifdef DEBUG
		log_msg("write: end_pos: %d start:pos %d\n", backlog->end_pos,
			backlog->start_pos);
#endif
	}
	return 0;
}

/******************************************************************************
* backlog_expand
* Purpose: Attempt to expand the buffer to be twice the size it was
* Notes:  Assumes the backlog lock has been aquired
*
*
* Returns: 0 for success, other on failure
******************************************************************************/
int
backlog_expand(Backlog * backlog)
{

	/* calculating the new size */
	uint32_t 	new_size = 2 * backlog->size;
	void           *new_log = NULL;

	log_err("Attempting to expand backlog to %lu bytes", new_size);
	/* Fix for over memory expansion and force kill of bgpmon from Linux kernel */
	if (new_size > 8 * START_BACKLOG_SIZE) {
		log_err("Backlog expanding stopped!  Too big of memory! %d", new_size);
		return -1;
	}
	/* Creating the new log */
	new_log = calloc(new_size, sizeof(uint8_t));
	if (new_log == NULL) {
		log_err("Failed to calloc new backlog");
		return -1;
	}
	/* we have the larger space... the copying from the old buffer will differ */
	/* depending on the state of wrapping */
	if (backlog->start_pos <= backlog->end_pos) {
		memcpy(new_log, &(backlog->buffer[backlog->start_pos]), (backlog->end_pos - backlog->start_pos));
		free(backlog->buffer);
		backlog->buffer = new_log;
		backlog->end_pos = backlog->end_pos - backlog->start_pos;
		backlog->start_pos = 0;
		backlog->size = new_size;
		return 0;
	}
	/* if we are here there was wrapping and we need to do 2 memcpys */
	memcpy(new_log,
	       &(backlog->buffer[backlog->start_pos]),
	       (backlog->size - backlog->start_pos));
	memcpy(&(new_log[(backlog->size - backlog->start_pos)]),
	       backlog->buffer,
	       (backlog->end_pos));
	backlog->end_pos = (backlog->size - backlog->start_pos) + backlog->end_pos;
	backlog->start_pos = 0;
	backlog->size = new_size;
	free(backlog->buffer);
	backlog->buffer = new_log;
	return 0;
}


/******************************************************************************
* backlog_shrink
* Purpose: Attempt to shrink the buffer back down to the default starting
*          size
* Notes: Assumes the lock has already been obtained
*        Assumes that the buffer is empty
*
* Returns: 0 for success, other on failure
******************************************************************************/
int
backlog_shrink(Backlog * backlog, uint32_t new_size)
{

	void           *new_log = NULL;

	/* only shrink an empty buffer */
	if (backlog->start_pos != backlog->end_pos) {
		return -1;
	}
	new_log = calloc(new_size, sizeof(uint8_t));
	if (new_log == NULL) {
		log_err("Failed to calloc smaller backlog for shrinking.");
		return -1;
	}
	free(backlog->buffer);

	backlog->buffer = new_log;
	backlog->start_pos = 0;
	backlog->end_pos = 0;
	backlog->size = new_size;

	return 0;

}
/******************************************************************************
* MRT_backlog_read
* This function reads a single mrt message from the backlog
* If the message that is next to be read will not fit in the space
* provided the length of that message is returned.
* Otherwise, 0 on success, 1 on empty, -1 on corrupt, > 1 if the buffer is not
* large enough (the buffer is obviously larger than 1 byte and so thats a
* resonable restriction.
* The function can be called again with a larger buffer
******************************************************************************/
int
backlog_read_MRT(Backlog * backlog, MRTheader * mrtHeader,
		 uint8_t * rawMessage, uint16_t bytes)
{

	uint32_t 	message_index;
#ifdef DEBUG
	log_msg("read: end_pos: %d start:pos %d\n",
		backlog->end_pos, backlog->start_pos);
#endif

	/* check to see if the backlog is empty  */
	if (backlog->start_pos == backlog->end_pos) {
		return 1;
	}
	/* start by scanning for the header */
	/* there are several cases here */
	/* 1 - there was no wrapping and there is not a full message */
	/* 2 - there was no wrapping and there is a full header */
	/* 3 - there was wrapping and the header is not full */
	/* 4 - there was wrapping and the header is wrapped */
	/* 5 - there was wrapping and the header is not wrapped */
	if (backlog->start_pos < backlog->end_pos) {
		/* there has not been any wrapping */
		if ((backlog->end_pos - backlog->start_pos) < MRT_HEADER_LENGTH) {
			/* 1 - there was no wrapping and there is not a full message */
			return 1;
		}
		/* 2 - there was no wrapping and there is a full header */
#ifdef DEBUG
		log_msg("read: no wrapping, copy header\n");
#endif
		memcpy(mrtHeader, &(backlog->buffer[backlog->start_pos]),
		       MRT_HEADER_LENGTH);
		message_index = backlog->start_pos + MRT_HEADER_LENGTH;

	} else if (((backlog->size - backlog->start_pos) + backlog->end_pos) < MRT_HEADER_LENGTH) {
		/* 3 - there was wrapping and the header is not full */
		return 1;

	} else if ((backlog->size - backlog->start_pos) < MRT_HEADER_LENGTH) {
		/* 4 - there was wrapping and the header is wrapped */
		memcpy(mrtHeader, &(backlog->buffer[backlog->start_pos]),
		       (backlog->size - backlog->start_pos));
		memcpy(((void *) mrtHeader + (backlog->size - backlog->start_pos)),
		       backlog->buffer,
		(MRT_HEADER_LENGTH - (backlog->size - backlog->start_pos)));
		message_index = MRT_HEADER_LENGTH - (backlog->size - backlog->start_pos);
#ifdef DEBUG
		log_msg("read: wrapped header\n");
#endif

	} else {
		/* 5 - there was wrapping and the header is not wrapped */
		memcpy(mrtHeader, &(backlog->buffer[backlog->start_pos]),
		       MRT_HEADER_LENGTH);
		message_index = backlog->start_pos + MRT_HEADER_LENGTH;
#ifdef DEBUG
		log_msg("read: wrapped, but not header\n");
#endif
	}

	/* the header has been read -- network ordering */
	mrtHeader->timestamp = ntohl(mrtHeader->timestamp);
	mrtHeader->type = ntohs(mrtHeader->type);
	mrtHeader->subtype = ntohs(mrtHeader->subtype);
	mrtHeader->length = ntohl(mrtHeader->length);

	/* validate the header */
	int 		err_code = MRT_header_invalid(mrtHeader);
	if (err_code) {
		log_err("invalid header: type %d subtype %d err code %d\n",
			mrtHeader->type,
			mrtHeader->subtype,
			err_code);
		/* we don't have a valid header...  */
		return (-1 * err_code);
	}
	/* attempt to read the message  */
	/* there are several cases here */
	/* 1 - there was no wrapping and there is not a full message */
	/* 2 - there was no wrapping and there is a full message  */
	/* 3 - there was wrapping and the message is not full */
	/* 4 - there was wrapping and the message is wrapped */
	/* 5 - there was wrapping and the message is not wrapped */
	/* check to see if there is a full message in the buffer */
	if (backlog->start_pos < backlog->end_pos) {
		/* there has not been any wrapping */
		if ((backlog->end_pos - backlog->start_pos) <
		    (MRT_HEADER_LENGTH + mrtHeader->length)) {
			/* there is not a full message in the buffer as of now */
			return 1;
		}
	} else if (((backlog->size - backlog->start_pos) + backlog->end_pos) <
		   (MRT_HEADER_LENGTH + mrtHeader->length)) {
		return 1;
	}
	/* check to see if the length of the message will fit in the buffer */
	if (mrtHeader->length > bytes) {
		return mrtHeader->length;
	}
	/* Now we can go ahead and read the message. */
	/* No validation is done on the message itself, that is left to the */
	/* caller. */
	/* We have the same cases as above */
	/* 1 - there has been no wrapping, but the full message is not there */
	/* 2 - no wrapping, message is there */
	/* 3 - wrapping, message is not there */
	/* 4 - wrapping, message is wrapped */
	/* 5 - wrapping, message is not wrapped */
	if (message_index < backlog->end_pos) {
		/* there has not been any wrapping */
		if ((backlog->end_pos - message_index) < mrtHeader->length) {
			/* there is not a full message in the buffer as of now */
			return 1;
		}
#ifdef DEBUG
		log_msg("read: no message wrapping\n");
#endif
		memcpy(rawMessage, &(backlog->buffer[message_index]),
		       mrtHeader->length);
		message_index = message_index + mrtHeader->length;

	} else if (((backlog->size - message_index) + backlog->end_pos) < mrtHeader->length) {
		/* there has been wrapping and there is not a full message */
		return 1;

	} else if ((backlog->size - message_index) < mrtHeader->length) {
		/* the message is in the buffer, but it is wrapped */
#ifdef DEBUG
		log_msg("read: message wrapped\n");
#endif
		memcpy(rawMessage, &(backlog->buffer[message_index]),
		       (backlog->size - message_index));
		memcpy((rawMessage + (backlog->size - message_index)), backlog->buffer,
		     (mrtHeader->length - (backlog->size - message_index)));
		message_index = mrtHeader->length - (backlog->size - message_index);

	} else {
#ifdef DEBUG
		log_msg("read: message not wrapped\n");
#endif
		/* there has been wrapping, but the message is not wrapped */
		memcpy(rawMessage, &(backlog->buffer[message_index]),
		       mrtHeader->length);
		message_index = message_index + mrtHeader->length;
	}

	/* move the message index to the end of the read message */
	backlog->start_pos = message_index;
#ifdef DEBUG
	log_msg("read: end_pos: %d start:pos %d\n",
		backlog->end_pos, backlog->start_pos);
#endif

	return 0;
}

/******************************************************************************
* MRT_backlog_fastforward_BGP
* This function attempts to find the next BGP header and then backup to the
* start of the MRT header before the BGP header
* Assumptions: The buffer is full of MRT data
*              The lock has already been acquired
* Returns: 0 if a fast forward took place, 1 if a fast forward was no possible
******************************************************************************/
int
MRT_backlog_fastforward_BGP(Backlog * backlog)
{

	uint32_t 	curr_pos;
	uint8_t 	hdr_cnt = 0;
	/* As long as curr_pos is less than the end of the buffer */
	/* and not equal to the end_pos we should keep going */
	/* start at start_pos; */
	curr_pos = backlog->start_pos;
	while (curr_pos != backlog->end_pos && hdr_cnt < 16) {

		/* if we have all ones increment out count */
		if (backlog->buffer[curr_pos] == 255) {
			hdr_cnt++;
		} else {
			/* start over at 0 */
			hdr_cnt = 0;
		}

		curr_pos++;
		if (curr_pos >= backlog->size) {
			curr_pos = 0;
		}
	}

	/* check to see if we found the header */
	if (hdr_cnt == 16) {
		/* now we need to step forward until we reach */
		/* the end of this message */
		uint16_t 	bgp_length;
		READ_2BYTES(bgp_length, backlog->buffer[curr_pos]);
		/* uint8_t bgp_length = ntohs((uint8_t)backlog->buffer[curr_pos]); */
		bgp_length -= (BGP_HEADER_LEN - 3);
		/* the three is for the length and type fields */
		/* attempt to fast forward to the end of the length (this should be the */
		/* next message) */

		/* There has been no wrapping */
		if (curr_pos >= backlog->start_pos && curr_pos <= backlog->end_pos) {
			/* the backlog does not contain the whole meesage */
			if (curr_pos + bgp_length > backlog->end_pos) {
				return 1;
			}
			log_err("fast forward in progress: no wrapping/whole message ");
			/* char str[MAX_MRT_LENGTH]; */
			backlog->start_pos = (curr_pos + bgp_length);
			return 0;

			/* There has been wrapping */
		} else if (curr_pos >= backlog->start_pos && (backlog->end_pos <
						      backlog->start_pos)) {
			/* but the whole message is not in the buffer (split into 2 statements) */
			/* calculate the space in the buffer  */
			/* (backlog->size-curr_pos)(guaranteed to be >) + backlog->end_pos */
			if (bgp_length > (backlog->size - curr_pos) + backlog->end_pos) {
				return 1;
			}
			log_err("fast forward in progress: wrapping/whole message ");
			/* success */
			if (bgp_length <= (backlog->size - curr_pos)) {
				backlog->start_pos = (curr_pos + bgp_length);
			} else {
				backlog->start_pos = (bgp_length - (backlog->size - curr_pos));
			}
			return 0;
		} else if (curr_pos < backlog->start_pos && curr_pos <= backlog->end_pos) {
			if ((curr_pos + bgp_length) <= backlog->end_pos) {
				log_err("fast forward in progress: last case");
				char 		str      [MAX_MRT_LENGTH];
				bin2hexstr(&backlog->buffer[curr_pos], bgp_length, str, MAX_MRT_LENGTH);
				log_err("fast forward past: %s\n", str);
				/* success */
				backlog->start_pos = (curr_pos + bgp_length);
				bin2hexstr(&backlog->buffer[backlog->start_pos], bgp_length, str,
					   MAX_MRT_LENGTH);
				log_err("next header: %s\n", str);
				return 0;
			} else {
				return 1;
			}
		}
	}
	/* we read the entire backlog and found no marker */
	backlog->start_pos = backlog->end_pos = 0;
	return -1;
}



/*
int
backlog_write_XML(Backlog* bl, char* buffer, uint32_t bytes){

#ifdef DEBUG
    log_msg("Writing XML to buffer size = %d", bytes);
#endif

    char* space;
    uint32_t size;
    if(get_buffer_write_pos(bl, &space, &size)){
      return -1;
    }
#ifdef DEBUG
    log_msg("Size able to write to buffer = %d", bytes);
#endif
    if(size < bytes){
#ifdef DEBUG
    log_msg("Write XML shows that there is not enough space in the buffer to write the message");
#endif
      return -2;
    }

    strncpy(space, buffer, bytes);

    if(record_buffer_write(bl, bytes)){
      return -3;
    }

    return 0;

}*/




/**
returns 0 if no error
return 1 if error

*/
int
lock_XML_buffer(Backlog * b)
{
#ifdef DEBUG
	log_msg("Locking the xml buffer");
#endif
	return pthread_mutex_lock(&(b->lock));
}
/**
returns 0 if no error
return 1 if error

*/
int
unlock_XML_buffer(Backlog * b)
{
#ifdef DEBUG
	log_msg("Unocking the xml buffer");
#endif
	return pthread_mutex_unlock(&(b->lock));
}

/*****************************************************************************
get_buffer_write_pos
get a pointer to the space where writing can take place, along with the
amount of data that can be written into it
return values: 0, success
               1, buffer is full
*****************************************************************************/
int
get_XML_buffer_write_pos(Backlog * b, char **pos, uint32_t * space)
{
	pthread_mutex_lock(&b->wrap_lock);
	*pos = (char *) &b->buffer[b->end_pos];
	/* calculate the space */
	if (b->start_wrap ^ b->end_wrap) {
		/* we are in a wrapped state */
		*space = (b->start_pos - 1) - b->end_pos;
	} else {
		/* not in a wrapped state */
		*space = b->size - b->end_pos;
	}
	if (*space == 0) {
		pthread_mutex_unlock(&b->wrap_lock);
		return 1;
	}
	pthread_mutex_unlock(&b->wrap_lock);
	return 0;
}


/*****************************************************************************
record_buffer_write
get a pointer to the space where writing can take place, along with the
amount of data that can be written into it
return values: 0, success
               1, buffer is full
*****************************************************************************/
int
record_XML_buffer_write(Backlog * b, uint32_t length)
{
	pthread_mutex_lock(&b->wrap_lock);
	b->end_pos += length;
	if (b->end_pos == b->size) {
		b->end_pos = 0;
		__sync_fetch_and_xor(&b->end_wrap, 1);
	} else if (b->end_pos > b->size) {
		pthread_mutex_unlock(&b->wrap_lock);
		return 1;
	}
	pthread_mutex_unlock(&b->wrap_lock);
	return 0;
}


/*****************************************************************************
read_xml_message
read a complete xml message from the buffer
input: buffer pointer, pointer to space for message, max length of data,
	pointer to the length of the message being returned.
return values: 0, success
               1, buffer is empty
               2, unknown
               3, destination buffer is too small
               4, Corrupt data coming in didn't start with a '<'
*****************************************************************************/
int
backlog_read_XML(Backlog * b, char *dest, uint32_t max_length, uint32_t * return_len)
{

	/* our positions in the buffer */
	uint32_t 	scan_pos = b->start_pos;
	int 		scan_wrap = b->start_wrap;

	/* have we emptied the buffer? */
	int 		empty = 0;
	if (b->start_pos == b->end_pos) {
		return 1;
	}
	/* position in the destination buffer */
	uint32_t 	dest_idx = 0;

	/* keep track of tag depth and message depth */
	int 		tag_depth = 0;
	int 		msg_depth = 0;

	/* as it scan through the data it needs to maintain 3 variables */
	char           *previous = NULL;
	char           *current = (char *) &b->buffer[scan_pos];
	char           *next = NULL;
	pthread_mutex_lock(&b->wrap_lock);
	if (b->end_wrap ^ scan_wrap) {
		/* we are in a wrapped state */
		if ((scan_pos + 1) < b->size) {
			next = (char *) &b->buffer[scan_pos + 1];
		} else {
			if (b->end_pos != 0) {
				next = (char *) &b->buffer[0];
			} else {
				/* the buffer is going to be empty on the next step */
				/* and in this case that means that we should stop */
				pthread_mutex_unlock(&b->wrap_lock);
				return 1;
			}
		}
	} else {
		if ((scan_pos + 1) < b->end_pos) {
			next = (char *) &b->buffer[scan_pos + 1];
		} else {
			/* the buffer is going to be empty on the next step */
			/* and in this case that means that we should stop */
			pthread_mutex_unlock(&b->wrap_lock);
			return 1;
		}
	}
	pthread_mutex_unlock(&b->wrap_lock);

	/* if we aren't starting at a < character the XML is corrupt */
	if (*current != '<') {
		return 4;
	}
	if (dest_idx < max_length) {
		dest[dest_idx] = *current;
		dest_idx++;
	} else {
		return 3;
	}


	/* increment our state */
	tag_depth++;
	msg_depth++;

	/* the basic idea here is to take one step forward in the buffer */
	/* this step may actually be back to the beginning of the buffer */
	/* or it may not be possible */
	pthread_mutex_lock(&b->wrap_lock);
	while ((tag_depth != 0 || msg_depth != 0) && !empty) {
		/* take one step further in the buffer */
		scan_pos++;
		previous = current;
		current = next;

		if (current == NULL) {
			pthread_mutex_unlock(&b->wrap_lock);
			return 1;
		}
		if (b->end_wrap ^ scan_wrap) {
			/* we are in a wrapped state */
			if (scan_pos == b->size) {
				scan_pos = 0;
				scan_wrap = scan_wrap ^ 1;
				if (b->end_pos > 1) {
					next = (char *) &b->buffer[1];
				} else {
					next = NULL;
				}
			} else if ((scan_pos + 1) < b->size) {
				next = (char *) &b->buffer[scan_pos + 1];
			} else {
				if (b->end_pos != 0) {
					next = (char *) &b->buffer[0];
				} else {
					next = NULL;
				}
			}
		} else {
			/* not in a wrapped position */
			if ((scan_pos + 1) < b->end_pos) {
				next = (char *) &b->buffer[scan_pos + 1];
			} else {
				next = NULL;
			}
		}

		/* check the value of current */
		if (*current == '<') {
			tag_depth++;
			msg_depth++;
		} else if (*current == '>') {
			tag_depth--;
		} else if (*current == '/') {
			if (*previous == '<') {
				msg_depth -= 2;
			} else if (next != NULL && *next == '>') {
				msg_depth -= 1;
			}
		}
		if (dest_idx < max_length) {
			dest[dest_idx] = *current;
			dest_idx++;
		} else {
			pthread_mutex_unlock(&b->wrap_lock);
			return 3;
		}

		/* check for an emtpy buffer */
		if (scan_pos == b->end_pos) {
			empty = 1;
		}
	}
	pthread_mutex_unlock(&b->wrap_lock);

	/* if a complete message was found */
	/* update the state of the buffer */
	if (tag_depth == 0 && msg_depth == 0) {
		pthread_mutex_lock(&b->wrap_lock);
		if (scan_pos > b->start_pos) {
			if ((scan_pos + 1) < b->size) {
				b->start_pos = scan_pos + 1;
			} else {
				b->start_pos = scan_pos + 1;
				__sync_fetch_and_xor(&b->start_wrap, 1);
			}
		} else {
			b->start_pos = scan_pos + 1;
			__sync_fetch_and_xor(&b->start_wrap, 1);
		}
		pthread_mutex_unlock(&b->wrap_lock);
		dest[dest_idx] = '\0';

		*return_len = dest_idx + 1;	/* +1 because we want the
						 * count to include the \o */
		return 0;
	} else if (empty) {
		return 1;
	}
	return 2;
}


int
XML_backlog_fastforward(Backlog * backlog)
{
	short 		c = 1;	/* multiplyer for the message */
	uint32_t 	totalCount = 0;

	/* Ideally, we will read messages out of the buffer one by one and free */
	/* them until the buffer is empty.  Then we'll return the number of */
	/* messages skipped */
	while (1) {
		uint32_t 	msgLen = 0;
		char           *msg = (char *) calloc(c * XML_BUFFER_LEN, sizeof(char));
		if (msg == NULL) {
			/* TODO - ERROR CHECKING AND HANDLING */
		}
		int 		retval = backlog_read_XML(backlog, msg, c * XML_BUFFER_LEN, &msgLen);
		if (retval == 1) {	/* buf is empty */
			free(msg);
			break;
		} else if (retval == 2) {	/* unknown error from reading
						 * from buffer */
			free(msg);
			log_err("Unknown error fast forwarding the XML backlog");
			return -1;
		} else if (retval == 3) {	/* making buffer bigger and
						 * trying again */
			c++;
			free(msg);
			continue;
		} else if (retval == 4) {	/* corrupt data coming in */
			free(msg);
			log_err("Found corrupt data coming in when fast forwarding the XML backlog");
			return -1;
		} else {	/* retval == 0 - got a message */
			totalCount++;
			free(msg);
		}
	}
	return totalCount;

}
