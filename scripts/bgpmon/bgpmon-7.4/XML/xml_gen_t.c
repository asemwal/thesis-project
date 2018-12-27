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
 *  File: xmlGen_t.c
 *  Authors: Catherine Olschanowsky
 */
#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include <libxml/xpath.h>
#include <libxml/xpathInternals.h>
#include "xml_gen_t.h"
#include "../Queues/gen_skip_msg.h"



/***

  TODO - MAKE SURE AFTER EVERY FREE (EXCEPT IN THE BIG CASE) THAT THE POINTERS
  ARE SET TO NULL TO MAKE SURE WE'RE NOT TESTING DEAD MEMORY SPACE
***/










char           *xmlTestBuffer;
int 		max_len = 10000;

/****************************** TEST STRINGS **********************************
This section of test strings is meant to help make the test cases more easily
read. They can be chosen from the archives, from the octets and pasted in.
*******************************************************************************/

/* message with several withdrawl nodes */
char           *msg_1_str = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF006E020020185CF667185CF666185CF66A18D74157185CF669185CF66815C921A015C921A800334001010040021202080BE317C658F50B6200D10F450F450F4540030441318165C008100BE300020BE303E90BE317E00BE3189C18977612";
uint8_t        *msg_1;
/* message 2 is message 1 with labels */
char           *msg_2_str = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF006E020020185CF667185CF666185CF66A18D74157185CF669185CF66815C921A015C921A800334001010040021202080BE317C658F50B6200D10F450F450F4540030441318165C008100BE300020BE303E90BE317E00BE3189C1897761200010001000100010001000100010002";
uint8_t        *msg_2;
/* message 3 has an mp_reach component */
char           *msg_3_str = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF006E0200000057400101004002160205000402650000415F00000DDD00008C9A00008C9AC0070800008C9AADDEE9FE800E2C00020120200112F8000000000000000002170104FE80000000000000D6CA6DFFFE2055310030200104502030";
uint8_t        *msg_3;
/* message 4 has an mp_unreach component */
char           *msg_4_str = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF007802000000614001010040021202040004026500001B1B00000DDD000073A7400600C00708000073A740D36F06800E2C00020120200112F8000000000000000002170104FE80000000000000D6CA6DFFFE20553100302001067C01EC900F0008000201202A03BD20";
uint8_t        *msg_4;



/*****************************************************************************
                          Attribute Test Strings
*****************************************************************************/
/*type 1 */
char           *orig_test_str = "40010100";	/* well-known, mandantory */
uint8_t        *orig_test;

char           *orig_test_str2 = "40010000";	/* fails with bad length */
uint8_t        *orig_test2;

char           *orig_test_str3 = "400101FF";	/* fails with bad origin */
uint8_t        *orig_test3;

/*type 2 */
char           *aspath_test_str = "40021202080BE317C658F50B6200D10F450F450F454";
uint8_t        *aspath_test;

char           *aspath_test_str2 = "40020002080BE317C658F50B6200D10F450F450F454";	/* fails with bad length */
uint8_t        *aspath_test2;

char           *aspath_test_str3 = "4002120000000000000000000000000000000000000";	/* fails with bad
											 * segment type */
uint8_t        *aspath_test3;

char           *aspath_test_str4 = "4002120200000000000000000000D10F450F450F454";	/* will be used for
											 * failing at ASN length */
uint8_t        *aspath_test4;

char           *aspath_test_str5 = "40021202040003029000001B1B0000232A00003384";	/* has asn4's */
uint8_t        *aspath_test5;

/*type 3 */
char           *nexthop_test_str = "4003048017000D";
uint8_t        *nexthop_test;

char           *nexthop_test_str2 = "4003008017000D";	/* will fail for bad
							 * length */
uint8_t        *nexthop_test2;

/*type 4 */
char           *med_test_str = "80040401010101";
uint8_t        *med_test;

char           *med_test_str2 = "80040001010101";	/* will fail for bad
							 * length */
uint8_t        *med_test2;

char           *med_test_str3 = "8004040000000F";	/* will fail for bad
							 * length */
uint8_t        *med_test3;

/*type 5 */
char           *local_pref_test_str = "40050401010101";	/* loc_pref = 16843009 */
uint8_t        *local_pref_test;

char           *local_pref_test_str2 = "40050001010101";	/* should fail for bad
								 * length */
uint8_t        *local_pref_test2;

/*type 6 */
char           *atom_agg_test_str = "400600";	/* well-known, transitive,
						 * type 6, length 0 */
uint8_t        *atom_agg_pref_test;

/*type 7 */
char           *aggregator_test_str = "C007064D1CCC44AA01";	/* example 19740
								 * 28.17.84.162 */
uint8_t        *aggregator_test;

char           *aggregator_test_str2 = "C007002F718017000D";	/* should fail with bad
								 * length */
uint8_t        *aggregator_test2;

char           *aggregator_test_str3 = "C0070800002F0941160CFE";	/* example with as4
									 * 19740 28.17.84.162 */
uint8_t        *aggregator_test3;

/*type 8 */
char           *community_test_str = "C0080C2B9C04742B9C1EC836D900CA16D0461416D04E74";
uint8_t        *community_test;

char           *community_test_str2 = "C008002B9C04742B9C1EC836D900CA16D0461416D04E74";	/* sould fail with bad
											 * length */
uint8_t        *community_test2;

/*type 9 */
char           *originatorid_test_str = "8009048017000D";	/* contrived example
								 * similar to next hop
								 * //TODO */
uint8_t        *originatorid_test;

char           *originatorid_test_str2 = "8009008017000D";	/* should fail with bad
								 * length */
uint8_t        *originatorid_test2;

/*type 10 */
/*char* cluster_list_test_str = ""; //TODO find test case */
char           *cluster_list_test_str = "800A0C8017000D8017000E8017000F";	/* contrived example 3
										 * ids: 128.23.0.13,
										 * 128.23.0.14,
										 * 128.23.0.15 */
uint8_t        *cluster_list_test;

/*type 14 */
char           *nlri_test_str_1 = "18D18E8C";
uint8_t        *nlri_test_1;

char           *nlri_test_str_2 = "1529F940";
uint8_t        *nlri_test_2;


char           *mpnlri_test_str_1 = "900E001A000201102A03A480FFFFFFFF000000000000024700202A001A80";
uint8_t        *mpnlri_test_1;

char           *mpnlri_test_str_2 = "900E001F000201102A03A480FFFFFFFF00000000000002470020280600022028060003";
uint8_t        *mpnlri_test_2;

char           *mpnlri_test_str_3 = "900E00AC000201102C0FFC00000000000000000000000003002C2408802601E02C2408802601F02C2408802603802C2408802600702C2408802501802C2408802501902C2408802501A02C2408802600202C2408802600A02C2408802501202C2408802501102C2408802600B02C240880250280202408802620240880252C2408802606E02C2408802608902C2408802607002C2408802607102C2408802606F02C2408802608802C2408802607302C2408802608A02C2408802608B02424088000902124088024802C2408802608E02C2408802608D02C2408802609202C2408802609002C24088026085028240880F10128240880F1002C2408802608402C2408802608302C2408802608202C2408802608102C2408802608F02C2408802607602C2408802607B02C2408802607A02C2408802607C02C2408802607D02C2408802608602C2408802609102C2408802608002C2408802607F02C2408802607E02C2408802607902C2408802607802C2408802607702C2408802607402C2408802607502C2408802608702C2408802500C02C2408802602E02C2408802500002C2408802500E02C2408802500D02C2408802500802C2408802500702C2408802500102C2408802500B02C2408802606402C2408802605D02C2408802500602C2408802500A02C2408802606202C2408802501002C2408802500F02C2408802500502C2408802500302C2408802500402C2408802602F02C2408802603002C2408802603702C2408802501F02C2408802604202C2408802604102C2408802604502C2408802603E02C2408802604302C2408802603F02C2408802601C02C2408802601B02C2408802601A02C2408802501602C2408802605102C2408802502202C2408802601302C2408802601402C2408802601202C2408802502A02C2408802600602C2408802502302C2408802600502C2408802600402C2408802600302C2408802600802C2408802600902C2408802602202C2408802604F02C2408802605002C2408802502102C2408802501702C2408802602602C2408802602002C2408802602502C2408802602302C2408802605202C2408802502402C2408802502B02C2408802602402C2408802500202C2408802603D02C2408802603902C2408802502002C2408802502902C2408802602802C2408802602702C2408802501402C2408802501502C2408802501302C2408802601802C2408802605302C2408802605502C2408802606302C2408802601102C2408802600102C2408802605402C2408802606502C2408802601702C2408802501D02C2408802600F02C2408802601002C2408802606602C2408802604E02C2408802501E02C2408802600002C2408802606702C2408802601602C2408802604602C2408802606002C2408802605F02C2408802605E02C2408802605C02C2408802605B02C2408802605A02C2408802605902C2408802605802C2408802605702C2408802605602C2408802606802C2408802606902C2408802606A02C2408802606B02C2408802606C02C2408802606D02C2408802600C02C2408802600D02C2408802501B02C2408802501C02C2408802502502C2408802502602C2408802502702C2408802602902C2408802602A02C2408802602C02C2408802602D0";
/*REALLY long example that might be causing problems in production -TODO fully test this */
uint8_t        *mpnlri_test_3;

