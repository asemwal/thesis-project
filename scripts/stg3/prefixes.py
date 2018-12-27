# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:26:36 2018

@author: asemwal
"""
import time
import utils
import sys
f=sys.argv[1]
stats = {}

purpose='prefixes'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [1])
    try:
        stats[k] = 1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k:0})
    l = file.readline()
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