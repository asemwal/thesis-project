# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:26:36 2018

@author: asemwal
"""
import time
import utils
import sys
f='/home/asemwal/raw_data/2018/proc/tmp_vplinks_1530662400_153074879'
f= '/home/asemwal/raw_data/experiments/results/path_monset450_1541412861'
stats = {}
jaccard = {}
purpose='jaccard'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    rec = l.split("#")
    vp = rec[0]
    links= set(rec[1].split(","))
    if rec[2] == 'M':
        stats.update({vp:links})
        jaccard.update({vp:{}})
    l = str(file.readline()).strip()
    
for i in stats.keys():
    for j in stats.keys():
        if i != j:
            jaccard[i].update({j:0})
     
header = "H|"
key = list(stats.keys())
for I in range(0,len(key)):
    i = key[I]
    header += i +"|"
    print("{} took {}".format(I, time.time()))
    for J in range(I,len(key)):
        if I != J:
            j = key[J]
            aub = len(stats[i].union(stats[j]))
            aib = len(stats[i].intersection(stats[j])) 
            distance = 0;
            if aib == 0:
                distance= 1
            else:
                distance = 1 - (float(aib)/aub)
            jaccard[i][j] = round(distance,6)
            jaccard[j][i] = round(distance,6)

line=""
print(time.time())
header +='\n'
line = header
for I in range(0,len(key)):
    i = key[I]
    line += i+"|"
    for J in range(0,len(key)):
        j = key[J]
        if I == J:
            line +="-|"
        else:
            line += str(jaccard[i][j])+"|"
    line +='\n'
#out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out = open('/home/asemwal/raw_data/experiments/results/path_monset450_1541412861_2','w')
out.write(line)
out.flush()
out.close()
