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
 *  File: xml_help_t.c
 *  Authors: M. Lawrence Weikum
 *  Date: August 22. 2013
 */
#include "xml_help_t.h"


char           *msg1 = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"2\">2a03:a480:ffff:ffff::247</ADDRESS><PORT>179</PORT><ASN4>59469</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"2\">2001:468:d01:33::80df:330f</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1377276814</TIMESTAMP><DATETIME>2013-08-23T16:53:34Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>1767341969</SEQUENCE_NUMBER><bgp:UPDATE bgp_message_type=\"2\"><bgp:ORIGIN optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"1\">IGP</bgp:ORIGIN><bgp:AS_PATH optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"2\"><bgp:AS_SEQUENCE><bgp:ASN4>59469</bgp:ASN4><bgp:ASN4>174</bgp:ASN4><bgp:ASN4>3356</bgp:ASN4><bgp:ASN4>21371</bgp:ASN4><bgp:ASN4>35054</bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH><bgp:COMMUNITY optional=\"true\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"8\"><bgp:ASN2>174</bgp:ASN2><bgp:VALUE>21100</bgp:VALUE></bgp:COMMUNITY><bgp:COMMUNITY optional=\"true\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"8\"><bgp:ASN2>174</bgp:ASN2><bgp:VALUE>22005</bgp:VALUE></bgp:COMMUNITY><bgp:MP_REACH_NLRI optional=\"true\" transitive=\"false\" partial=\"false\" extended=\"true\" attribute_type=\"14\" safi=\"1\"><bgp:MP_NEXT_HOP afi=\"2\">2a03:a480:ffff:ffff::247</bgp:MP_NEXT_HOP><bgp:MP_NLRI afi=\"2\">2a03:bd80::/32</bgp:MP_NLRI></bgp:MP_REACH_NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF005D02000000464001010040021602050000E84D000000AE00000D1C0000537B000088EEC0080800AE526C00AE55F5900E001A000201102A03A480FFFFFFFF000000000000024700202A03BD80</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH2a03:bd80::/32]/NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>";

char           *msg2 = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"1\">205.166.205.202</ADDRESS><PORT>179</PORT><ASN4>6360</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1377276814</TIMESTAMP><DATETIME>2013-08-23T16:53:34Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>1767341970</SEQUENCE_NUMBER><bgp:UPDATE bgp_message_type=\"2\"><bgp:ORIGIN optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"1\">IGP</bgp:ORIGIN><bgp:AS_PATH optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"2\"><bgp:AS_SEQUENCE><bgp:ASN4>6360</bgp:ASN4><bgp:ASN4>4323</bgp:ASN4><bgp:ASN4>701</bgp:ASN4><bgp:ASN4>2914</bgp:ASN4><bgp:ASN4>4230</bgp:ASN4><bgp:ASN4>28573</bgp:ASN4></bgp:AS_SEQUENCE></bgp:AS_PATH><bgp:NEXT_HOP optional=\"false\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"3\" afi=\"1\">205.166.205.202</bgp:NEXT_HOP><bgp:COMMUNITY optional=\"true\" transitive=\"true\" partial=\"false\" extended=\"false\" attribute_type=\"8\"><bgp:ASN2>65535</bgp:ASN2><bgp:VALUE>65281</bgp:VALUE></bgp:COMMUNITY><bgp:NLRI afi=\"1\">179.216.216.0/22</bgp:NLRI><bgp:NLRI afi=\"1\">179.216.196.0/23</bgp:NLRI><bgp:NLRI afi=\"1\">179.217.100.0/22</bgp:NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0052020000002F4001010040021A0206000018D8000010E3000002BD00000B620000108600006F9D400304CDA6CDCAC00804FFFFFF0116B3D8D817B3D8C416B3D964</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"179.216.216.0/22\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"179.216.196.0/23\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH[MP_NLRI=\"179.217.100.0/22\"]/MP_NLRI</NODE_PATH><ANNOTATION>DPATH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>";

char           *msg3 = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"1\">129.250.1.248</ADDRESS><PORT>179</PORT><ASN4>2914</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1377276814</TIMESTAMP><DATETIME>2013-08-23T16:53:34Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>1767341971</SEQUENCE_NUMBER><bgp:UPDATE bgp_message_type=\"2\"><bgp:WITHDRAW afi=\"1\">148.208.211.0/24</bgp:WITHDRAW></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF001B0200041894D0D30000</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE[\"148.208.211.0/24\"]/bgp:WITHDRAW</NODE_PATH><ANNOTATION>WITH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>";

