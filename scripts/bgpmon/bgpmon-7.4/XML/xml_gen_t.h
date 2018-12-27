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
 *  File: xml_gen_t.h
 *  Authors: Catherine Olschanowsky
 *  Date: March 2012 
 */
#ifndef XML_GEN_T_H_
#define XML_GEN_T_H_

#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include <libxml/parser.h>
#include <libxml/xmlschemas.h>

#include "../Util/bgpmon_formats.h"
#include "xml_gen.h"

#define XSD_PATH "etc/bgp_monitor_2_00.xsd"
#define MY_ENCODING "ISO-8859-1"

/**Primary tests**/
void testXML_BMF2XML();
void testXML_BMF2XML_labeled();

/**Status Message TEsts**/
void test_generic_status();

/**Attribute Tests**/
void test_origin_attribute();// type 1
void test_as_path_attribute();// type 2
void test_next_hop_attribute();// type 3
void test_med_attribute(); // type 4
void test_local_pref_attribute();// type 5
void test_at_agg_attribute();//type 6
void test_aggregator_attribute();//type 7
void test_community_attribute();// type 8
void test_originator_id_attribute();//type 9
void test_cluster_list_attribute();//type 10
void test_nlri_attribute();//type 14
void test_mpreach_nlri_attribute();//type 14
void test_unreach_nlri_attribute();//type 15
void test_extend_comm_attribute(); // type 16
void test_as4_path_attribute();//type 17
void test_as4_aggregator_attribute();//type 18
void test_pmsi_tunnel_attribute(); // type 22
void test_tunnel_encap_attribute(); // type 23
void test_traffic_eng_attribute(); // type 24
void test_ipv6_addr_spec_attribute(); // type 25
void test_pe_dist_attribute(); // type 27
void test_bgp_entropy_attribute(); // type 28
void test_attr_set_attribute(); // type 128
void test_unknown_attribute(); // unknown type

/**Misc tests**/
void test_getXMLAddressString();

void test_skipAheadMessage();

/**Other Methods**/
int init_xml_gen(void);
int clean_xml_gen(void);

#endif
