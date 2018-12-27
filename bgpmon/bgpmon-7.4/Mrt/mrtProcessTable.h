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
 *  File: mrtinstance.c
 * 	Authors: He Yan, Dan Massey, Mikhail, Cathie Olschanowsky, Darshan Washimkar
 *
 *  Date: March 2012
 */
#ifndef MRTPROCESSTABLE_H_
#define MRTPROCESSTABLE_H_
 
/* externally visible structures and functions for mrts */
#include "mrt.h"
#include "mrtMessage.h"
#include "mrtUtils.h"
#include "../Util/backlogUtil.h"
#include "../Util/bgp.h"
#include "../XML/xml_gen.h"
// needed for QueueWriter
#include "../Queues/queue.h"

/* required for logging functions */
#include "../Util/log.h"
#include "../Util/utils.h"


#define TABLE_TRANSFER_SLEEP 30
#define MAX_RIB_ENTRY_HEADER_LENGTH 23

// MRT Peer_Index_Table,   subtype = 1
struct MRT_Index_Table
{
        uint32_t BGPSrcID;
        uint16_t ViewNameLen;
        uint16_t ViewName;
        uint16_t PeerCount;
        uint8_t  PeerType;
        uint32_t PeerBGPID;
        uint8_t  PeerIP[16];
        char  PeerIPStr[ADDR_MAX_CHARS];
        uint32_t PeerAS;
};
typedef struct MRT_Index_Table mrt_index;

// MRT RIB IP
struct MRT_RIB_Table
{
        uint32_t SeqNumb;
        uint8_t PrefixLen;
        char    Prefix[16];
        uint16_t EntryCount;
        uint16_t PeerIndex;
        uint32_t OrigTime;
        uint16_t AttrLen;
        u_char    BGPAttr[4096];
};
typedef struct MRT_RIB_Table mrt_uni;

// linked list of BGP messages
struct BGPTableStruct
{
        // includes WDLen=0, Attr Len, Attr, NLRI(Pref len, Pref), Could be MP_REACH
        BGPMessage *BGPmessage;
        // length of entire BGP message
        int length;
        // link to next structure
        struct BGPTableStruct *next;
} ;

struct BufferStructure
{
        // Session ID
        int ID;
        // flag which shows existence of linked list of BGP messages
        int table_exist;
        // linked list
        struct BGPTableStruct *start;
        struct BGPTableStruct *tail;
        uint32_t msg_count;
};
typedef struct BufferStructure  TableBuffer;

struct TABLE_DUMP_struct
{
  uint16_t viewNumber;
  uint16_t sequenceNumber;
  uint8_t prefix[16];
  char prefixStr[ADDR_MAX_CHARS];
  uint8_t prefixLength;
  uint8_t  status;
  uint32_t  originatedTime;
  uint8_t peerIP[16];
  char peerIPstr[ADDR_MAX_CHARS];
  uint16_t peerAs;
  uint16_t attributeLength;
  u_char    BGPAttr[4096];
};
typedef struct TABLE_DUMP_struct TABLE_DUMP_MSG;

struct PEER_ENTRIES_struct
{
    uint8_t  peerType;
    uint32_t peerBGPID;
    uint8_t  peerIP[16];
    char  peerIPStr[ADDR_MAX_CHARS];
    uint32_t peerAS;
};
typedef struct PEER_ENTRIES_struct Peer_Entry;

struct MRT_PEER_INDEX_TABLE_struct
{
    uint32_t BGPSrcID;
    uint16_t ViewNameLen;
    uint16_t ViewName;
    uint16_t PeerCount;
    Peer_Entry *peerEntries;
};
typedef struct MRT_PEER_INDEX_TABLE_struct Peer_Index_Table;

struct RIB_ENTRIES_struct
{
    uint16_t PeerIndex;
    uint32_t OrigTime;
    uint16_t AttrLen;
    u_char    BGPAttr[4096];
};
typedef struct RIB_ENTRIES_struct Rib_Entry;

struct MRT_RIB_TABLE_struct
{
    uint32_t SeqNumb;
    uint8_t PrefixLen;
    uint8_t Prefix[16];
    uint16_t EntryCount;
    Rib_Entry *RibEntry;
};
typedef struct MRT_RIB_TABLE_struct Mrt_Rib_Table;

struct MRT_RIB_GENERIC_struct
{
    uint32_t SeqNumb;
    uint16_t AFI;
    uint8_t SAFI;
    uint8_t NLRI[16];
    uint16_t EntryCount;
    Rib_Entry *RibEntry;
};
typedef struct MRT_RIB_GENERIC_struct Mrt_Rib_Generic;