char           *msg4 = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"2\">2001:388:1::13</ADDRESS><PORT>179</PORT><ASN4>7575</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"2\">2001:468:d01:33::80df:330f</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1377276814</TIMESTAMP><DATETIME>2013-08-23T16:53:34Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>1767341972</SEQUENCE_NUMBER><bgp:UPDATE bgp_message_type=\"2\"><bgp:MP_UNREACH_NLRI optional=\"true\" transitive=\"false\" partial=\"false\" extended=\"true\" attribute_type=\"15\" safi=\"1\"><bgp:MP_NLRI afi=\"2\">2a03:bd80::/32</bgp:MP_NLRI></bgp:MP_UNREACH_NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0023020000000C900F0008000201202A03BD80</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH2a03:bd80::/32]/NLRI</NODE_PATH><ANNOTATION>WITH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>";

char           *msg5 = "<BGP_MONITOR_MESSAGE xmlns:xsi=\"http://www.w3.org/2001/XMLSchema\" xmlns=\"urn:ietf:params:xml:ns:bgp_monitor\" xmlns:bgp=\"urn:ietf:params:xml:ns:xfb\" xmlns:ne=\"urn:ietf:params:xml:ns:network_elements\"><SOURCE><ADDRESS afi=\"2\">2001:388:1::16</ADDRESS><PORT>179</PORT><ASN4>7575</ASN4></SOURCE><DEST><ADDRESS afi=\"1\">128.223.51.15</ADDRESS><PORT>179</PORT><ASN4>6447</ASN4></DEST><MONITOR><ADDRESS afi=\"2\">2001:468:d01:33::80df:330f</ADDRESS><PORT>0</PORT><ASN4>0</ASN4></MONITOR><OBSERVED_TIME precision=\"false\"><TIMESTAMP>1377276814</TIMESTAMP><DATETIME>2013-08-23T16:53:34Z</DATETIME></OBSERVED_TIME><SEQUENCE_NUMBER>1767341973</SEQUENCE_NUMBER><bgp:UPDATE bgp_message_type=\"2\"><bgp:MP_UNREACH_NLRI optional=\"true\" transitive=\"false\" partial=\"false\" extended=\"true\" attribute_type=\"15\" safi=\"1\"><bgp:MP_NLRI afi=\"2\">2a03:bd80::/32</bgp:MP_NLRI></bgp:MP_UNREACH_NLRI></bgp:UPDATE><OCTET_MESSAGE>FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0023020000000C900F0008000201202A03BD80</OCTET_MESSAGE><METADATA><NODE_PATH>//bgp:UPDATE/bgp:MP_REACH2a03:bd80::/32]/NLRI</NODE_PATH><ANNOTATION>WITH</ANNOTATION></METADATA></BGP_MONITOR_MESSAGE>";


int 		msg1len;
int 		msg2len;
int 		msg3len;
int 		msg4len;
int 		msg5len;

/* The suite initialization function.
 * Returns zero on success, non-zero otherwise.
 */
int 
init_xml_test(void)
{

	msg1len = strlen(msg1);
	msg2len = strlen(msg2);
	msg3len = strlen(msg3);
	msg4len = strlen(msg4);
	msg5len = strlen(msg5);

	return 0;
}

/* The suite cleanup function.
 * Returns zero on success, non-zero otherwise.
 */
int 
clean_xml_test(void)
{

	return 0;
}



void 
testXML_copyNew()
{

	char           *msg1cpy = NULL;
	copyXMLmsg((void **) &msg1cpy, msg1);
	CU_ASSERT(strcmp(msg1cpy, msg1) == 0);
	if (msg1cpy != NULL)
		free(msg1cpy);

	char           *msg2cpy = NULL;
	copyXMLmsg((void **) &msg2cpy, msg2);
	CU_ASSERT(strcmp(msg2cpy, msg2) == 0);
	if (msg2cpy != NULL)
		free(msg2cpy);

	char           *msg3cpy = NULL;
	copyXMLmsg((void **) &msg3cpy, msg3);
	CU_ASSERT(strcmp(msg3cpy, msg3) == 0);
	if (msg3cpy != NULL)
		free(msg3cpy);

	char           *msg4cpy = NULL;
	copyXMLmsg((void **) &msg4cpy, msg4);
	CU_ASSERT(strcmp(msg4cpy, msg4) == 0);
	if (msg4cpy != NULL)
		free(msg4cpy);

	char           *msg5cpy = NULL;
	copyXMLmsg((void **) &msg5cpy, msg5);
	CU_ASSERT(strcmp(msg5cpy, msg5) == 0);
	if (msg5cpy != NULL)
		free(msg5cpy);
}
