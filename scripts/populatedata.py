# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 18:44:14 2018

@author: asemwal
"""
import math
import time
import networkx as nx
import utils

def addresssize(s):
    x = s.split("/")[-1]
    return int(2**(32-int(x)))

def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def prepareline(x,a):
    line =''
    sep = "|"
    line += x[0]+sep +x[1]+sep+x[2]+sep + x[3]+ sep
    line += a[x[1]]['p2p']+sep+a[x[1]]['s2s']+sep+a[x[1]]['p2c']+sep+a[x[1]]['c2p']+sep+str(a[x[1]]['c'])+sep + str(a[x[1]]['v4']) + sep +str(len(a[x[1]]['pop'])) + sep
    line += a[x[2]]['p2p']+sep+a[x[2]]['s2s']+sep+a[x[2]]['p2c']+sep+a[x[2]]['c2p']+sep+str(a[x[2]]['c'])+sep+ str(a[x[2]]['v4']) + sep+str(len(a[x[2]]['pop'])) + sep
    line += a[x[3]]['p2p']+sep+a[x[3]]['s2s']+sep+a[x[3]]['p2c']+sep+a[x[3]]['c2p']+sep+str(a[x[3]]['c'])+sep+ str(a[x[3]]['v4']) + sep+str(len(a[x[3]]['pop'])) + sep
    line += x[4]+ '\n'
    return line
    
    
    
stats = {}
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/proc/nodedegreerelationships_tmp','r')
purpose='nodedegree'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
print("Beginning Processing at {}".format(time.time()))

#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==5 ):
        stats.update({x[0]:{'p2p':x[1],'s2s':x[2],'p2c':x[3],'c2p':x[4], 'c': 0,'v4': 0 , 'v6': 0 , 'pop': set() } })
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))
file = open('/home/asemwal/raw_data/2018/proc/centrallity_longpaths_1530662400_1530748799','r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    try:
        stats[x[0]]['c'] = x[2]
    except KeyError as e:
        pass
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))
file = open('/home/asemwal/raw_data/2018/proc/ipv4_originprefix_1530662400_1530748799','r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    try:
        stats[x[0]]['v4'] += addresssize(x[1])
    except KeyError as e:
        pass
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))

import json
file = open('/home/asemwal/raw_data/datasets/ix-asns_201802.jsonl','r')
l = (file.readline()).strip()
l = (file.readline()).strip()
while(l !=''):
    rec = json.loads(l)
    try:
        stats[rec['asn']]['pop'].add(rec['ix_id'])
    except KeyError as e:
        print rec
    l = (file.readline()).strip()

file = open('/home/asemwal/raw_data/2018/proc/traindata.txt_2','r')
file.close()
file = open('/home/asemwal/thesis/bgp-python/data/simulator/myrun/testdata','r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
print("Beginning Processing at {}".format(time.time()))

#file = open(location+year+'proc/'+f, 'r')
line = ''
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==5):
        try:
            line+= prepareline(x,stats)
        except KeyError as e:
            print(x)
            pass
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))
out = open('/home/asemwal/raw_data/2018/proc/traindata.txt_4', 'w')
out.write(line)
out.flush()
out.close()
