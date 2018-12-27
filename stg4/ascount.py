# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
f=sys.argv[1]
purpose='ascount'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases= l.split("|" )
    try:
        if(len(ases)==3):
            stats[ases[0]] =1
            stats[ases[1]] =1
    except KeyError as e:
            stats.update({ases[0] : 1})
            stats.update({ases[1] : 1})
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