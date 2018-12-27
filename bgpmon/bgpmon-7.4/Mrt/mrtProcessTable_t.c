/*
 *      Copyright (c) 2010 Colorado State University
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
 *      OTHER DEALINGS IN THE SOFTWARE.
 *
 *
 *  File: mrtProcessTable_t.c
 *  Authors: Darshan Washimkar
 *  Date: June 2014
 */

#include <CUnit/Basic.h>
#include <stdlib.h>
#include <stdio.h>
#include "mrtProcessTable_t.h"
#include "mrtProcessMSG.h"

/* Table Dump V1 IPV4 legitimate message string */
char           *test_table_dump_IPV4_str = "000000000300000008013BE1851ED1F402730D1C003C4001010040020802030D1C02BD0050400304D1F4027380040400000000C0081C0D1C00030D1C00560D1C023F0D1C029A0D1C029C0D1C02A80D1C07D8";
uint8_t        *test_table_dump_IPV4;

/* Table Dump V1 IPV4 shorter message */
char           *test_table_dump_IPV4_short_str = "000000000300000008013BE1851ED1F402730D1C003F4001010040020802030D1C02BD0050400304D1F4027380040400000000C0081C0D1C00030D1C00560D1C023F0D1C029A0D1C029C0D1C02A80D1C07D8";
uint8_t        *test_table_dump_IPV4_short;

/* Table Dump V1 IPV4 wrong status field */
char           *test_table_dump_IPV4_Wstatus_str = "000000000300000008033BE1851ED1F402730D1C003C4001010040020802030D1C02BD0050400304D1F4027380040400000000C0081C0D1C00030D1C00560D1C023F0D1C029A0D1C029C0D1C02A80D1C07D8";
uint8_t        *test_table_dump_IPV4_Wstatus;

/* Table Dump V1 IPV4 legitimate message string */
char           *test_table_dump_IPV6_str = "000000000300000008013BE1851ED1F402730D1C003C4001010040020802030D1C02BD0050400304D1F4027380040400000000C0081C0D1C00030D1C00560D1C023F0D1C029A0D1C029C0D1C02A80D1C07D802A8";
uint8_t        *test_table_dump_IPV6;

/* Table Dump V2 PEER INDEX TABLE sub-type legitimate message string */
char           *test_table_dump_v2_PeerIndexTable_str = "80DF330F000000060240391DF140391DF100002D11024C4B64264C4B642600002D9202C63A057FC63A057F00000E8F0200000000CA703CF3000011BA0340391CF12001046800020000000000000000000100002D110340391DF120010468FF020000000000000000000100002D11";
uint8_t        *test_table_dump_v2_PeerIndexTable;

/* Table Dump V2 PEER INDEX TABLE sub-type shorter message */
char           *test_table_dump_v2_PeerIndexTable_Short_str = "80DF330F000000060240391DF140391DF10000";
uint8_t        *test_table_dump_v2_PeerIndexTable_Short;

/* Table Dump V2 PEER INDEX TABLE sub-type longer message */
char           *test_table_dump_v2_PeerIndexTable_long_str = "80DF330F000000070240391DF140391DF100002D11024C4B64264C4B642600002D9202C63A057FC63A057F00000E8F0200000000CA703CF3000011BA0340391CF12001046800020000000000000000000100002D110340391DF120010468FF020000000000000000000100002D110240391DF140391DF100002D11";
uint8_t        *test_table_dump_v2_PeerIndexTable_long;

/* Table Dump V2 PEER INDEX TABLE sub-type with wrong Peer Type value */
char           *test_table_dump_v2_PeerIndexTable_WPT_str = "80DF330F000000060540391DF140391DF100002D11024C4B64264C4B642600002D9202C63A057FC63A057F00000E8F0200000000CA703CF3000011BA0340391CF12001046800020000000000000000000100002D110340391DF120010468FF020000000000000000000100002D11";
uint8_t        *test_table_dump_v2_PeerIndexTable_WPT;

