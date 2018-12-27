# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:19:40 2018

@author: asemwal
"""

import time
import utils
import sys
#f=sys.argv[1]
f='/home/asemwal/raw_data/2018/proc/peer_origin_1530709999_1530773099_dedup'
stats = {}
purpose='peer_origin_map'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [0,1])
    try:
        stats[k] += 1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k:1})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += str(x[0].strip())+"|"+str(x[1])+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()