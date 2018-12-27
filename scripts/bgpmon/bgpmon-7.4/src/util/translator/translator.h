#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/queue.h>
#include <time.h>
#include "XML/xml.h"
#include "XML/xml_gen.h"
#include "Util/bgpmon_formats.h"
#include "Mrt/mrtProcessMSG.h"
#include "Mrt/mrtProcessTable.h"
#include "Util/bgp.h"
#include "Util/geolocation.h"

#define BGPSIZE 4096
#define XMLBUFSIZ 100000

struct seen_entry {
	LIST_ENTRY(seen_entry) pointers;
	size_t		strsiz;
	char		*ipstr;
	uint32_t	seen;
};

struct seen_list {
	LIST_HEAD(seenhead, seen_entry) head;
	size_t size;
};

struct seen_list seenl; /* global on the stack */
char mrt_file[FILENAME_MAX_CHARS]; /* global filename */
FILE *log_fd, *FileIn; /* the file pointers for input and log */
char monitor_addr[ADDR_MAX_CHARS];
char xml_buf[XMLBUFSIZ]; /* 100k static xml array for msgs */
int monitor_addr_type; /* ipv4 is the default */
uint16_t monitor_port; /* default collector port */
uint32_t monitor_asn; /* default ASN */
char ttraveler_flag; /* to toggle time traveler detection in updates */
char file_flag;
double rate; /* the rate that we parsed messages */
struct timeval tstart, tend;
size_t counter,largercounter;
uint8_t bgpmsg[2*BGPSIZE];


void (*trans_log)(const char *, ...); /* with this we will hijack the log function */
int add_to_seen_list(struct seen_list *, char *, uint32_t);
int free_seen_list(struct seen_list *);
void print_seen_list(struct seen_list *);
int trans_is_valid_IP(char *, int);
int trans_process_table_dump_file();
int trans_process_update_file();
int trans_MRT_processType_TableDump(uint8_t *, MRTheader *, MRTmessage *, BMF *, int *, uint16_t *);
int trans_MRT_processType_TableDumpV2(uint8_t *, MRTheader *, Peer_Index_Table **, int *, BMF **, MRTmessage ***, int **, unsigned int *);
int trans_MRT_processType_TableDumpV2_PeerIndexTable(uint8_t *, MRTheader *, Peer_Index_Table**);
int trans_MRT_processType_TableDumpV2_RIB_SUBTYPE(uint8_t *, MRTheader *, Peer_Index_Table **, int *, BMF **, MRTmessage ***, int **, unsigned int *);
int trans_MRT_processType_TableDumpV2_GENERIC_SUBTYPE(uint8_t *, MRTheader *, BMF **);
int trans_packPrefix(uint8_t *, int, int, u_char *);
