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
stats = {'':0}
purpose='collectorpathvisibility'
f=sys.argv[1]
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while( l !=''):
    x = str(l).split("|");
    k=utils.getKey(x,[4,9])
    try:
#        stats[str(x[4])+"|"+str(x[5])+"|"+str(x[9])] =1
        stats[k] =1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        stats.update({k:1})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += str(x[0]) +"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()