char           *mpnlri_test_str_4 = "800E16000201102607BE00000102400000000000000BF1003024048000B4B1302404800000843024048000008330240480000078302404800000723024048000007130240480000070302404800000303024048000002530240480000024302404800000233024048000002230240480000021302404800000203024048000001530240480000014302404800000133024048000001230240480000011302404800000103024048000000F3024048000000E3024048000000D3024048000000C3024048000000B3024048000000A302404800000093024048000000830240480000007302404800000063024048000000530240480000004302404800000033024048000000230240480000001302404800000002024048000";
uint8_t        *mpnlri_test_4;


/*type 15 */
char           *unreach_nlri_test_str = "900F000700010216C76D20";
uint8_t        *unreach_nlri_test;

char           *unreach_nlri_test_str_2 = "900F00170002012028060000202806000320280600022028060001";
uint8_t        *unreach_nlri_test_2;

/*type 16 */
char           *extend_comm_test_str = "C01008000236D90000138BB";
uint8_t        *extend_comm_test;

char           *extend_comm_test_str2 = "C0100800FF36D90000138B";	/* has fake subtype */
uint8_t        *extend_comm_test2;

char           *extend_comm_test_str3 = "C01008FFFF36D90000138B";	/* has fake type and
									 * subtype */
uint8_t        *extend_comm_test3;

/*type 17 */
char           *as4path_test_str = "C01122020800002F71000036D90000051300000DDD00006E080000CF430004021A00006EB4";
uint8_t        *as4path_test;

/*type 18 */
char           *as4_aggregator_test_str = "C012080002018B6704BC02";
uint8_t        *as4_aggregator_test;

/*type 22 */
char           *pmsi_tunnel_test_str = "C0160100";	/* TODO find test case -
							 * this is just to test
							 * the hex creation */
uint8_t        *pmsi_tunnel_test;

/*type 23 */
char           *tunnel_encap_test_str = "";	/* TODO find test case */
uint8_t        *tunnel_encap_test;

/*type 24 */
char           *traffic_eng_test_str = "";	/* TODO find test case */
uint8_t        *traffic_eng_test;

/*type 25 */
char           *ipv6_addr_spec_test_str = "";	/* TODO find test case */
uint8_t        *ipv6_addr_spec_test;

/*type 27 */
char           *pe_dist_test_str = "";	/* TODO find test case */
uint8_t        *pe_dist_test;

/*type 28 */
char           *bgp_entropy_test_str = "";	/* TODO find test case */
uint8_t        *bgp_entropy_test;

/*type 128 */
char           *attr_set_test_str = "";	/* TODO find test case */
uint8_t        *attr_set_test;


/*type unknown */
char           *unknown_test_str = "40FE048017000D";	/* is just the next hop
							 * test with FE instead
							 * of 03 as the type */
char           *unknown_test_str_2 = "10FE0001FF";	/* same as the last
							 * test, just twice with
							 * a fake of type FE and
							 * length 1 in the
							 * middle */
char           *unknown_test_str_3 = "90FE032C000201102404A10000000000000000000000000100302A01884000EF302A01884000EE302A01884000EB302A01884000EA302A01884000E7302A01884000E6302A01884000E3302A01884000E2302A01884000DF302A01884000DE302A01884000DB302A01884000DA302A01884000D7302A01884000D6302A01884000D3302A01884000D2302A01884000CF302A01884000CE302A01884000CB302A01884000CA302A01884000C7302A01884000C6302A01884000C3302A01884000C2302A01884000BF302A01884000BE302A01884000BB302A01884000BA302A01884000B7302A01884000B6302A01884000B3302A01884000B2302A01884000AF302A01884000AE302A01884000AB302A01884000AA302A01884000A7302A01884000A6302A01884000A3302A01884000A2302A018840009F302A018840009E302A018840009B302A018840009A302A0188400097302A0188400096302A0188400093302A0188400092302A018840008F302A018840008E302A018840008B302A018840008A302A0188400087302A0188400086302A0188400083302A0188400082302A018840007F302A018840007E302A018840007B302A018840007A302A0188400077302A0188400076302A0188400073302A0188400072302A018840006F302A018840006E302A018840006B302A018840006A302A0188400067302A0188400066302A0188400063302A0188400062302A018840005F302A018840005E302A018840005B302A018840005A302A0188400057302A0188400056302A0188400053302A0188400052302A018840004F302A018840004E302A018840004B302A018840004A302A0188400043302A0188400042302A018840003F302A018840003E302A018840003B302A018840003A302A0188400037302A0188400036302A0188400033302A0188400032302A018840002F302A018840002E302A018840002B302A018840002A302A0188400027302A0188400026302A0188400023302A0188400022302A018840001F302A018840001E302A018840001B302A018840001A302A0188400017302A0188400016302A0188400013302A0188400012302A0188400010302A0188400001302A0188400000";	/* really long test case
																																																																																																																																																																																																																		 * to test the creation
																																																																																																																																																																																																																		 * of hex. is the same
																																																																																																																																																																																																																		 * message as the long
																																																																																																																																																																																																																		 * mp_reach, but with a
																																																																																																																																																																																																																		 * fake type */
uint8_t        *unknown_test;
uint8_t        *unknown_test_2;
uint8_t        *unknown_test_3;



/*****************************************************************************
                            Misc. Test Strings
*****************************************************************************/

char           *ipv4_address_test_str = "01020304";
uint8_t        *ipv4_address_test;

char           *ipv6_address_test_str = "01020304010203040102030401020304";
uint8_t        *ipv6_address_test;

/*****************************************************************************
                            Skip Ahead Tests
*****************************************************************************/

SAM            *skipAheadInfo = NULL;
BMF 		skipAheadBMF = NULL;


/* a little helper function so that the test messages are more readable */
int 
str2Hex(char *string, uint8_t ** hex)
{
	*hex = calloc(strlen(string) / 2, sizeof(uint8_t));
	int 		i;
	int 		len = strlen(string);
	uint32_t 	u;
	for (i = 0; i < len / 2; i++) {
		sscanf(string + (2 * i), "%2x", &u);
		(*hex)[i] = u;
	}
	return i;
}

