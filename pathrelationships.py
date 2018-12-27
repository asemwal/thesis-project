# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 21:43:51 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 01:18:21 2018

@author: asemwal
"""
import math
import time
import utils
import networkx as nx


def inverselink(r):
    if r == 'c2p':
        return 'p2c'
    elif r == 'p2c':
        return 'c2p'
    else:
        return r
        
stats ={}
relationship ={}
file = open('/home/asemwal/raw_data/2018/proc/ascount_1530662400_1530748799','r')
purpose='pathappendpathrelationship'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip();
while l !='':
    asn=l.split("|")[0]
    relationship.update({asn:dict()})
    l = str(file.readline()).strip();

print("{}: Neighbour list initialized... now populate neighbours".format(time.time()))
file.close()

"""
For all paths in AS update neighbour set and after that count degree
"""
f='/home/asemwal/raw_data/2018/proc/ascount_1530662400_1530748799'
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
l = str(file.readline()).strip();

c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}

while l!='':
    ases = l.split("|")
    if True:
        relationship[ases[0]].update({ases[1]:c[ases[2]]})
        relationship[ases[1]].update({ases[0]:inverselink(c[ases[2]])})
    l = str(file.readline()).strip();

    
print("{}: end of neighbour and degree processing".format(time.time()))
file.close()

file = open('/home/asemwal/raw_data/2018/proc/paths_append_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    aspath = l.split(" ")
    relationshipaspath = []
    for i in range(1, len(aspath)):
        relationshipaspath.append(relationship[aspath[i-1]][aspath[i]]) 
    
    try:
        stats[" ".join(relationshipaspath)] += 1
    except KeyError as e:
        stats.update({" ".join(relationshipaspath):1})
    
    l = str(file.readline()).strip();

print("{}: end of paths generation".format(time.time()))
file.close()

out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
while(True):
    try:
        x = stats.popitem()
        out.write(str(x[0])+"|"+ str(x[1])+"\n")
    except KeyError as e:
        break;
#out.write(line)
out.flush()
out.close()
