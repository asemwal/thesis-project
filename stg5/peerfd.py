# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
f='/home/asemwal/raw_data/2014/proc/rawscount_pct_1404432000_1404518399'
if len(sys.argv) >=2:
    f=sys.argv[1]

purpose='peerfd'
print(time.time())
file = open(f, 'r')
print(file.name)
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
peerset = set()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [0,2,3])
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
    l = file.readline().strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += (str(x[0]) +"|"+str(x[1]['R']) +"|"+str(x[1]['A']) +"|"+str(x[1]['W']) +"|"+str(x[1]['S'])+ "|"+ str(x[1]['R'] + x[1]['W']+ x[1]['A'] + x[1]['S'])  +"\n"   )
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()