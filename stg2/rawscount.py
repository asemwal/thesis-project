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
purpose='rawscount'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [1])
    try:
        stats[k]['R'] += int(x[4])
        stats[k]['A'] += int(x[5])
        stats[k]['W'] += int(x[6])
        stats[k]['S'] += int(x[7])
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k:{'R':int(x[4]),'A':int(x[5]),'W':int(x[6]),'S':int(x[7])}})
    l = file.readline()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += (str(x[0]) +"|"+str(x[1]['R']) +"|"+str(x[1]['A']) +"|"+str(x[1]['W']) +"|"+str(x[1]['S']) +"\n"   )
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()