/* required by cunit for optional initilization */
int
init_xml_gen(void)
{
	xmlTestBuffer = (char *) calloc(max_len, sizeof(char));
	if (xmlTestBuffer == 0) {
		return 1;
	}
	memset(xmlTestBuffer, '\0', max_len);

	/* //convert the test inputs */

	/* test strings */
	str2Hex(msg_1_str, &msg_1);
	str2Hex(msg_2_str, &msg_2);
	str2Hex(msg_3_str, &msg_3);
	str2Hex(msg_4_str, &msg_4);

	/* attribute test strings */
	str2Hex(orig_test_str, &orig_test);	/* type 1 */
	str2Hex(orig_test_str2, &orig_test2);
	str2Hex(orig_test_str3, &orig_test3);
	str2Hex(aspath_test_str, &aspath_test);	/* type 2 */
	str2Hex(aspath_test_str2, &aspath_test2);
	str2Hex(aspath_test_str3, &aspath_test3);
	str2Hex(aspath_test_str4, &aspath_test4);
	str2Hex(aspath_test_str5, &aspath_test5);
	str2Hex(nexthop_test_str, &nexthop_test);	/* type 3 */
	str2Hex(nexthop_test_str2, &nexthop_test2);
	str2Hex(med_test_str, &med_test);	/* type 4 */
	str2Hex(med_test_str2, &med_test2);
	str2Hex(med_test_str3, &med_test3);
	str2Hex(local_pref_test_str, &local_pref_test);	/* type 5 */
	str2Hex(local_pref_test_str2, &local_pref_test2);
	str2Hex(atom_agg_test_str, &atom_agg_pref_test);	/* type 6 */
	str2Hex(aggregator_test_str, &aggregator_test);	/* type 7 */
	str2Hex(aggregator_test_str2, &aggregator_test2);
	str2Hex(aggregator_test_str3, &aggregator_test3);
	str2Hex(community_test_str, &community_test);	/* type 8 */
	str2Hex(community_test_str2, &community_test2);
	str2Hex(originatorid_test_str, &originatorid_test);	/* type 9 */
	str2Hex(originatorid_test_str2, &originatorid_test2);
	str2Hex(cluster_list_test_str, &cluster_list_test);	/* type 10 */
	str2Hex(nlri_test_str_1, &nlri_test_1);	/* type 14 */
	str2Hex(nlri_test_str_2, &nlri_test_2);
	str2Hex(mpnlri_test_str_1, &mpnlri_test_1);
	str2Hex(mpnlri_test_str_2, &mpnlri_test_2);
	str2Hex(mpnlri_test_str_3, &mpnlri_test_3);
	str2Hex(mpnlri_test_str_4, &mpnlri_test_4);
	str2Hex(unreach_nlri_test_str, &unreach_nlri_test);	/* type 15 */
	str2Hex(unreach_nlri_test_str_2, &unreach_nlri_test_2);	/* type 15 */
	str2Hex(extend_comm_test_str, &extend_comm_test);	/* type 16 */
	str2Hex(extend_comm_test_str2, &extend_comm_test2);
	str2Hex(extend_comm_test_str3, &extend_comm_test3);
	str2Hex(as4path_test_str, &as4path_test);	/* type 17 */
	str2Hex(as4_aggregator_test_str, &as4_aggregator_test);	/* type 18 */
	str2Hex(pmsi_tunnel_test_str, &pmsi_tunnel_test);	/* type 22 */
	str2Hex(tunnel_encap_test_str, &tunnel_encap_test);	/* type 23 */
	str2Hex(traffic_eng_test_str, &traffic_eng_test);	/* type 24 */
	str2Hex(ipv6_addr_spec_test_str, &ipv6_addr_spec_test);	/* type 25 */
	str2Hex(pe_dist_test_str, &pe_dist_test);	/* type 27 */
	str2Hex(bgp_entropy_test_str, &bgp_entropy_test);	/* type 28 */
	str2Hex(attr_set_test_str, &attr_set_test);	/* type 128 */
	str2Hex(unknown_test_str, &unknown_test);	/* type UNKNOWN */
	str2Hex(unknown_test_str_2, &unknown_test_2);
	str2Hex(unknown_test_str_3, &unknown_test_3);


	/* misc. test strings */
	str2Hex(ipv4_address_test_str, &ipv4_address_test);
	str2Hex(ipv6_address_test_str, &ipv6_address_test);

	/* skip ahead tests */
	skipAheadInfo = malloc(sizeof(SAM));
	skipAheadInfo->queueName = "TEST_QUEUE";
	skipAheadInfo->numMsgsSkipped = 5000;
	skipAheadBMF = createBMFWithData(0, BMF_TYPE_SKIP_AHEAD, skipAheadInfo);

	return 0;
}
/* required by cunit for optional cleanup */
int
clean_xml_gen(void)
{

	/* test strings */
	free(xmlTestBuffer);
	free(msg_1);
	free(msg_2);
	free(msg_3);
	free(msg_4);

	/* attribute test strings */
	free(orig_test);	/* type 1 */
	free(orig_test2);
	free(orig_test3);
	free(aspath_test);	/* type 2  */
	free(aspath_test2);
	free(aspath_test3);
	free(aspath_test4);
	free(aspath_test5);
	free(nexthop_test);	/* type 3 */
	free(nexthop_test2);
	free(med_test);		/* type 4 */
	free(med_test2);
	free(med_test3);
	free(local_pref_test);	/* type 5 */
	free(local_pref_test2);
	free(atom_agg_pref_test);	/* type 6 */
	free(aggregator_test);	/* type 7 */
	free(aggregator_test2);
	free(aggregator_test3);
	free(community_test);	/* type 8 */
	free(community_test2);
	free(originatorid_test);/* type 9 */
	free(originatorid_test2);
	free(cluster_list_test);/* type 10 */
	free(nlri_test_1);	/* tyep 14 */
	free(nlri_test_2);
	free(mpnlri_test_1);
	free(mpnlri_test_2);
	free(mpnlri_test_3);
	free(mpnlri_test_4);
	free(unreach_nlri_test);/* type 15 */
	free(unreach_nlri_test_2);	/* type 15 */
	free(extend_comm_test);	/* type 16 */
	free(extend_comm_test2);
	free(extend_comm_test3);
	free(as4path_test);	/* type 17 */
	free(as4_aggregator_test);	/* type 18 */
	free(pmsi_tunnel_test);	/* type 22 */
	free(tunnel_encap_test);/* type 23 */
	free(traffic_eng_test);	/* type 24 */
	free(ipv6_addr_spec_test);	/* type 25 */
	free(pe_dist_test);	/* type 27 */
	free(bgp_entropy_test);	/* type 28 */
	free(attr_set_test);	/* type 128 */
	free(unknown_test);	/* type UNKNOWN */
	free(unknown_test_2);
	free(unknown_test_3);

	/* misc test strings */
	free(ipv4_address_test);
	free(ipv6_address_test);

	/* skip ahead tests */
	destroyBMF(skipAheadBMF);

	return 0;
}


/*****************************************************************************
******************************************************************************
                            PRIMARY TEST CASES
******************************************************************************
*****************************************************************************/

/*
 *
*/
void
testXML_BMF2XML_labeled()
{

	/* create some state information to be included in the message */
	bgp_monitor_data state_data;
	strcpy(state_data.source_addr, "1.2.3.4");
	state_data.source_asn_length = 2;
	state_data.source_asn = 3;
	state_data.source_port = 179;
	strcpy(state_data.monitor_addr, "2.3.4.5");
	state_data.monitor_asn_length = 2;
	state_data.monitor_asn = 4;
	state_data.monitor_port = 178;
	strcpy(state_data.dest_addr, "3.4.5.6");
	state_data.dest_asn_length = 2;
	state_data.dest_asn = 5;
	state_data.dest_port = 177;
	state_data.sequence = 50000;
	state_data.asn_size = 2;

	/* create a simple BMF message to be written out */
	BMF 		testBMF = createBMF(0, BMF_TYPE_MSG_LABELED, NULL, 0);
	bgpmonMessageAppend(testBMF, msg_2, strlen(msg_2_str) / 2);

	memset(xmlTestBuffer, '\0', max_len);
	int 		bmf2xml = BMF2XML(testBMF, xmlTestBuffer, max_len, (void *) &state_data);
	CU_ASSERT(bmf2xml != 0);

	/* create a doc for validation */
	xmlInitParser();
	xmlDocPtr 	test_doc = xmlParseDoc(BAD_CAST xmlTestBuffer);

	/* open the xsd file for validation */
	xmlDocPtr 	schema_doc = xmlReadFile(XSD_PATH, NULL, 0);
	CU_ASSERT(schema_doc != NULL);
	xmlSchemaParserCtxtPtr parser_ctxt = xmlSchemaNewDocParserCtxt(schema_doc);
	CU_ASSERT(parser_ctxt != NULL);
	xmlSchemaPtr 	schema = xmlSchemaParse(parser_ctxt);
	CU_ASSERT(schema != NULL);
	xmlSchemaValidCtxtPtr valid_ctxt = xmlSchemaNewValidCtxt(schema);
	CU_ASSERT(valid_ctxt != NULL);
	/* this is the actual validation */
	CU_ASSERT((xmlSchemaValidateDoc(valid_ctxt, test_doc) == 0));

	/* do some xpath searches to be sure that the data was put in correctly */
	char           *xpathExpr =
	"//bgp:UPDATE[bgp:NLRI=\"151.118.18.0/24\"]/bgp:NLRI[@afi=\"1\"]";
	xmlXPathContextPtr xpathCtx;
	xmlXPathObjectPtr xpathObj;
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);

	xmlNodeSetPtr 	nodes = xpathObj->nodesetval;
	int 		size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size == 1);
	CU_ASSERT(nodes->nodeTab[0]->type == XML_ELEMENT_NODE);
	char           *value = (char *) xmlNodeGetContent(nodes->nodeTab[0]);
	CU_ASSERT(value != NULL);
	CU_ASSERT(0 == (strcmp("151.118.18.0/24", value)));
	free(value);

	xmlSchemaFreeValidCtxt(valid_ctxt);
	xmlSchemaFree(schema);
	xmlSchemaFreeParserCtxt(parser_ctxt);
	xmlFreeDoc(schema_doc);
	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);
	xmlFreeDoc(test_doc);
	xmlCleanupParser();

	destroyBMF(testBMF);

}

