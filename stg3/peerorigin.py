# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 13:19:40 2018

@author: asemwal
"""

import time
import utils
import sys
f=sys.argv[1]
#f='/home/asemwal/raw_data/2018/proc/peerpathvisibility_1530769500_1530773099'
stats = {}
purpose='peer_origin'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [1])
    try:
        newases = k.split(" ")
        ases = [newases[0]]
        peer = x[0]
        for i in range(1, len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
                
        origin = ases[-1]
        k = utils.getKey([peer," ".join(ases),origin],[0,2,1])
        stats[k] = 1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k:0})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += str(x[0].strip())+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()