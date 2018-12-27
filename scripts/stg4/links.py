# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
f='/home/asemwal/raw_data/2018/proc/paths_append_1530662400_1530748799'
purpose='vp_links3'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    try:
        if l != '':
            ases= utils.getUniquePath(l.split(" "))
    except IndexError:
        print("In file {} line {}".format(f,l))
        pass
    peer = ases[0]
    for i in range(1, len(ases)):
        try:
            #stats[peer+"|"+ases[i-1]+"|"+ases[i] ] += 1
            stats[peer][ases[i-1]+"|"+ases[i]]=1
        except KeyError as e:
            stats.update({peer:{ases[i-1]+"|"+ases[i] :1}})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            #line += str(k) + "|"+ str(stats[k])+"\n"
            line += str(x[0].strip())+"#"+ ",".join(x[1].keys()) +"#"+ str(len(x[1].keys() ))+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f.split("/")[-1]), 'w')


out.write(line)
out.flush()
out.close()