/* Legitimate Table Dump V2 RIB_IPV4_UNICAST sub-type MRT message */
char           *test_table_dump_v2_RibIpv4Unicast_str = "000000000803000300004933645D00434001010050020012020400002D1100003C34000024580000005040030440391DF180040400000C8CC008182D1162703C34025B3C34026D3C3402BF3C34051F3C3411C600014933647C00384001010050020016020500002D9200001F4100003C3400002458000000504003044C4B6426C008101F4107D01F4107D12D9203E82D9203EC000249335BB300254001010050020016020500000E8F00000B6200000B620000245800000050400304C63A057F";
uint8_t        *test_table_dump_v2_RibIpv4Unicast;

/* Shorter Table Dump V2 RIB_IPV4_UNICAST sub-type MRT message */
char           *test_table_dump_v2_RibIpv4Unicast_short_str = "000000000803000300004933645D004340010100500200";
uint8_t        *test_table_dump_v2_RibIpv4Unicast_short;

/* Legitimate Table Dump V2 RIB_IPV6_UNICAST sub-type MRT message */
char           *test_table_dump_v2_RibIpv6Unicast_str = "00041F6620200100000002000549318AC00041400101005002000E020300002D1100000DDD0000315D80040400000000C008042D116270800E1A0002011020010468FF0200000000000000000001002020010000000449318A9A0051400101005002000E020300002D1100000DDD0000315D80040400000B74C008140DDD12230DDD7A942D1107D1315DFDE8315DFDEA800E1A0002011020010468000200000000000000000001002020010000";
uint8_t        *test_table_dump_v2_RibIpv6Unicast;

/* Shorter Table Dump V2 RIB_IPV6_UNICAST sub-type MRT message */
char           *test_table_dump_v2_RibIpv6Unicast_short_str = "00041F6620200100000002000549318AC00041400101005002000E020300002D";
uint8_t        *test_table_dump_v2_RibIpv6Unicast_short;

/* Sample Table Dump V2 RIB GENERIC Sub-type */
char           *test_table_dump_v2_RibGeneric_str = "540391DF140391DF100002D11024C4B64264C4B642600002D9202C63A057FC63A057F00000E8F0200000000CA703CF3000011BA0340391CF12001046800020000000000000000000100002D110340391DF1200";
uint8_t        *test_table_dump_v2_RibGeneric;

/*Creating variables to pass it to processing functions */
MRTmessage 	mrtMessage;
BMF 		bmf;
BMF            *bmfArray;
int 		asNumLen;


int 
init_ProcessTable(void)
{

	/* convert test string to hex */
	str2Hex(test_table_dump_IPV4_str, &test_table_dump_IPV4);
	str2Hex(test_table_dump_IPV4_short_str, &test_table_dump_IPV4_short);
	str2Hex(test_table_dump_IPV4_Wstatus_str, &test_table_dump_IPV4_Wstatus);
	str2Hex(test_table_dump_IPV6_str, &test_table_dump_IPV6);
	str2Hex(test_table_dump_v2_PeerIndexTable_str, &test_table_dump_v2_PeerIndexTable);
	str2Hex(test_table_dump_v2_PeerIndexTable_Short_str, &test_table_dump_v2_PeerIndexTable_Short);
	str2Hex(test_table_dump_v2_PeerIndexTable_long_str, &test_table_dump_v2_PeerIndexTable_long);
	str2Hex(test_table_dump_v2_PeerIndexTable_WPT_str, &test_table_dump_v2_PeerIndexTable_WPT);
	str2Hex(test_table_dump_v2_RibIpv4Unicast_str, &test_table_dump_v2_RibIpv4Unicast);
	str2Hex(test_table_dump_v2_RibIpv4Unicast_short_str, &test_table_dump_v2_RibIpv4Unicast_short);
	str2Hex(test_table_dump_v2_RibIpv6Unicast_str, &test_table_dump_v2_RibIpv6Unicast);
	str2Hex(test_table_dump_v2_RibIpv6Unicast_short_str, &test_table_dump_v2_RibIpv6Unicast_short);
	str2Hex(test_table_dump_v2_RibGeneric_str, &test_table_dump_v2_RibGeneric);
	return 0;
}

