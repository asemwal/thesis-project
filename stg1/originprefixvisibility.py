# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 12:26:36 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
purpose='originprefixvisibility'
f=sys.argv[1]
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    x = str(l).split("|");
    k=utils.getKey(x, [10,7])
    try:
        if x[1]  in ('R','A'):
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
        line += str(x[0])+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()