void
testXML_BMF2XML()
{


	/* boilerplate to be used for several tests */
	/* create some state information to be included in the message */
	bgp_monitor_data state_data;
	strcpy(state_data.source_addr, "1.2.3.4");
	state_data.source_asn_length = 2;
	state_data.source_asn = 3;
	state_data.source_port = 179;
	strcpy(state_data.monitor_addr, "2.3.4.5");
	state_data.monitor_asn_length = 2;
	state_data.monitor_asn = 4;
	state_data.monitor_port = 178;
	strcpy(state_data.dest_addr, "3.4.5.6");
	state_data.dest_asn_length = 2;
	state_data.dest_asn = 5;
	state_data.dest_port = 177;
	state_data.sequence = 50000;
	state_data.asn_size = 4;

	/* open the xsd file for validation */
	xmlDocPtr 	schema_doc = xmlReadFile(XSD_PATH, NULL, 0);
	CU_ASSERT(schema_doc != NULL);
	xmlSchemaParserCtxtPtr parser_ctxt = xmlSchemaNewDocParserCtxt(schema_doc);
	CU_ASSERT(parser_ctxt != NULL);
	xmlSchemaPtr 	schema = xmlSchemaParse(parser_ctxt);
	CU_ASSERT(schema != NULL);
	xmlSchemaValidCtxtPtr valid_ctxt = xmlSchemaNewValidCtxt(schema);
	CU_ASSERT(valid_ctxt != NULL);

	/* TEST 1: has NLRI and Withdraw */
	BMF 		testBMF = createBMF(0, BMF_TYPE_MSG_FROM_PEER, NULL, 0);
	bgpmonMessageAppend(testBMF, msg_1, strlen(msg_1_str) / 2);
	memset(xmlTestBuffer, '\0', max_len);
	int 		bmf2xml = BMF2XML(testBMF, xmlTestBuffer, max_len, (void *) &state_data);
	CU_ASSERT(bmf2xml != 0);
	/* create a doc for validation */
	xmlInitParser();
	xmlDocPtr 	test_doc = xmlParseDoc(BAD_CAST xmlTestBuffer);
	/* printf("Buffer is %s",xmlTestBuffer); */

	/* this is the actual validation */
	CU_ASSERT((xmlSchemaValidateDoc(valid_ctxt, test_doc) == 0));

	/* do some xpath searches to be sure that the data was put in correctly */
	char           *xpathExpr =
	"//bgp:UPDATE[bgp:NLRI=\"151.118.18.0/24\"]/bgp:NLRI[@afi=\"1\"]";
	xmlXPathContextPtr xpathCtx;
	xmlXPathObjectPtr xpathObj;
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);

	/* check that there is a single result */
	xmlNodeSetPtr 	nodes = xpathObj->nodesetval;
	int 		size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size == 1);
	if (size == 1) {
		CU_ASSERT(nodes->nodeTab[0]->type == XML_ELEMENT_NODE);
		xmlChar        *value = xmlNodeGetContent(nodes->nodeTab[0]);
		CU_ASSERT(value != NULL);
		CU_ASSERT(0 == (strcmp("151.118.18.0/24", (char *) value)));
		free(value);
	}
	xmlXPathFreeObject(xpathObj);

	/* check that there are no results */
	xpathObj = xmlXPathEvalExpression(BAD_CAST "//METADATA", xpathCtx);
	CU_ASSERT(xpathObj != NULL);
	nodes = xpathObj->nodesetval;
	size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size == 0);

	/* cleanup before next test */
	xmlXPathFreeContext(xpathCtx);
	xmlXPathFreeObject(xpathObj);
	xmlFreeDoc(test_doc);
	destroyBMF(testBMF);


	/* Test 2:  a message with MP_REACH */
	state_data.asn_size = 4;
	testBMF = createBMF(0, BMF_TYPE_MSG_FROM_PEER, NULL, 0);
	bgpmonMessageAppend(testBMF, msg_3, strlen(msg_3_str) / 2);

	memset(xmlTestBuffer, '\0', max_len);
	bmf2xml = BMF2XML(testBMF, xmlTestBuffer, max_len, (void *) &state_data);
	CU_ASSERT(bmf2xml != 0);
	xmlInitParser();
	test_doc = xmlParseDoc(BAD_CAST xmlTestBuffer);
	/* printf("Buffer is %s",xmlTestBuffer); */

	/* this is the actual validation */
	CU_ASSERT((xmlSchemaValidateDoc(valid_ctxt, test_doc) == 0));

	/* do some xpath searches to be sure that the data was put in correctly */
	xpathExpr = "//bgp:MP_NLRI";
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);
	nodes = xpathObj->nodesetval;
	size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size > 0);

	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);

	xpathExpr = "//bgp:WITHDRAW";
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);
	nodes = xpathObj->nodesetval;
	size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size == 0);

	/* cleanup from xpath */
	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);

	/* cleanup from document creation */
	xmlFreeDoc(test_doc);
	destroyBMF(testBMF);

	/* Test 3:  a message with MP_UNREACH */
	state_data.asn_size = 4;
	testBMF = createBMF(0, BMF_TYPE_MSG_FROM_PEER, NULL, 0);
	int 		len = strlen(msg_4_str) / 2;
	bgpmonMessageAppend(testBMF, msg_4, len);

	memset(xmlTestBuffer, '\0', max_len);
	bmf2xml = BMF2XML(testBMF, xmlTestBuffer, max_len, (void *) &state_data);
	CU_ASSERT(bmf2xml != 0);
	xmlInitParser();
	test_doc = xmlParseDoc(BAD_CAST xmlTestBuffer);
	/* printf("Buffer is %s",xmlTestBuffer); */

	/* this is the actual validation */
	CU_ASSERT((xmlSchemaValidateDoc(valid_ctxt, test_doc) == 0));

	/* do some xpath searches to be sure that the data was put in correctly */
	xpathExpr = "//bgp:MP_NLRI";
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);
	nodes = xpathObj->nodesetval;
	size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size > 0);

	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);

	xpathExpr = "//bgp:WITHDRAW";
	xpathCtx = xmlXPathNewContext(test_doc);
	CU_ASSERT(xpathCtx != NULL);
	CU_ASSERT(0 == xmlXPathRegisterNs(xpathCtx, BAD_CAST "bgp", BAD_CAST _XFB_NS));
	xpathObj = xmlXPathEvalExpression(BAD_CAST xpathExpr, xpathCtx);
	CU_ASSERT(xpathObj != NULL);
	nodes = xpathObj->nodesetval;
	size = (nodes) ? nodes->nodeNr : 0;
	CU_ASSERT(size == 0);

	/* cleanup from xpath */
	xmlXPathFreeObject(xpathObj);
	xmlXPathFreeContext(xpathCtx);

	/* cleanup from document creation */
	xmlFreeDoc(test_doc);
	destroyBMF(testBMF);

	/* cleanup from schema validation  */
	xmlSchemaFreeValidCtxt(valid_ctxt);
	xmlSchemaFree(schema);
	xmlSchemaFreeParserCtxt(parser_ctxt);
	xmlFreeDoc(schema_doc);
	xmlCleanupParser();


}


/*****************************************************************************
******************************************************************************
                         STATUS MESSAGE TEST CASES
******************************************************************************
*****************************************************************************/
void
test_generic_status()
{				/*
	    char* msg = "TEST MESSAGE";
	    int len = strlen(msg);
	    uint16_t type = BMF_TYPE_QUEUES_STATUS;
	    BMF bmf = createBMF(0, type, msg, len);
	    CU_ASSERT(bmf != NULL);
	  
	    xmlNodePtr statusNode = genStatusNode(bmf, type);
	    CU_ASSERT(bmf != NULL);
	  
	    CU_ASSERT(strcmp((char*)statusNode->name, "STATUS") == 0);
	  
	    char* c = (char*)xmlNodeGetContent(statusNode);
	    CU_ASSERT(strcmp(c, "QUEUES_STATUS TEST MESSAGE") == 0);
	    free(c);
	  
	    /*cleaning up */
	destroyBMF(bmf);
	xmlFreeNode(statusNode);
	*/
}




/*****************************************************************************
******************************************************************************
                            ATTRIBUTE TEST CASES
******************************************************************************
*****************************************************************************/

void				/* type 1 */
test_origin_attribute()
{

	/* Testing first string */
	int 		start = 0;
	xmlNodePtr 	originNode = genAttNode(orig_test, &start, NULL, 2, 6);
	start = 0;
	xmlNodePtr 	originNode2 = genAttNode(orig_test2, &start, NULL, 2, 6);
	start = 0;
	xmlNodePtr 	originNode3 = genAttNode(orig_test3, &start, NULL, 2, 6);

	CU_ASSERT(originNode != NULL);

	CU_ASSERT(strcmp((char *) originNode->name, "ORIGIN") == 0);

	char           *content = (char *) xmlNodeGetContent(originNode);
	CU_ASSERT(strcmp(content, "IGP") == 0);
	free(content);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) originNode->properties);
	CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "false" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) originNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);

	xmlFreeNode(originNode);

	/* Testing second String */
	/* should return null for there is a bad length */
	CU_ASSERT(originNode2 == NULL);

	/* Testing third String */
	char           *c = (char *) xmlNodeGetContent(originNode3);
	CU_ASSERT(strcmp(c, "OTHER") == 0);
	free(c);
	xmlFreeNode(originNode3);
}