int 
clean_ProcessTable(void)
{
	free(test_table_dump_IPV4);
	free(test_table_dump_IPV4_short);
	free(test_table_dump_IPV4_Wstatus);
	free(test_table_dump_IPV6);
	free(test_table_dump_v2_PeerIndexTable);
	free(test_table_dump_v2_PeerIndexTable_Short);
	free(test_table_dump_v2_PeerIndexTable_long);
	free(test_table_dump_v2_PeerIndexTable_WPT);
	free(test_table_dump_v2_RibIpv4Unicast);
	free(test_table_dump_v2_RibIpv4Unicast_short);
	free(test_table_dump_v2_RibIpv6Unicast);
	free(test_table_dump_v2_RibIpv6Unicast_short);
	free(test_table_dump_v2_RibGeneric);
	return 0;
}


void 
testProcessTable_TableDumpV1(void)
{
	/* Create MRT Header to pass it to TABLE DUMP message processing function */
	int 		tableDumpV1;
	MRTheader 	mrtHeader;
	uint16_t 	seqNo;
	sscanf("3BE1A131", "%x", &mrtHeader.timestamp);
	mrtHeader.type = TABLE_DUMP;
	mrtHeader.subtype = AFI_IPv4;
	sscanf("00000052", "%x", &mrtHeader.length);

	/* Create bmf */
	bmf = createBMF(0, BMF_TYPE_TABLE_TRANSFER, NULL, 0);
	if (bmf == NULL) {
		log_err("processMRTTableDumpFile: Unable to create BMF");
		return (1);
	}
	/* Valid TABLE DUMP V1 IPV4 input message */
	tableDumpV1 = MRT_processType_TableDump(test_table_dump_IPV4,
			  &mrtHeader, &mrtMessage, &bmf, &asNumLen, &seqNo);
	CU_ASSERT(tableDumpV1 != 1);
	CU_ASSERT(bmf != NULL);
	CU_ASSERT(asNumLen == 2);
	CU_ASSERT(bmf->length != 0);

	/* Longer TABLE DUMP V1 IPV4 input message */
	tableDumpV1 = MRT_processType_TableDump(test_table_dump_IPV4_short,
			  &mrtHeader, &mrtMessage, &bmf, &asNumLen, &seqNo);
	CU_ASSERT(tableDumpV1 == 1);

	/* TABLE DUMP V1 IPV4 input message with wrong status field */
	tableDumpV1 = MRT_processType_TableDump(test_table_dump_IPV4_Wstatus,
			  &mrtHeader, &mrtMessage, &bmf, &asNumLen, &seqNo);
	CU_ASSERT(tableDumpV1 == 1);

	/* TABLE DUMP V1 IPV6 subtype */
	mrtHeader.subtype = AFI_IPv6;
	sscanf("00000054", "%x", &mrtHeader.length);
	tableDumpV1 = MRT_processType_TableDump(test_table_dump_IPV6,
			  &mrtHeader, &mrtMessage, &bmf, &asNumLen, &seqNo);
	CU_ASSERT(tableDumpV1 == 1);
}