/*-----------------------------------------------------------------------------
 * Purpose:This method processes MRT message of type 13 (TABLE DUMP V2)
 *         sub-type 6 (RIB_GENERIC)
 * Input:  the control MRT structure for this instance, Raw Table Dump v2
 *         message
 * Output: 0 for success
 *         1 for failure
 * Description: Table Dump information is populate in structure and
 *              on successful execution, BMF pointer is assigned with value.
 *
 * Author: Darshan Washimkar 6/6/2014
 *
-----------------------------------------------------------------------------*/

int MRT_processType_TableDumpV2_GENERIC_SUBTYPE(uint8_t* rawMessage,
      MRTheader *mrtHeader, BMF **bmfArray);

/*-----------------------------------------------------------------------------
 * Purpose:This method processes MRT message of type 13 (TABLE DUMP V2)
 *         sub-type 2,3,4,5 (RIB_IPV4_UNICAST, RIB_IPV4_MULTICAST,
 *         RIB_IPV6_UNICAST, RIB_IPV6_MULTICAST)
 * Input:  the control MRT structure for this instance, Raw Table Dump v2
 *         message
 * Output: 0 for success
 *         1 for failure
 * Description: Table Dump information is populate in structure and
 *              on successful execution, BMF pointer is assigned with value.
 *
 * Author: Darshan Washimkar 6/6/2014
 *
-----------------------------------------------------------------------------*/

int MRT_processType_TableDumpV2_RIB_SUBTYPE(uint8_t* rawMessage,
        MRTheader *mrtHeader, Peer_Index_Table **peerIndexTable,
        int* entryCount,BMF **bmfArray, MRTmessage ***mrtMessageArray,
        int **asn_lengthArray, unsigned int *seqNo);

/*-----------------------------------------------------------------------------
 * Purpose:This method processes MRT message of type 13 (TABLE DUMP V2)
 *         sub-type 1 (PEER_INDEX_TABLE)
 * Input:  the control MRT structure for this instance, Raw Table Dump v2
 *         message
 * Output: 0 for success
 *         1 for failure
 * Description: Table Dump information is populate in structure and
 *              on successful execution, BMF pointer is assigned with value.
 *
 * Author: Darshan Washimkar 6/6/2014
 *
-----------------------------------------------------------------------------*/

int MRT_processType_TableDumpV2_PeerIndexTable(uint8_t* rawMessage,
                MRTheader *mrtHeader, Peer_Index_Table** peerIndexTable);


/*-----------------------------------------------------------------------------
 * Purpose:This method processes MRT message of type 13 (TABLE DUMP V2)
 * Input:  the control MRT structure for this instance, Raw Table Dump
 *         message
 * Output: 1 for success
 *         0 for failure
 * Author: Darshan Washimkar 6/6/2014
 *
-----------------------------------------------------------------------------*/

int MRT_processType_TableDumpV2(uint8_t* rawMessage,
		MRTheader *mrtHeader, Peer_Index_Table **peerIndexTable,
		int* entryCount, BMF **bmfArray, MRTmessage ***mrtMessageArray,
		int **asn_lengthArray, unsigned int *seqNo);

/*-----------------------------------------------------------------------------
 * Purpose:This method processes MRT message of type 12 (TABLE DUMP)
 *         sub-type 1, 2 (IPV4, IPV6)
 * Input:  the control MRT structure for this instance, Raw Table Dump v2
 *         message
 * Output: 0 for success
 *         1 for failure
 * Description: Table Dump information is populate in structure and
 *              on successful execution, BMF pointer is assigned with value.
 *
 * Author: Darshan Washimkar 6/6/2014
 *
-----------------------------------------------------------------------------*/
int MRT_processType_TableDump(uint8_t* rawMessage, MRTheader *mrtHeader,
		             MRTmessage* mrtMessage_c, BMF *bmf, int* asNumLen, uint16_t* seqNo);

/*--------------------------------------------------------------------------------------
 * Purpose: Compacting prefix IP address to prefix
 * Input:  Prefix IP address, IP address version, Prefix Length
 * Output:  Compacted prefix, Size of Packed Prefix (return 0, if any error)
 * Darshan Washimkar @ Aug 3, 2014
 * -------------------------------------------------------------------------------------*/
int packPrefix(uint8_t *prefixIpAddr,  int ipVer, int prefixLen, u_char *packedPrefix);

/*--------------------------------------------------------------------------------------
 * Purpose: check how many null and non null tables we have
 * Input:  tablebuffer pointer,  number of peers in table
 * Output:  0 failure, 1 success (signal to exit while loop)
 * Mikhail Strizhov @ Oct 6, 2010
 * -------------------------------------------------------------------------------------*/
int checkBGPTableEmpty(TableBuffer  *tablebuffer, int NumberPeers);