void				/* type 2 */
test_as_path_attribute()
{
	/* Testing first string */
	int 		start = 0;

	xmlNodePtr 	aspathNode = genAttNode(aspath_test, &start, NULL, 2, 22);
	start = 0;
	xmlNodePtr 	aspathNode2 = genAttNode(aspath_test2, &start, NULL, 2, 22);
	start = 0;
	xmlNodePtr 	aspathNode3 = genAttNode(aspath_test3, &start, NULL, 2, 22);
	start = 0;
	xmlNodePtr 	aspathNode4 = genAttNode(aspath_test4, &start, NULL, 666, 22);
	start = 0;
	xmlNodePtr 	aspathNode5 = genAttNode(aspath_test5, &start, NULL, 4, 22);

	CU_ASSERT(aspathNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) aspathNode->name, "AS_PATH") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) aspathNode->properties);
	CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "false" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) aspathNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);


	xmlNodePtr 	asSegNode = aspathNode->children;
	CU_ASSERT(strcmp((char *) asSegNode->name, "AS_SEQUENCE") == 0);

	/* test sould have 4 children.  Let's test them all! */
	xmlNodePtr 	as2node1 = asSegNode->children;
	xmlNodePtr 	as2node2 = as2node1->next;
	xmlNodePtr 	as2node3 = as2node2->next;
	xmlNodePtr 	as2node4 = as2node3->next;
	CU_ASSERT(strcmp((char *) as2node1->name, "ASN2") == 0);
	CU_ASSERT(strcmp((char *) as2node2->name, "ASN2") == 0);
	CU_ASSERT(strcmp((char *) as2node3->name, "ASN2") == 0);
	CU_ASSERT(strcmp((char *) as2node4->name, "ASN2") == 0);


	char           *content1 = (char *) xmlNodeGetContent(as2node1);
	char           *content2 = (char *) xmlNodeGetContent(as2node2);
	char           *content3 = (char *) xmlNodeGetContent(as2node3);
	char           *content4 = (char *) xmlNodeGetContent(as2node4);
	CU_ASSERT(strcmp(content1, "3043") == 0);
	CU_ASSERT(strcmp(content2, "6086") == 0);
	CU_ASSERT(strcmp(content3, "22773") == 0);
	CU_ASSERT(strcmp(content4, "2914") == 0);

	free(content1);
	free(content2);
	free(content3);
	free(content4);

	xmlFreeNode(aspathNode);

	/* Testing second string */
	/* should fail with bad length */
	CU_ASSERT(aspathNode2 == NULL);

	/* Testing third string */
	/* should fail with bad length */
	CU_ASSERT(aspathNode3 == NULL);

	/* Testing fourth string */
	/* should fail with bad AS type */
	CU_ASSERT(aspathNode4 == NULL);


	CU_ASSERT(aspathNode5 != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) aspathNode5->name, "AS_PATH") == 0);

	char           *optional2 = (char *) xmlNodeGetContent((xmlNodePtr) aspathNode5->properties);
	CU_ASSERT(strcmp(optional2, "false") == 0);	/* optional is "false" */
	free(optional2);

	char           *transitive2 = (char *) xmlNodeGetContent((xmlNodePtr) aspathNode5->properties->next);
	CU_ASSERT(strcmp(transitive2, "true") == 0);	/* transitive is "true" */
	free(transitive2);


	xmlNodePtr 	asSegNodea = aspathNode5->children;
	CU_ASSERT(strcmp((char *) asSegNodea->name, "AS_SEQUENCE") == 0);

	/* test sould have 4 children.  Let's test them all! */
	xmlNodePtr 	as2node1a = asSegNodea->children;
	xmlNodePtr 	as2node2a = as2node1a->next;
	xmlNodePtr 	as2node3a = as2node2a->next;
	xmlNodePtr 	as2node4a = as2node3a->next;
	CU_ASSERT(strcmp((char *) as2node1a->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as2node2a->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as2node3a->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as2node4a->name, "ASN4") == 0);


	char           *content1a = (char *) xmlNodeGetContent(as2node1a);
	char           *content2a = (char *) xmlNodeGetContent(as2node2a);
	char           *content3a = (char *) xmlNodeGetContent(as2node3a);
	char           *content4a = (char *) xmlNodeGetContent(as2node4a);
	CU_ASSERT(strcmp(content1a, "197264") == 0);
	CU_ASSERT(strcmp(content2a, "6939") == 0);
	CU_ASSERT(strcmp(content3a, "9002") == 0);
	CU_ASSERT(strcmp(content4a, "13188") == 0);

	free(content1a);
	free(content2a);
	free(content3a);
	free(content4a);

	xmlFreeNode(aspathNode5);
}



void				/* type 3 */
test_next_hop_attribute()
{

	/* Testing first string */
	int 		start = 0;

	xmlNodePtr 	nexthopNode = genAttNode(nexthop_test, &start, NULL, 2, 7);
	start = 0;
	xmlNodePtr 	nexthopnode2 = genAttNode(nexthop_test2, &start, NULL, 2, 7);

	CU_ASSERT(nexthopNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) nexthopNode->name, "NEXT_HOP") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) nexthopNode->properties);
	CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "false" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) nexthopNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);


	char           *content = (char *) xmlNodeGetContent(nexthopNode);
	CU_ASSERT(strcmp(content, "128.23.0.13") == 0);
	free(content);

	/* Testing for afi */
	xmlNodePtr 	afiNode = (xmlNodePtr) nexthopNode->properties->next->next->next->next->next;
	char           *afi = (char *) xmlNodeGetContent(afiNode);
	CU_ASSERT(strcmp(afi, "1") == 0);
	free(afi);

	xmlFreeNode(nexthopNode);

	/* Testing second string */
	/* should fail with bad length */
	CU_ASSERT(nexthopnode2 == NULL);

}


void				/* type 4 */
test_med_attribute()
{
	/* Testing first string */
	int 		start = 0;

	xmlNodePtr 	medNode = genAttNode(med_test, &start, NULL, 2, 7);
	start = 0;
	xmlNodePtr 	medNode2 = genAttNode(med_test2, &start, NULL, 2, 7);
	start = 0;
	xmlNodePtr 	medNode3 = genAttNode(med_test3, &start, NULL, 2, 7);

	CU_ASSERT(medNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) medNode->name, "MULTI_EXIT_DISC") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) medNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) medNode->properties->next);
	CU_ASSERT(strcmp(transitive, "false") == 0);	/* transitive is "false" */
	free(transitive);


	char           *content = (char *) xmlNodeGetContent(medNode);
	CU_ASSERT(strcmp(content, "16843009") == 0);
	free(content);

	xmlFreeNode(medNode);

	/* Another test string for validating value of multi exit discriminator */
	char           *content3 = (char *) xmlNodeGetContent(medNode3);
	CU_ASSERT(strcmp(content3, "15") == 0);
	free(content3);

	xmlFreeNode(medNode3);

	/* Testing second string */
	/* should fail with bad length */
	CU_ASSERT(medNode2 == NULL);


}


void				/* type 5 */
test_local_pref_attribute()
{
	/* Testing fist string */

	int 		start = 0;
	xmlNodePtr 	locprefNode = genAttNode(local_pref_test, &start, NULL, 2, 7);
	start = 0;
	xmlNodePtr 	locprefNode2 = genAttNode(local_pref_test2, &start, NULL, 2, 7);

	CU_ASSERT(locprefNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) locprefNode->name, "LOCAL_PREF") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) locprefNode->properties);
	CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "false" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) locprefNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);

	char           *content = (char *) xmlNodeGetContent(locprefNode);
	CU_ASSERT(strcmp(content, "16843009") == 0);
	free(content);

	xmlFreeNode(locprefNode);

	/* Testing second strng */
	/* should fail with bad length */
	CU_ASSERT(locprefNode2 == NULL);
}


void				/* type 6 */
test_at_agg_attribute()
{

	int 		start = 0;

	xmlNodePtr 	atAggNode = genAttNode(atom_agg_pref_test, &start, NULL, 2, 3);

	CU_ASSERT(atAggNode != NULL);	/* making sure we have the node back */
	CU_ASSERT(strcmp((char *) atAggNode->name, "ATOMIC_AGGREGATE") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) atAggNode->properties);
	CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "false" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) atAggNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);

	xmlFreeNode(atAggNode);

}



void				/* type 7 */
test_aggregator_attribute()
{
	/* testing first string */
	int 		start = 0;

	xmlNodePtr 	aggNode = genAttNode(aggregator_test, &start, NULL, 2, 9);
	start = 0;
	xmlNodePtr 	aggNode2 = genAttNode(aggregator_test2, &start, NULL, 2, 9);
	start = 0;
	xmlNodePtr 	aggNode3 = genAttNode(aggregator_test3, &start, NULL, 4, 9);

	CU_ASSERT(aggNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) aggNode->name, "AGGREGATOR") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) aggNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) aggNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);

	xmlNodePtr 	asn_node = aggNode->children;
	xmlNodePtr 	ip_node = asn_node->next;

	char           *asnContent = (char *) xmlNodeGetContent(asn_node);
	CU_ASSERT(strcmp(asnContent, "19740") == 0);
	free(asnContent);

	char           *ipContent = (char *) xmlNodeGetContent(ip_node);
	CU_ASSERT(strcmp(ipContent, "204.68.170.1") == 0);
	free(ipContent);

	xmlFreeNode(aggNode);

	/* Testing second string */
	/* should fail with bad length */
	CU_ASSERT(aggNode2 == NULL);

	if (aggNode2 != NULL) {
		return;
	}
	/* Testing third string */

	CU_ASSERT(aggNode3 != NULL);
	CU_ASSERT(strcmp((char *) aggNode3->name, "AGGREGATOR") == 0);

	char           *optional2 = (char *) xmlNodeGetContent((xmlNodePtr) aggNode3->properties);
	CU_ASSERT(strcmp(optional2, "true") == 0);	/* optional is "true" */
	free(optional2);

	char           *transitive2 = (char *) xmlNodeGetContent((xmlNodePtr) aggNode3->properties->next);
	CU_ASSERT(strcmp(transitive2, "true") == 0);	/* transitive is "true" */
	free(transitive2);

	xmlNodePtr 	asn_node2 = aggNode3->children;
	xmlNodePtr 	ip_node2 = asn_node2->next;

	char           *asnContent2 = (char *) xmlNodeGetContent(asn_node2);
	CU_ASSERT(strcmp(asnContent2, "12041") == 0);
	free(asnContent2);

	char           *ipContent2 = (char *) xmlNodeGetContent(ip_node2);
	CU_ASSERT(strcmp(ipContent2, "65.22.12.254") == 0);
	free(ipContent2);


	xmlFreeNode(aggNode3);


}

