#include <sys/queue.h>
#include <sys/types.h>
#define ULOC_STR "UNKNOWN LOCATION"
#define GEOLOCATION_MAX_CHARS 512

struct geodb_entry {
	LIST_ENTRY(geodb_entry) pointers;
	char		*ipstr;
	char		*location;
};

struct geodb_list {
	LIST_HEAD(geodbhead, geodb_entry) head;
	size_t size;
};

int   geodb_configured;
struct geodb_list geolist;

int   geodb_add(struct geodb_list *, char *, char*);
char *geodb_resolve(struct geodb_list *, char *);
int   geodb_init(struct geodb_list *, char *);
