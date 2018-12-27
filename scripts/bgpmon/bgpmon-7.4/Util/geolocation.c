#include <stdlib.h>
#include <string.h>
#include "geolocation.h"
#include "bgpmon_defaults.h"
#include "log.h"

int
geodb_add(struct geodb_list *list, char *ip, char *loc)
{
	struct geodb_entry *tmp;
	struct geodb_entry *ge;
	size_t iplen;
	size_t loclen;
	LIST_FOREACH(tmp, &list->head, pointers) {
		if (strncmp(tmp->ipstr, ip, ADDR_MAX_CHARS) == 0) {
			LIST_REMOVE(tmp, pointers);
			free(tmp);
			break;
		}
	}
	ge = malloc(sizeof(struct geodb_entry));
	iplen = strnlen(ip, ADDR_MAX_CHARS);
	loclen = strnlen(loc, GEOLOCATION_MAX_CHARS);
	ge->ipstr = strndup(ip, iplen);
	ge->location = strndup(loc, loclen);
	LIST_INSERT_HEAD(&list->head, ge, pointers);
	(list->size)++;
	return 0;
}

char *
geodb_resolve(struct geodb_list *list, char *ip)
{
	struct geodb_entry *tmp;
	if (list->size == 0) {
		return ULOC_STR;
	}

	LIST_FOREACH(tmp, &list->head, pointers) {
		if (strncmp(tmp->ipstr, ip, ADDR_MAX_CHARS) == 0) {
			return tmp->location;
		}
	}

	return ULOC_STR;
}

int
geodb_init(struct geodb_list *list, char *fname)
{
	FILE *fp;
	char *line = NULL, *p = NULL, *iptmp = NULL, *loctmp = NULL;
	size_t linesize = 0,loclen = 0;
	ssize_t linelen;
	fp = fopen(fname, "r");
	if (fp == NULL) {
		perror("failed to open geolocation file\n"); /* log is not yet inited */
		return 1;
	}
	while ((linelen = getline(&line, &linesize, fp)) != -1) {
		loctmp = NULL;
		iptmp = p = line;
		if (linelen > 0 && line[0] == '#') /* comment line */
			continue;
		for (; p < &line[linelen-1] && (p = strsep(&line, " \t")) != NULL;) {
			if (*p == '\0') {
				continue;
			} else if (*p == '\n') {
				fprintf(stderr, "missing location string\n");
				loctmp = NULL;
				break;
			} else {
				if ((loclen = strlen(p)) > 1 && p[loclen-1] == '\n') {
					p[loclen-1] = '\0';
				}
				loctmp = p;
			}
		}

		if (loctmp != NULL) { /* means we got both delmited fields from line */
			geodb_add(list, iptmp, loctmp);
		} else {
			fprintf(stderr, "geolocation ignoring malformed line\n");
		}
	}

	if (ferror(fp)) {
		perror("geolocation getline error\n");
		fclose(fp);
		return 1;
	}

	fclose(fp);
	return 0;
}