void				/* type 8 */
test_community_attribute()
{
	/* testing first string */
	int 		start = 0;
	xmlNodePtr 	commNode = genAttNode(community_test, &start, NULL, 2, 23);
	start = 0;
	xmlNodePtr 	commNode4 = genAttNode(community_test2, &start, NULL, 2, 23);

	CU_ASSERT(commNode != NULL);	/* making sure we have the node back */


	CU_ASSERT(strcmp((char *) commNode->name, "COMMUNITY") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) commNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) commNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);



	xmlNodePtr 	commNode2 = (xmlNodePtr) commNode->next;
	xmlNodePtr 	commNode3 = (xmlNodePtr) commNode2->next;

	/* has 3 communities */
	/* as 11164, value 1140 */
	/* as 11164, value 7880 */
	/* as 14041, value 202 */

	CU_ASSERT(strcmp((char *) commNode2->name, "COMMUNITY") == 0);
	CU_ASSERT(strcmp((char *) commNode3->name, "COMMUNITY") == 0);

	char           *asn1 = (char *) xmlNodeGetContent(commNode->children);
	char           *value1 = (char *) xmlNodeGetContent(commNode->children->next);
	char           *asn2 = (char *) xmlNodeGetContent(commNode2->children);
	char           *value2 = (char *) xmlNodeGetContent(commNode2->children->next);
	char           *asn3 = (char *) xmlNodeGetContent(commNode3->children);
	char           *value3 = (char *) xmlNodeGetContent(commNode3->children->next);

	CU_ASSERT(strcmp(asn1, "11164") == 0);
	CU_ASSERT(strcmp(value1, "1140") == 0);
	CU_ASSERT(strcmp(asn2, "11164") == 0);
	CU_ASSERT(strcmp(value2, "7880") == 0);
	CU_ASSERT(strcmp(asn3, "14041") == 0);
	CU_ASSERT(strcmp(value3, "202") == 0);


	free(asn1);
	free(value1);
	free(asn2);
	free(value2);
	free(asn3);
	free(value3);

	xmlFreeNodeList(commNode);

	/* testing second string */
	/* should fail with bad length */
	CU_ASSERT(commNode4 == NULL);

}


void				/* type 9 */
test_originator_id_attribute()
{
	/* testing first string */
	int 		start = 0;

	xmlNodePtr 	origNode = genAttNode(originatorid_test, &start, NULL, 2, 7);
	start = 0;
	xmlNodePtr 	origNode2 = genAttNode(originatorid_test2, &start, NULL, 2, 7);

	CU_ASSERT(origNode != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) origNode->name, "ORIGINATOR_ID") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) origNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) origNode->properties->next);
	CU_ASSERT(strcmp(transitive, "false") == 0);	/* transitive is "false" */
	free(transitive);


	char           *content = (char *) xmlNodeGetContent(origNode);
	CU_ASSERT(strcmp(content, "128.23.0.13") == 0);
	free(content);

	/* Testing for afi */
	xmlNodePtr 	afiNode = (xmlNodePtr) origNode->properties->next->next->next->next->next;
	char           *afi = (char *) xmlNodeGetContent(afiNode);
	CU_ASSERT(strcmp(afi, "1") == 0);
	free(afi);

	xmlFreeNode(origNode);

	/* testing second string */
	/* should fail with bad length */
	CU_ASSERT(origNode2 == NULL);

}


void				/* type 10 */
test_cluster_list_attribute()
{
	int 		start = 0;

/*#ifdef FIND_BGP_ODDITIES
  xmlNodePtr clNode = genAttNode(cluster_list_test, &start, NULL, 2, 15, NULL);
#else*/
	xmlNodePtr 	clNode = genAttNode(cluster_list_test, &start, NULL, 2, 15);
/*#endif */
	CU_ASSERT(clNode != NULL);	/* making sure we have the node back */
	if (clNode != NULL) {
		/*
		 * CU_ASSERT(strcmp((char*)clNode->name, "CLUSTER_LIST") == 0);
		 * 
		 * char* optional = (char*)xmlNodeGetContent( (xmlNodePtr) clNode->properties);
		 * CU_ASSERT(strcmp(optional, "true") == 0); /*optional is "true"
		 */
		free(optional);

		char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) clNode->properties->next);
		CU_ASSERT(strcmp(transitive, "false") == 0);	/* transitive is "false" */
		free(transitive);


		/* Three id's: 128.23.0.13, 128.23.0.14, 128.23.0.15 */
		xmlNodePtr 	cid1 = (xmlNodePtr) clNode->children;
		xmlNodePtr 	cid2 = (xmlNodePtr) cid1->next;
		xmlNodePtr 	cid3 = (xmlNodePtr) cid2->next;

		char           *cid1str = (char *) xmlNodeGetContent(cid1);
		char           *cid2str = (char *) xmlNodeGetContent(cid2);
		char           *cid3str = (char *) xmlNodeGetContent(cid3);

		CU_ASSERT(strcmp(cid1str, "128.23.0.13") == 0);
		CU_ASSERT(strcmp(cid2str, "128.23.0.14") == 0);
		CU_ASSERT(strcmp(cid3str, "128.23.0.15") == 0);


		/* TODO create test afi's */


		free(cid1str);
		free(cid2str);
		free(cid3str);
		*/
			xmlFreeNode(clNode);
	}
}

void				/* type 14 - NLRI nodes */
test_nlri_attribute()
{
	int 		pos = 0;
	xmlNodePtr 	nlri_node = genNLRINode(nlri_test_1, &pos, NULL);
	CU_ASSERT(nlri_node != NULL);
	if (nlri_node == NULL) {
		return;
	}
	char           *pContent = (char *) xmlNodeGetContent(nlri_node);
	CU_ASSERT(strcmp(pContent, "209.142.140.0/24") == 0);
	free(pContent);
	xmlFreeNode(nlri_node);

	pos = 0;
	nlri_node = genNLRINode(nlri_test_2, &pos, NULL);
	CU_ASSERT(nlri_node != NULL);
	if (nlri_node == NULL) {
		return;
	}
	pContent = (char *) xmlNodeGetContent(nlri_node);
	CU_ASSERT(strcmp(pContent, "41.249.64.0/21") == 0);
	free(pContent);
	xmlFreeNode(nlri_node);

}

