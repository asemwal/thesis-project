# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
purpose='longpaths'
f=sys.argv[1]
#f='/home/asemwal/raw_data/2018/proc/paths_append_1530722400_1530732399'
stats={}
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()

#file = open('/home/asemwal/thesis/bgp/archive_1530729999_1530739999', 'r')
#stats collected
print(time.time())
#file = open('/home/asemwal/thesis/bgpreader/archive_1530709999_1530729998', 'r')
c=0;
while( l !=''):
    ases= l.split(" " )
    j = len(ases)-1
    for i in range(j-1, -1,-1 ):
        try:
            stats[" ".join(ases[i:])] = 1
        except KeyError as e:
            stats.update({" ".join(ases[i:]) : 1})
    l = str(file.readline()).strip()
line=""
print(time.time())
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
while(True):
    try:
        x = stats.popitem()
        out.write(str(x[0])+"\n")
    except KeyError as e:
        break;
out.flush()
out.close()
