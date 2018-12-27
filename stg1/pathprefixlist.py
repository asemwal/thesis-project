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
path_prefix = {'':[]}
purpose='pathprefixlist'
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
        if prefix not in path_prefix[path]:
            path_prefix[path].append(prefix)
    except AttributeError as e:
        print(l)
        print(path_prefix)
        pass
    except KeyError as e:
        path_prefix.update({path:[prefix]})
    except IndexError as e:
        print(path_prefix)
        print(l)
        print(path)
        print(prefix)
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = path_prefix.popitem()
        line += str(x[0])+ "|" + str(len(x[1])) +"|"+ str(",".join(x[1]))+"\n"
    except KeyError as e:
        break;

out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()