void				/* type 14 - The whole MP_REACH_NLRI nodes */
test_mpreach_nlri_attribute()
{

	/* Testing first string */
	int 		pos = 0;
	xmlNodePtr 	mpreach = genAttNode(mpnlri_test_1, &pos, NULL, 4, 312);
	CU_ASSERT(mpreach != NULL);
	if (mpreach == NULL) {
		return;
	}
	CU_ASSERT(strcmp((char *) mpreach->name, "MP_REACH_NLRI") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) mpreach->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) mpreach->properties->next);
	CU_ASSERT(strcmp(transitive, "false") == 0);	/* transitive is "true" */
	free(transitive);

	CU_ASSERT(strcmp((char *) mpreach->children->name, "MP_NEXT_HOP") == 0);
	char           *pContent = (char *) xmlNodeGetContent(mpreach->children);
	CU_ASSERT(strcmp(pContent, "2a03:a480:ffff:ffff::247") == 0);
	free(pContent);

	CU_ASSERT(strcmp((char *) mpreach->children->next->name, "MP_NLRI") == 0);
	char           *pContent2 = (char *) xmlNodeGetContent(mpreach->children->next);
	CU_ASSERT(strcmp(pContent2, "2a00:1a80::/32") == 0);
	free(pContent2);

	xmlFreeNode(mpreach);

	/* Testing second string */
	pos = 0;
	xmlNodePtr 	mpreach2 = genAttNode(mpnlri_test_2, &pos, NULL, 4, 312);
	CU_ASSERT(mpreach2 != NULL);
	if (mpreach2 == NULL) {
		return;
	}
	CU_ASSERT(strcmp((char *) mpreach2->name, "MP_REACH_NLRI") == 0);

	char           *optional3 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach2->properties);
	CU_ASSERT(strcmp(optional3, "true") == 0);	/* optional is "true" */
	free(optional3);

	char           *transitive3 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach2->properties->next);
	CU_ASSERT(strcmp(transitive3, "false") == 0);	/* transitive is "true" */
	free(transitive3);

	CU_ASSERT(strcmp((char *) mpreach2->children->name, "MP_NEXT_HOP") == 0);
	char           *pContent3 = (char *) xmlNodeGetContent(mpreach2->children);
	CU_ASSERT(strcmp(pContent3, "2a03:a480:ffff:ffff::247") == 0);
	free(pContent3);

	CU_ASSERT(strcmp((char *) mpreach2->children->next->name, "MP_NLRI") == 0);
	char           *pContent4 = (char *) xmlNodeGetContent(mpreach2->children->next);
	CU_ASSERT(strcmp(pContent4, "2806:2::/32") == 0);
	free(pContent4);

	CU_ASSERT(strcmp((char *) mpreach2->children->next->next->name, "MP_NLRI") == 0);
	char           *pContent5 = (char *) xmlNodeGetContent(mpreach2->children->next->next);
	CU_ASSERT(strcmp(pContent5, "2806:3::/32") == 0);
	free(pContent5);

	xmlFreeNode(mpreach2);

	/* Testing third string */
	pos = 0;
	xmlNodePtr 	mpreach3 = genAttNode(mpnlri_test_3, &pos, NULL, 4, 312);
	CU_ASSERT(mpreach3 != NULL);
	if (mpreach3 == NULL) {
		return;
	}
	CU_ASSERT(strcmp((char *) mpreach3->name, "MP_REACH_NLRI") == 0);

	char           *optional9 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach3->properties);
	CU_ASSERT(strcmp(optional9, "true") == 0);	/* optional is "true" */
	free(optional9);

	char           *transitive9 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach3->properties->next);
	CU_ASSERT(strcmp(transitive9, "false") == 0);	/* transitive is "true" */
	free(transitive9);
	/*
	 * TODO FULLY TEST THIS MPREACHNLRI - IT'S LONG BUT NEEDE char* pContent =
	 * (char*)xmlNodeGetContent(mpreach3->children); CU_ASSERT(strcmp(pContent,
	 * "199.109.32.0/22") == 0); free(pContent);
	 */
	xmlFreeNode(mpreach3);

	/* Testing fourth string */
	pos = 0;
	xmlNodePtr 	mpreach4 = genAttNode(mpnlri_test_4, &pos, NULL, 4, 312);
	CU_ASSERT(mpreach4 != NULL);
	if (mpreach4 == NULL) {
		return;
	}
	CU_ASSERT(strcmp((char *) mpreach4->name, "MP_REACH_NLRI") == 0);

	char           *optional91 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach4->properties);
	CU_ASSERT(strcmp(optional91, "true") == 0);	/* optional is "true" */
	free(optional91);

	char           *transitive91 = (char *) xmlNodeGetContent((xmlNodePtr) mpreach4->properties->next);
	CU_ASSERT(strcmp(transitive91, "false") == 0);	/* transitive is "true" */
	free(transitive91);
	/*
	 * TODO FULLY TEST THIS MPREACHNLRI - IT'S LONG BUT NEEDE
	 */
	xmlFreeNode(mpreach4);
}

void				/* type 15 */
test_unreach_nlri_attribute()
{
	int 		pos = 0;
	xmlNodePtr 	unlri_node = genAttNode(unreach_nlri_test, &pos, NULL, 4, 11);
	xmlNodePtr 	unlri_node_2 = genAttNode(unreach_nlri_test_2, &pos, NULL, 4, 11);

	CU_ASSERT(unlri_node != NULL);
	if (unlri_node == NULL) {
		if (unlri_node_2 != NULL);
		xmlFreeNode(unlri_node_2);
		return;
	}
	CU_ASSERT(strcmp((char *) unlri_node->name, "MP_UNREACH_NLRI") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) unlri_node->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) unlri_node->properties->next);
	CU_ASSERT(strcmp(transitive, "false") == 0);	/* transitive is "true" */
	free(transitive);

	char           *pContent = (char *) xmlNodeGetContent(unlri_node->children);
	CU_ASSERT(strcmp(pContent, "199.109.32.0/22") == 0);
	free(pContent);

	xmlFreeNode(unlri_node);

	/* Testing the second string with two NLRI's */
	CU_ASSERT(unlri_node_2 != NULL);
	if (unlri_node_2 == NULL) {
		return;
	}
	CU_ASSERT(strcmp((char *) unlri_node_2->name, "MP_UNREACH_NLRI") == 0);

	char           *optional2 = (char *) xmlNodeGetContent((xmlNodePtr) unlri_node_2->properties);
	CU_ASSERT(strcmp(optional2, "true") == 0);	/* optional is "true" */
	free(optional2);

	char           *transitive2 = (char *) xmlNodeGetContent((xmlNodePtr) unlri_node_2->properties->next);
	CU_ASSERT(strcmp(transitive2, "false") == 0);	/* transitive is "true" */
	free(transitive2);

	char           *pContent2 = (char *) xmlNodeGetContent(unlri_node_2->children);
	CU_ASSERT(strcmp(pContent2, "2806::/32") == 0);
	free(pContent2);

	char           *pContent3 = (char *) xmlNodeGetContent(unlri_node_2->children->next);
	CU_ASSERT(strcmp(pContent3, "2806:3::/32") == 0);
	free(pContent3);

	char           *pContent4 = (char *) xmlNodeGetContent(unlri_node_2->children->next->next);
	CU_ASSERT(strcmp(pContent4, "2806:2::/32") == 0);
	free(pContent4);

	char           *pContent5 = (char *) xmlNodeGetContent(unlri_node_2->children->next->next->next);
	CU_ASSERT(strcmp(pContent5, "2806:1::/32") == 0);
	free(pContent5);

	xmlFreeNode(unlri_node_2);


}

void				/* type 16 */
test_extend_comm_attribute()
{
	/* Testing the first string */
	int 		start = 0;

	xmlNodePtr 	extcommNode = genAttNode(extend_comm_test, &start, NULL, 4, 11);
	start = 0;
	xmlNodePtr 	extcommNode2 = genAttNode(extend_comm_test2, &start, NULL, 4, 11);
	start = 0;
	xmlNodePtr 	extcommNode3 = genAttNode(extend_comm_test3, &start, NULL, 4, 11);
	CU_ASSERT(extcommNode != NULL);	/* making sure we have the node back */
	CU_ASSERT(strcmp((char *) extcommNode->name, "EXTENDED_COMMUNITIES") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) extcommNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);
	optional = NULL;

	char           *transitive = (char *) xmlNodeGetContent(
				(xmlNodePtr) extcommNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);
	transitive = NULL;

	char           *type = (char *) xmlNodeGetContent((xmlNodePtr) extcommNode->properties->next->next->next->next->next);
	CU_ASSERT(strcmp(type, "Two-Octet AS Specific Extended Community") == 0);
	free(type);
	type = NULL;

	char           *subtype = (char *) xmlNodeGetContent((xmlNodePtr) extcommNode->properties->next->next->next->next->next->next);
	CU_ASSERT(strcmp(subtype, "Route Target") == 0);
	free(subtype);
	subtype = NULL;

	/* this one should have an ASN2 of 14041 */
	/* value of 0000138B */
	/* route target community */

	xmlNodePtr 	asn2 = (xmlNodePtr) extcommNode->children;
	xmlNodePtr 	value = (xmlNodePtr) asn2->next;

	char           *asn = (char *) xmlNodeGetContent((xmlNodePtr) asn2);
	CU_ASSERT(strcmp(asn, "14041") == 0);
	free(asn);
	asn = NULL;

	char           *val = (char *) xmlNodeGetContent((xmlNodePtr) value);
	CU_ASSERT(strcmp(val, "0000138B") == 0);
	free(val);
	val = NULL;




	/* Testing the second string */
	/* fake subtype for a 2-octate AS */
	CU_ASSERT(extcommNode2 != NULL);
	char           *asn1 = (char *) xmlNodeGetContent((xmlNodePtr) extcommNode2->children);
	CU_ASSERT(strcmp(asn1, "14041") == 0);
	free(asn1);
	asn1 = NULL;

	/* Testing the third string */
	/* fake type */
	CU_ASSERT(extcommNode3 != NULL);
	char           *hex = (char *) xmlNodeGetContent((xmlNodePtr) extcommNode3->children);
	CU_ASSERT(strcmp(hex, "C01008FFFF36D90000") == 0);
	free(hex);
	hex = NULL;


	xmlFreeNode(extcommNode);
	xmlFreeNode(extcommNode2);
	xmlFreeNode(extcommNode3);
}