void 
testProcessTableDumpV2_PeerIndexTable(void)
{
	MRTheader 	mrtHeader;
	int 		tableDumpV2PeerIndexTable, i;
	Peer_Index_Table *peerIndexTable = NULL;
	sscanf("0000006E", "%x", &mrtHeader.length);
	mrtHeader.type = TABLE_DUMP_V2;
	mrtHeader.subtype = PEER_INDEX_TABLE;
	sscanf("493335E3", "%x", &mrtHeader.timestamp);

	/* Legitimate MRT message */
	tableDumpV2PeerIndexTable = MRT_processType_TableDumpV2_PeerIndexTable
		(test_table_dump_v2_PeerIndexTable, &mrtHeader, &peerIndexTable);
	CU_ASSERT(tableDumpV2PeerIndexTable != 1);
	CU_ASSERT(peerIndexTable->BGPSrcID == 2162111247);
	CU_ASSERT(peerIndexTable->ViewNameLen == 0);
	CU_ASSERT(peerIndexTable->PeerCount == 6);
	CU_ASSERT(peerIndexTable->peerEntries != NULL);
	for (i = 0; i < peerIndexTable->PeerCount; i++) {
		CU_ASSERT(peerIndexTable->peerEntries[i].peerType <= 3);
	}

	/* Shorter message - fails with exceeded length */
	free(peerIndexTable);
	peerIndexTable = NULL;
	sscanf("00000013", "%x", &mrtHeader.length);
	tableDumpV2PeerIndexTable = MRT_processType_TableDumpV2_PeerIndexTable
		(test_table_dump_v2_PeerIndexTable_Short, &mrtHeader, &peerIndexTable);
	CU_ASSERT(tableDumpV2PeerIndexTable == 1);

	/* Longer message fail with length mismatch */
	free(peerIndexTable);
	peerIndexTable = NULL;
	sscanf("0000006E", "%x", &mrtHeader.length);
	tableDumpV2PeerIndexTable = MRT_processType_TableDumpV2_PeerIndexTable
		(test_table_dump_v2_PeerIndexTable_long, &mrtHeader, &peerIndexTable);
	CU_ASSERT(tableDumpV2PeerIndexTable == 1);

	/* Fail with wrong Peer Type value */
	free(peerIndexTable);
	peerIndexTable = NULL;
	tableDumpV2PeerIndexTable = MRT_processType_TableDumpV2_PeerIndexTable
		(test_table_dump_v2_PeerIndexTable_WPT, &mrtHeader, &peerIndexTable);
	CU_ASSERT(tableDumpV2PeerIndexTable == 1);
}

