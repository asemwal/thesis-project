# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:26:36 2018

@author: asemwal
"""
import time
import utils
import sys
f='/home/asemwal/raw_data/2018/proc/destinationsource_1530662400_1530748799'
stats = {}
purpose1='destinationcount'
purpose2='destinationset'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    try:
        stats[x[0]].add(x[1])
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({x[0] : {x[1]}})
    l = str(file.readline()).strip()
print(time.time())
out1 = open(location+year+'proc/'+purpose1+'_'+utils.getTimeStamp(f), 'w')
out2 = open(location+year+'proc/'+purpose2+'_'+utils.getTimeStamp(f), 'w')
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            out1.write(str(x[0]) +"|"+str(len(x[1]))  +"\n"   )
            out2.write(str(x[0]) +"|"+",".join(list(x[1]))  +"\n"   )
    except KeyError as e:
        break;
out1.flush()
out1.close()
out2.flush()
out2.close()