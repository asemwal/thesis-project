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
purpose='paths_append'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k= utils.getKey(x, [0])
    try:
        newases = k.split(" ")
        ases = [newases[0]]
        for i in range(1, len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
                
        stats[" ".join(ases)] = 1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({" ".join(ases):1})
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