void 
testProcessTableDumpV2_RIB_SUBTYPE(void)
{

	/* Populate Peer Index Table */
	Peer_Index_Table *peerIndexTable = NULL;
	MRTheader 	mrtHeader_peerIndexTable;
	sscanf("0000006E", "%x", &mrtHeader_peerIndexTable.length);
	mrtHeader_peerIndexTable.type = TABLE_DUMP_V2;
	mrtHeader_peerIndexTable.subtype = PEER_INDEX_TABLE;
	sscanf("493335E3", "%x", &mrtHeader_peerIndexTable.timestamp);
	MRT_processType_TableDumpV2_PeerIndexTable
		(test_table_dump_v2_PeerIndexTable,
		 &mrtHeader_peerIndexTable, &peerIndexTable);

	/* Legitimate Table Dump V2 RIB IPV4 UNICAST Sub-type */
	MRTheader 	mrtHeader;
	MRTmessage    **mrtMessageArray;
	int 		returnValue, i;
	int 		entryCount;
	int            *asn_lengthArray;
	unsigned int 	seqNo;
	sscanf("000000C0", "%x", &mrtHeader.length);
	mrtHeader.type = TABLE_DUMP_V2;
	mrtHeader.subtype = RIB_IPV4_UNICAST;
	sscanf("493365EF", "%x", &mrtHeader_peerIndexTable.timestamp);

	returnValue = MRT_processType_TableDumpV2_RIB_SUBTYPE(
	     test_table_dump_v2_RibIpv4Unicast, &mrtHeader, &peerIndexTable,
	&entryCount, &bmfArray, &mrtMessageArray, &asn_lengthArray, &seqNo);

	CU_ASSERT(returnValue == 0);
	CU_ASSERT(entryCount == 3);
	for (i = 0; i < entryCount; i++) {
		CU_ASSERT(bmfArray[i] != NULL);
		CU_ASSERT((bmfArray[i])->data != NULL);
	}

	/* Fails with shorter MRT message length */
	sscanf("00000017", "%x", &mrtHeader.length);
	returnValue = MRT_processType_TableDumpV2_RIB_SUBTYPE(
	test_table_dump_v2_RibIpv4Unicast_short, &mrtHeader, &peerIndexTable,
	&entryCount, &bmfArray, &mrtMessageArray, &asn_lengthArray, &seqNo);

	CU_ASSERT(returnValue == 1);

	/* Legitimate Table Dump V2 RIB IPV6 UNICAST Sub-type */
	sscanf("000000AD", "%x", &mrtHeader.length);
	mrtHeader.type = TABLE_DUMP_V2;
	mrtHeader.subtype = RIB_IPV6_UNICAST;
	sscanf("493365F0", "%x", &mrtHeader_peerIndexTable.timestamp);
	returnValue = MRT_processType_TableDumpV2_RIB_SUBTYPE(
	     test_table_dump_v2_RibIpv6Unicast, &mrtHeader, &peerIndexTable,
	&entryCount, &bmfArray, &mrtMessageArray, &asn_lengthArray, &seqNo);

	CU_ASSERT(returnValue == 0);
	CU_ASSERT(entryCount == 2);
	for (i = 0; i < entryCount; i++) {
		CU_ASSERT(bmfArray[i] != NULL);
		CU_ASSERT((bmfArray[i])->data != NULL);
	}

	/* Fail with shorter MRT message length */
	sscanf("00000020", "%x", &mrtHeader.length);
	returnValue = MRT_processType_TableDumpV2_RIB_SUBTYPE(
	test_table_dump_v2_RibIpv6Unicast_short, &mrtHeader, &peerIndexTable,
	&entryCount, &bmfArray, &mrtMessageArray, &asn_lengthArray, &seqNo);
	CU_ASSERT(returnValue == 1);

}

void 
testProcessTableDumpV2_RIB_GENERIC_SUBTYPE(void)
{
	MRTheader 	mrtHeader;
	sscanf("00000053", "%x", &mrtHeader.length);
	mrtHeader.type = TABLE_DUMP_V2;
	mrtHeader.subtype = RIB_GENERIC;
	sscanf("493335E3", "%x", &mrtHeader.timestamp);

	MRT_processType_TableDumpV2_GENERIC_SUBTYPE(test_table_dump_v2_RibGeneric,
						    &mrtHeader, &bmfArray);
	CU_ASSERT(TRUE);
}

void 
testIsValidIpAddress(void)
{
	char 		ipAddress1[ADDR_MAX_CHARS] = "112.141.10.223";
	char 		ipAddress2[ADDR_MAX_CHARS] = "FE80:0000:0000:0000:0202:B3FF:FE1E:8329";
	int 		ipType1 = 4;
	int 		ipType2 = 6;
	int 		returnvalue;

	returnvalue = isValidIpAddress(ipAddress1, ipType1);
	CU_ASSERT(returnvalue == 0);

	returnvalue = isValidIpAddress(ipAddress2, ipType2);
	CU_ASSERT(returnvalue == 0);
}

void 
testPackPrefix(void)
{
	const char     *prefixIPAddrStr = "130.150.27.214";
	int 		ipVer = 4;
	int 		prefixLen = 21;
	u_char 		packedPrefix[16];
	uint8_t 	prefixIPAddr[16];
	uint8_t 	requiredPackedPrefix[16];
	int 		i;

	sscanf("189682", "%x", &requiredPackedPrefix);
	if (inet_pton(AF_INET, prefixIPAddrStr, prefixIPAddr)) {
		packPrefix(prefixIPAddr, ipVer, prefixLen, packedPrefix);
	}
	for (i = 0; i < 3; i++) {
		CU_ASSERT(requiredPackedPrefix[i] == packedPrefix[i]);
	}
}
