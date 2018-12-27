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
 *  File:    xml_gen.h
 *  Author:  M. Lawrence Weikum
 *           Catherine Olschanowsky
 *  Adapted
 *  From:    Pei-chun (Payne) Cheng
 *           Jason Bartlett
 *  Date:    May 2013
 */

#ifndef XML_GEN_H_ 
#define XML_GEN_H_

#include <libxml/xmlwriter.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>

#include "xmlinternal.h"
#include "../Util/bgpmon_formats.h"
#include "../Util/bgpmon_defaults.h"
#include "../Util/log.h"
#include "../Util/bgppacket.h"
#include "../Util/xml_help.h"

#define _XML_NS "http://www.w3.org/2001/XMLSchema"
#define _XFB_NS "urn:ietf:params:xml:ns:xfb"
#define _NE_NS "urn:ietf:params:xml:ns:network_elements"
#define _MON_NS "urn:ietf:params:xml:ns:bgp_monitor"

#define ADDRESS_STRING_LEN 46


// the bgpmon related data for an XML message
typedef struct{
  char source_addr[ADDRESS_STRING_LEN];
  int  source_port;
  unsigned int source_asn;
  int source_asn_length;  
  char monitor_addr[ADDRESS_STRING_LEN];
  int  monitor_port;
  unsigned int monitor_asn;
  int monitor_asn_length;  
  char dest_addr[ADDRESS_STRING_LEN];
  int  dest_port;
  unsigned int dest_asn;
  int dest_asn_length;  
  unsigned int sequence;
  unsigned int asn_size;
} bgp_monitor_data;

/*-----------------------------------------------------------------------------
 * Purpose: entry fucntion which converts all types of BMF messages to XML
 *          text representations
 * input:   bmf - our internal BMF message
 *          xml - pointer to the buffer used for conversion
 *          maxlen - max length of the buffer
 * output:  the length of generated xml string
 * --------------------------------------------------------------------------*/
int BMF2XML(const BMF bmf, char *xml, const int maxlen, const void *monitorData);
xmlDocPtr genMSGDoc(const BMF bmf, const void* monitorData);

//for bgp xml headers
void genCollectionMethodNode(const BMF bmf, xmlNodePtr bgp_message);
xmlNodePtr genSourceNode(const BMF bmf,bgp_monitor_data *mon_data);
xmlNodePtr genDestNode(const BMF bmf,bgp_monitor_data *mon_data);
xmlNodePtr genMonitorNode(const BMF bmf,bgp_monitor_data *mon_data);
xmlNodePtr genObservedTimeNode(const BMF bmf);
xmlNodePtr genSequenceNumNode(const BMF bmf,bgp_monitor_data *state_data);
xmlNodePtr genOctetsNode(const BMF bmf);
xmlNodePtr genSkipAheadStatusNode(const BMF bmf);
xmlNodePtr genStatusNode(const BMF bmf, uint16_t type);
void addMetaData(const BMF, xmlDocPtr, xmlNodePtr, xmlNodePtr, bgp_monitor_data *);

// generation for nodes that are part of the BGP XSD
xmlNodePtr genBGPMSGNode(const BMF bmf,const xmlNsPtr ns, const int asn_len);
xmlNodePtr genAttNode(u_char *start, int* pos, const xmlNsPtr ns,int asn_len, int alen);
xmlNodePtr genWithNode(const u_char *start, int* pos,const xmlNsPtr ns);
xmlNodePtr genParseError(int position, const xmlNsPtr ns);
void genNodeAtts(xmlNodePtr node, const uint8_t flags, const uint8_t type);

//path attributes
xmlNodePtr genOriginNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos);
xmlNodePtr genASpathNode(xmlNodePtr asPathNode, 
              const uint16_t length, const u_char* start, uint16_t local_pos, 
              const xmlNsPtr ns, const int asn_len);
xmlNodePtr genNextHopNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos);
xmlNodePtr genMEDNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos);
xmlNodePtr genLocalPrefNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos);
xmlNodePtr genAggregatorNode(xmlNodePtr node, 
              const uint16_t length, u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genCommunityNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos, 
              const xmlNsPtr ns, uint8_t flags, const uint8_t type);
xmlNodePtr genOriginatorNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos);
xmlNodePtr genClusterListNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genMPReachNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genMPUnreachNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genExtendCommNode(xmlNodePtr node, 
              const uint16_t length, u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genAS4AggregatorNode(xmlNodePtr node, 
              const uint16_t length, u_char* start, uint16_t local_pos, const xmlNsPtr ns);
xmlNodePtr genUnknownExtendCommNode(xmlNodePtr node, 
              const uint16_t length, const u_char* start, const xmlNsPtr ns);


char* getAttType(const uint8_t type);
xmlNodePtr genExtComm(u_char *start, int* pos, const xmlNsPtr ns,int asn_len);
xmlNodePtr genNLRINode(const u_char *start, int* pos, const xmlNsPtr ns);

// helpers
int getPrefixString(const u_char* prefix, char* prefix_str, const uint32_t prefix_str_len, const int afi);
int getXMLAddressString(const u_char* addr, char* addr_str, const uint32_t addr_str_len, const int afi);
void sortPathAtts(xmlNodePtr* pathAtts, const int array_size);

#endif 
