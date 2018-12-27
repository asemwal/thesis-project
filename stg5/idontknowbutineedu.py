# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
f='/home/asemwal/raw_data/2018/proc/peerpathvisibility_1530709999_1530729998'
print(time.time())
file = open(f, 'r')
purpose='links'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    rec = l.split("|")
    ases= rec[1].split(" " )
    if rec[0] != ases[0]:
        print l
    for i in range(1, len(ases)):
        try:
            if ases[i-1] != ases[i]:
                stats[ases[i-1]+"|"+ases[i] ] += 1
        except KeyError as e:
            stats.update({ases[i-1]+"|"+ases[i] : 1})
    l = str(file.readline()).strip()
line=""
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            #line += str(k) + "|"+ str(stats[k])+"\n"
            line += str(x[0].strip())+"|"+ str(x[1])+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')


out.write(line)
out.flush()
out.close()