void				/* type 17 */
test_as4_path_attribute()
{
	int 		start = 0;

	xmlNodePtr 	as4pathNode = genAttNode(as4path_test, &start, NULL, 4, 37);

	CU_ASSERT(as4pathNode != NULL);	/* making sure we have the node back */
	CU_ASSERT(strcmp((char *) as4pathNode->name, "AS4_PATH") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) as4pathNode->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);
	optional = NULL;

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) as4pathNode->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);
	transitive = NULL;

	xmlNodePtr 	asSegNode = as4pathNode->children;
	CU_ASSERT(strcmp((char *) asSegNode->name, "AS_SEQUENCE") == 0);

	/* test sould have 4 children.  Let's test them all! */
	xmlNodePtr 	as4node1 = asSegNode->children;
	xmlNodePtr 	as4node2 = as4node1->next;
	xmlNodePtr 	as4node3 = as4node2->next;
	xmlNodePtr 	as4node4 = as4node3->next;
	xmlNodePtr 	as4node5 = as4node4->next;
	xmlNodePtr 	as4node6 = as4node5->next;
	xmlNodePtr 	as4node7 = as4node6->next;
	xmlNodePtr 	as4node8 = as4node7->next;
	CU_ASSERT(strcmp((char *) as4node1->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node2->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node3->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node4->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node5->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node6->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node7->name, "ASN4") == 0);
	CU_ASSERT(strcmp((char *) as4node8->name, "ASN4") == 0);


	char           *content1 = (char *) xmlNodeGetContent(as4node1);
	char           *content2 = (char *) xmlNodeGetContent(as4node2);
	char           *content3 = (char *) xmlNodeGetContent(as4node3);
	char           *content4 = (char *) xmlNodeGetContent(as4node4);
	char           *content5 = (char *) xmlNodeGetContent(as4node5);
	char           *content6 = (char *) xmlNodeGetContent(as4node6);
	char           *content7 = (char *) xmlNodeGetContent(as4node7);
	char           *content8 = (char *) xmlNodeGetContent(as4node8);
	CU_ASSERT(strcmp(content1, "12145") == 0);
	CU_ASSERT(strcmp(content2, "14041") == 0);
	CU_ASSERT(strcmp(content3, "1299") == 0);
	CU_ASSERT(strcmp(content4, "3549") == 0);
	CU_ASSERT(strcmp(content5, "28168") == 0);
	CU_ASSERT(strcmp(content6, "53059") == 0);
	CU_ASSERT(strcmp(content7, "262682") == 0);
	CU_ASSERT(strcmp(content8, "28340") == 0);

	free(content1);
	content1 = NULL;
	free(content2);
	content2 = NULL;
	free(content3);
	content3 = NULL;
	free(content4);
	content4 = NULL;
	free(content5);
	content5 = NULL;
	free(content6);
	content6 = NULL;
	free(content7);
	content7 = NULL;
	free(content8);
	content8 = NULL;


	xmlFreeNode(as4pathNode);
}

void				/* type 18 */
test_as4_aggregator_attribute()
{
	int 		start = 0;

	xmlNodePtr 	agg4Node = genAttNode(as4_aggregator_test, &start, NULL, 4, 11);

	CU_ASSERT(agg4Node != NULL);	/* making sure we have the node back */

	CU_ASSERT(strcmp((char *) agg4Node->name, "AS4_AGGREGATOR") == 0);

	char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) agg4Node->properties);
	CU_ASSERT(strcmp(optional, "true") == 0);	/* optional is "true" */
	free(optional);
	optional = NULL;

	char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) agg4Node->properties->next);
	CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
	free(transitive);
	transitive = NULL;

	xmlNodePtr 	asn_node = agg4Node->children;
	xmlNodePtr 	ip_node = asn_node->next;

	char           *asnContent = (char *) xmlNodeGetContent(asn_node);
	CU_ASSERT(strcmp(asnContent, "131467") == 0);
	free(asnContent);
	asnContent = NULL;

	char           *ipContent = (char *) xmlNodeGetContent(ip_node);
	CU_ASSERT(strcmp(ipContent, "103.4.188.2") == 0);
	free(ipContent);
	ipContent = NULL;

	xmlFreeNode(agg4Node);
}


void				/* type 22 */
test_pmsi_tunnel_attribute()
{
/*  int start = 0;

  xmlNodePtr pmsiNode = genAttNode(pmsi_tunnel_test, &start, NULL, 4, 4);
  CU_ASSERT(pmsiNode != NULL); /*making sure we have the node back */
	if (pmsiNode != NULL) {

		char           *hex = (char *) xmlNodeGetContent((xmlNodePtr) pmsiNode->children);
		CU_ASSERT(strcmp(hex, "C0160100") == 0);
		free(hex);

		xmlFreeNode(pmsiNode);
	} */			/* TODO - FIND AN EXAMPLE AND START WITH
				 * THAT.  THE CURRENT EXAMPLE MAY HAVE A BAD
				 * LENGTH */
}

void				/* type23 */
test_tunnel_encap_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}

void				/* type24 */
test_traffic_eng_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}
void				/* type25 */
test_ipv6_addr_spec_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}
void				/* type27 */
test_pe_dist_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}

void				/* type28 */
test_bgp_entropy_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}
void				/* type 128 */
test_attr_set_attribute()
{
	/* TODO */

	CU_ASSERT(0);

}

void				/* type UNKNOWN */
test_unknown_attribute()
{
	int 		start = 0;
	xmlNodePtr 	unNode = genAttNode(unknown_test, &start, NULL, 2, 4);
	/* testing multiple in a single string */
	start = 0;
	xmlNodePtr 	unNode2 = genAttNode(unknown_test_2, &start, NULL, 2, 1);
	xmlNodePtr 	unNode3 = genAttNode(unknown_test_3, &start, NULL, 2, 816);

	CU_ASSERT(unNode != NULL);	/* making sure we have the node back */
	if (unNode != NULL) {
		CU_ASSERT(strcmp((char *) unNode->name, "UNKNOWN_ATTRIBUTE") == 0);

		char           *optional = (char *) xmlNodeGetContent((xmlNodePtr) unNode->properties);
		CU_ASSERT(strcmp(optional, "false") == 0);	/* optional is "true" */
		free(optional);
		optional = NULL;

		char           *transitive = (char *) xmlNodeGetContent((xmlNodePtr) unNode->properties->next);
		CU_ASSERT(strcmp(transitive, "true") == 0);	/* transitive is "true" */
		free(transitive);
		transitive = NULL;

		char           *content = (char *) xmlNodeGetContent(unNode);
		CU_ASSERT(strcmp(content, "40FE048017000D") == 0);
		free(content);
		content = NULL;

		xmlFreeNode(unNode);
	}
	CU_ASSERT(unNode2 != NULL);
	if (unNode2 != NULL) {
		CU_ASSERT(strcmp((char *) unNode2->name, "UNKNOWN_ATTRIBUTE") == 0);
		char           *content = (char *) xmlNodeGetContent(unNode2);
		CU_ASSERT(strcmp(content, "10FE0001FF") == 0);
		free(content);
		content = NULL;

		xmlFreeNode(unNode2);
	}
	CU_ASSERT(unNode3 != NULL);
	if (unNode3 != NULL) {
		CU_ASSERT(strcmp((char *) unNode3->name, "UNKNOWN_ATTRIBUTE") == 0);
		char           *content = (char *) xmlNodeGetContent(unNode3);
		CU_ASSERT(strcmp(content, unknown_test_str_3) == 0);
		free(content);
		content = NULL;

		xmlFreeNode(unNode3);
	}
	/* testing this one again to make sure that everything prints out correctly after a big one */
	unNode2 = genAttNode(unknown_test_2, &start, NULL, 2, 1);
	CU_ASSERT(unNode2 != NULL);
	if (unNode2 != NULL) {
		CU_ASSERT(strcmp((char *) unNode2->name, "UNKNOWN_ATTRIBUTE") == 0);
		char           *content = (char *) xmlNodeGetContent(unNode2);
		/* fprintf(stderr, "Content=%s\n", content); */
		CU_ASSERT(strcmp(content, "10FE0001FF") == 0);
		free(content);
		content = NULL;

		xmlFreeNode(unNode2);
	}
}

/*****************************************************************************
******************************************************************************
                            MISC. TEST CASES
******************************************************************************
*****************************************************************************/


void
test_getXMLAddressString()
{
	/* Testing normal cercumstances */
	char 		buffer   [XML_TEMP_BUFFER_LEN] = {0};
	CU_ASSERT(7 == getXMLAddressString(ipv4_address_test, buffer, XML_TEMP_BUFFER_LEN, 1));
	CU_ASSERT(0 == strcmp(buffer, "1.2.3.4"));
	CU_ASSERT(31 == getXMLAddressString(ipv6_address_test, buffer, XML_TEMP_BUFFER_LEN, 2));
	CU_ASSERT(0 == strcmp(buffer, "102:304:102:304:102:304:102:304"));

	/* Forcing a buffer overflow to make sure snprintf works correctly */
	char 		buffer2  [2] = {0};
	CU_ASSERT(0 == getXMLAddressString(ipv4_address_test, buffer2, 2, 1));

}


/*****************************************************************************
******************************************************************************
                         SKIP AHEAD TEST CASES
******************************************************************************
*****************************************************************************/
void
test_skipAheadMessage()
{
	xmlNodePtr 	skipNode = genSkipAheadStatusNode(skipAheadBMF);
	CU_ASSERT(skipNode != NULL);
	if (skipNode != NULL) {

		/* Making sure the type is SkipAhead */
		char           *type = (char *) xmlNodeGetContent((xmlNodePtr) skipNode->children);
		CU_ASSERT(strcmp(type, "SKIP_AHEAD") == 0);
		free(type);
		type = NULL;

		/* Making sure the string is kept */
		char           *msg = (char *) xmlNodeGetContent((xmlNodePtr) skipNode->children->next);
		CU_ASSERT(strcmp(msg, "5000 messages were skipped in queue TEST_QUEUE") == 0);
		free(msg);
		msg = NULL;


	}
}
