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
 *  File: bgp_t.c
 *  Authors: Catherine Olschanowsky
 *  Date: Aug. 30, 2011
 */
#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include "site_defaults.h"
#include "Util/bgp_t.h"
#include "Util/log.h"
#include "Util/xml_help_t.h"
#include "Labeling/rtable_t.h"
#include "Mrt/mrtUtils_t.h"
#include "Mrt/mrtinstance_t.h"
#include "Util/backlogUtil_t.h"
#include "XML/xml_gen_t.h"
#include "Mrt/mrtProcessTable_t.h"

/* The main() function for setting up and running the tests.
 * Returns a CUE_SUCCESS on successful running, another
 * CUnit error code on failure.
 */
int 
main()
{

	init_log("test_driver", 0, 0, DEFAULT_LOG_FACILITY);
	CU_pSuite 	bgp_suite = NULL;
	/* CU_pSuite mrtUtil_suite = NULL;  */
	CU_pSuite 	backlogUtil_suite = NULL;
	/* CU_pSuite mrtInstance_suite = NULL; */
	CU_pSuite 	mrtProcessTable_suite = NULL;
	CU_pSuite 	rtable_suite = NULL;
	CU_pSuite 	xml_utils_suite = NULL;
	CU_pSuite 	xml_gen_suite = NULL;

	/* initialize the CUnit test registry */
	if (CUE_SUCCESS != CU_initialize_registry())
		return CU_get_error();

	/* add the suites to the registry */
	bgp_suite = CU_add_suite("BGP", init_bgp, clean_bgp);
	if (NULL == bgp_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	backlogUtil_suite = CU_add_suite("BacklkogUtil", init_mrtUtils, clean_mrtUtils);
	if (NULL == backlogUtil_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
/* mrtInstance_suite = CU_add_suite("MRTinstance", init_mrtinstance, clean_mrtinstance);
 if (NULL == mrtInstance_suite) {
    CU_cleanup_registry();
    return CU_get_error();
 }*/
	mrtProcessTable_suite = CU_add_suite("mrtProcessTable", init_ProcessTable, clean_ProcessTable);
	if (NULL == mrtProcessTable_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	rtable_suite = CU_add_suite("rtable", init_RTABLE, clean_RTABLE);
	if (NULL == rtable_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	xml_utils_suite = CU_add_suite("xml_utils", init_xml_test, clean_xml_test);
	if (NULL == xml_utils_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	xml_gen_suite = CU_add_suite("xml_gen", init_xml_gen, clean_xml_gen);
	if (NULL == xml_gen_suite) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	/* add the tests to the suites */
	if ((NULL == CU_add_test(bgp_suite, "test of BGP_createMessage",
				 testBGP_createMessage)) ||
	    NULL == CU_add_test(bgp_suite, "test of BGP_addWithdrawnRouteToUpdate",
				testBGP_addWithdrawnRouteToUpdate) ||
	    NULL == CU_add_test(bgp_suite, "test of BGP_addNLRIToUpdate",
				testBGP_addNLRIToUpdate) ||
	    NULL == CU_add_test(bgp_suite, "test of BGP_addPathAttributeToUpdate",
				testBGP_addPathAttributeToUpdate) ||
	    NULL == CU_add_test(bgp_suite, "test of BGP_calculateLength",
				testBGP_calculateLength) ||
	    NULL == CU_add_test(bgp_suite, "test of BGP_serialize",
				testBGP_serialize)) {

		CU_cleanup_registry();
		return CU_get_error();
	}
	if ((NULL == CU_add_test(backlogUtil_suite, "test_backlog_init", testMRT_backlog_init)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_MRT_backlog_write", testMRT_backlog_write)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_MRT_backlog_wrap", testMRT_backlog_wrap)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_MRT_backlog_fastforward", testMRT_backlog_fastforward)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_backlog_resize", testMRT_backlog_resize)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_MRT_backlog_read", testMRT_backlog_read)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_XML backlog_write", testXML_backlog_write)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_XML_backlog_fastforward", testXML_backlog_fastforward)) ||
	    (NULL == CU_add_test(backlogUtil_suite, "test_XML_backlog_read", testXML_backlog_read))) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	/*
	 * if (( NULL == CU_add_test(mrtInstance_suite,"test
	 * MRT_createTableBufferFromType13Subtype1",testMRT_createTableBufferFromType13Subtype1))
	 * || NULL == CU_add_test(mrtInstance_suite,"test
	 * MRT_processType13SubtypeSpecific",testMRT_processType13SubtypeSpecific) || NULL ==
	 * CU_add_test(mrtInstance_suite,"test
	 * MRT_processType16SubtypeMessage",testMRT_processType16SubtypeMessage)) {
	 * CU_cleanup_registry(); return CU_get_error(); }
	 */


	/* MRT Process Table Tests */
	if ((NULL == CU_add_test(mrtProcessTable_suite, "test of TABLE DUMP V1",
				 testProcessTable_TableDumpV1)) ||
	    (NULL == CU_add_test(mrtProcessTable_suite, "test of Table Dump V2 PEER_INDEX_TABLE sub-type",
				 testProcessTableDumpV2_PeerIndexTable)) ||
	    (NULL == CU_add_test(mrtProcessTable_suite, "test of Table Dump V2 RIB_SUBTYPE",
				 testProcessTableDumpV2_RIB_SUBTYPE)) ||
	    (NULL == CU_add_test(mrtProcessTable_suite, "test of Table Dump V2 RIB_GENERIC sub-type",
			     testProcessTableDumpV2_RIB_GENERIC_SUBTYPE)) ||
	    (NULL == CU_add_test(mrtProcessTable_suite, "test of valid IP Address string",
				 testIsValidIpAddress)) ||
	    (NULL == CU_add_test(mrtProcessTable_suite, "test of prefix packing function",
				 testPackPrefix))) {

		CU_cleanup_registry();
		return CU_get_error();
	}
	/* rtable tests */
	if ((NULL == CU_add_test(rtable_suite, "test of rtable_printPrefixV4",
				 testRTABLE_printPrefixV4)) ||
	  (NULL == CU_add_test(rtable_suite, "test of rtable_printPrefixV6",
			       testRTABLE_printPrefixV6)) ||
	(NULL == CU_add_test(rtable_suite, "test of rtable_stringToPrefixV4",
			     testRTABLE_stringToPrefixV4)) ||
	(NULL == CU_add_test(rtable_suite, "test of rtable_stringToPrefixV6",
			     testRTABLE_stringToPrefixV6))) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	/* xml_utils tests */
	if ((NULL == CU_add_test(xml_utils_suite, "test of copying xml strings",
				 testXML_copyNew))) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	/* xml_gen tests */
	if (
	    (NULL == CU_add_test(xml_gen_suite, "test of BMF2XML",
				 testXML_BMF2XML)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of labeled messages",
				 testXML_BMF2XML_labeled)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of status messages",
				 test_generic_status)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of origin attributes",	/* type 1 */
				 test_origin_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of AS path attributes",	/* type 2 */
				 test_as_path_attribute)) ||
	  (NULL == CU_add_test(xml_gen_suite, "test of Next Hop attributes",	/* type 3 */
			       test_next_hop_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of MED attributes",	/* type 4 */
				 test_med_attribute)) ||
	(NULL == CU_add_test(xml_gen_suite, "test of Local Pref attributes",	/* type 5 */
			     test_local_pref_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of Atomic Aggregate attributes",	/* type 6 */
				 test_at_agg_attribute)) ||
	(NULL == CU_add_test(xml_gen_suite, "test of Aggregator attributes",	/* type 7 */
			     test_aggregator_attribute)) ||
	 (NULL == CU_add_test(xml_gen_suite, "test of Community attributes",	/* type 8 */
			      test_community_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of Originator ID attributes",	/* type 9 */
				 test_originator_id_attribute)) ||
	/*
	 * (NULL == CU_add_test(xml_gen_suite, "test of Cluster List attributes",
	 * test_cluster_list_attribute))||
	 */
	    (NULL == CU_add_test(xml_gen_suite, "test of NLRI attributes",	/* type 14 */
				 test_nlri_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of MP_NLRI attributes",	/* type 14 */
				 test_mpreach_nlri_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of UNREACH NLRI attributes",	/* type 15 */
				 test_unreach_nlri_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of Extended Communities  attributes",	/* type 16 */
				 test_extend_comm_attribute)) ||
	  (NULL == CU_add_test(xml_gen_suite, "test of AS4_PATH attributes",	/* type 17 */
			       test_as4_path_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of AS4 AGGREGATOR attributes",	/* type 18 */
				 test_as4_aggregator_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of PMSI Tunnel  attributes",	/* type 22 */
				 test_pmsi_tunnel_attribute)) ||
	/*
	 * (NULL == CU_add_test(xml_gen_suite, "test of Tunnel encapsulation attributes",
	 * test_tunnel_encap_attribute)) ||
	 */
	    (NULL == CU_add_test(xml_gen_suite, "test of Traffic engineering attributes",	/* type 24 */
				 test_traffic_eng_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of IPv6 Address Specific Extende Community attributes",	/* type 25 */
				 test_ipv6_addr_spec_attribute)) ||
	    (NULL == CU_add_test(xml_gen_suite, "test of PE Distinguisher attributes",	/* type 27 */
				 test_pe_dist_attribute)) ||
	(NULL == CU_add_test(xml_gen_suite, "test of BGP Entropy attributes",	/* type 28 */
			     test_bgp_entropy_attribute)) ||
	  (NULL == CU_add_test(xml_gen_suite, "test of ATTR_SET attributes",	/* type 128 */
			       test_attr_set_attribute)) || */
	/*
	 * (NULL == CU_add_test(xml_gen_suite, "test of address string creation",
	 * test_getXMLAddressString)) ||
	 */
	    (NULL == CU_add_test(xml_gen_suite, "test of Unknown attributes",	/* unknown type */
				 test_unknown_attribute)) ||
	  (NULL == CU_add_test(xml_gen_suite, "test of skip ahead messages",
			       test_skipAheadMessage))
		) {
		CU_cleanup_registry();
		return CU_get_error();
	}
	/* Run all tests using the CUnit Basic interface */
	CU_basic_set_mode(CU_BRM_VERBOSE);
	CU_basic_run_tests();
	CU_cleanup_registry();
	return CU_get_error();
}
