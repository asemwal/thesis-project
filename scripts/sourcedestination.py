# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:26:36 2018

@author: asemwal
"""
import time
import utils
import sys
f='/home/asemwal/raw_data/2018/proc/longpaths_1530662400_1530748799'
stats = {}
purpose='sourcedestination'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split(" ");
    k= utils.getKey(x, [0,-1])
    try:
        stats[k] += 1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k : 1})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += (str(x[0]) +"|"+str(x[1]) +"\n"   )
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()