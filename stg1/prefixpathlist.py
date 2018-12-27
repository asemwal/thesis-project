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
import utils
import sys
prefix_path = {'':[]}
purpose='prefixpathlist'
f=sys.argv[1]
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(l !=''):
    x = l.split("|");
    prefix=''
    path=''
    if(x[1] in ['R','A'] and len(x) >= 10):
        path = str(x[9])
        prefix = str(x[7])
    
    try:
        if path not in prefix_path[prefix]:
            prefix_path[prefix].append(path)
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        prefix_path.update({prefix:[path]})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = prefix_path.popitem()
        line += str(x[0])+ "|" + str(len(x[1])) +"|"+ str(",".join(x[1]))+"\n"
    except KeyError as e:
        break;

out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()