/*--------------------------------------------------------------------------------------
 * Purpose: insert bmf messages into buffer
 * Input:  peers pointer to linked structure, tail of structure(makes addition faster), BMF message
 * Output: return linked list for every node, also updates tail by address
 * Mikhail Strizhov @ Oct 5, 2010
 * Input:  peers pointer to linked structure, tail of structure(makes addition faster), BMF message
 * Output: return linked list for every node, also updates tail by address
 * Mikhail Strizhov @ Oct 5, 2010
 * -------------------------------------------------------------------------------------*/
int insertBGPTable(TableBuffer *tbl, BGPMessage *bgp );

/*--------------------------------------------------------------------------------------
 * Purpose: write bmf messages to peer queue
 * Input: SessionID, linked list, Queue writer, convert flag (1 or 0)
 * Output: none
 * Mikhail Strizhov @ Oct 6, 2010
 * -------------------------------------------------------------------------------------*/
void writeBGPTableToQueue(int ID, struct BGPTableStruct **start, QueueWriter writerpointer, int asLen);

/*--------------------------------------------------------------------------------------
 * Purpose: free linked list of BGP messages
 * Input:  peers pointer to linked structure
 * Output: none
 * Mikhail Strizhov @ Oct 5, 2010
 * -------------------------------------------------------------------------------------*/
void freeBGPTable ( TableBuffer *tbl) ;

/*--------------------------------------------------------------------------------------
 * Purpose: this code processes MRT messages of type 13   TABLE_DUMP_V2
 * Input:  the socket to read from, the mrtheader object that put us here,
 * Output: 1 for success
 *         0 for failure
 * We are making the assumption that messages of type 13 will not be found in 
 * the same conversation as other types. Once we step into this subroutine
 * we will only process type 13s until disconnect.
 * TODO: this function needs more refactoring --> it is too long The Jira Issue is 
 * BGPMON-29
--------------------------------------------------------------------------------------*/
int 
MRT_processType13(MrtNode *cn, uint8_t *rawMessage, int *rawMessage_length, MRTheader *mrtHeader);

/******************************************************************************
 * Name: MRT_createTableBufferFromType13Subtype1
 * Input: MrtNode, mrtindex, tablebuffer (to be allocated), rawMessage mrtHeader
 * Outout: 0 on sucess, -1 on failure
 * Description:
 * This function reads the first message in a rib table conversation
 * and creates the infrastructure for saving all of the other data to be 
 * receieved.
******************************************************************************/
int
MRT_createTableBufferFromType13Subtype1(MrtNode *cn, mrt_index *indexPtr,TableBuffer **tablebuffer,
                                        const uint8_t *rawMessage,int rawMessage_length, MRTheader *mrtHeader);

/*-------------------------------------------------------------------------------------
 * Purpose: Process the Generic subtype from ribs
 * Input: NOT YET IMPLEMENTED
 * Output: NOT YET IMPLEMENTED
 * Info:
 * 4.3.3. RIB_GENERIC Subtype


   The RIB_GENERIC header is shown below.  It is used to cover RIB
   entries which do not fall under the common case entries defined
   above.  It consists of an AFI, Subsequent AFI (SAFI) and a single
   NLRI entry.  The NLRI information is specific to the AFI and SAFI
   values.  An implementation which does not recognize particular AFI
   and SAFI values SHOULD discard the remainder of the MRT record.

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                         Sequence number                       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |    Address Family Identifier  |Subsequent AFI |
       |         Entry Count           |  RIB Entries (variable)
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

                    Figure 9: RIB_GENERIC Entry Header
---------------------------------------------------------------------------------------*/
int 
MRT_processType13SubtypeGeneric(MRTheader *mrtHeader,const uint8_t *rawMessage, BGPMessage **bgp_arr,int *peer_idxs,int *bgp_count) ;

/*--------------------------------------------------------------------------------------
 * Purpose: this code processes MRT messages of type 13 subtype (2-5) 
 * Input:  pointer to table buffer, ptr to mrt header, raw mesage, a pointer to an 
           array of messages, an array for peer indexes, an array for counts and
           the max count expected
 * Output: 0 for success
 *         -1 for failure, this may be a read error or a format error
 *           therefore, it should not cause the read loop to exit
 *
 * Description: The main job of this function is to take the rawMessage, which is 
 * in MRT format, change it to BGP format, and then wrap it with a BMF header.
 * There will be one bmf message for each rib entry in the MRT message
--------------------------------------------------------------------------------------*/
int 
MRT_processType13SubtypeSpecific(TableBuffer *tablebuffer,MRTheader *mrtHeader,const uint8_t *rawMessage, BGPMessage **bgp_arr,
                                 int *peer_indexes,int *bgp_count,int max_count) ;

#endif
