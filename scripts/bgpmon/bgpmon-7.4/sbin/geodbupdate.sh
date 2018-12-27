#!/bin/sh
#this will be called normally from ../
ORIGGEODB="/etc/bgpmon_geodb.txt"
GEODBTMP="etc/geodbtemp"
GEODBMERGED="etc/bgpmon_geodb_merged.txt"
CURGEODB="etc/bgpmon_geodb.txt"
sed  '1,/#USER SUPPLIED DATA$/d' ${ORIGGEODB} > ${GEODBTMP}
cat ${CURGEODB} > ${GEODBMERGED}
cat ${GEODBTMP} >> ${GEODBMERGED}
rm -f ${GEODBTMP}
