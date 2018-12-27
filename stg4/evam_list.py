# -*- coding: utf-8 -*-
"""
Created on Sat Aug 18 16:42:28 2018

@author: asemwal
"""

stats={}
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
    try:
        line += x[0]+sep +x[1]+sep+x[2]+sep + x[3]+ sep
        line += a[x[1]]['degree']+sep+a[x[1]]['p2p']+sep+a[x[1]]['s2s']+sep+a[x[1]]['p2c']+sep+a[x[1]]['c2p']+sep+str(a[x[1]]['c'])+sep+str(a[x[1]]['ec'])+sep + str(a[x[1]]['v4']) + sep +str(len(a[x[1]]['pop'])) + sep
        line += a[x[2]]['degree']+sep+a[x[2]]['p2p']+sep+a[x[2]]['s2s']+sep+a[x[2]]['p2c']+sep+a[x[2]]['c2p']+sep+str(a[x[2]]['c'])+sep+str(a[x[2]]['ec'])+sep+ str(a[x[2]]['v4']) + sep+str(len(a[x[2]]['pop'])) + sep
        line += a[x[3]]['degree']+sep+a[x[3]]['p2p']+sep+a[x[3]]['s2s']+sep+a[x[3]]['p2c']+sep+a[x[3]]['c2p']+sep+str(a[x[3]]['c'])+sep+str(a[x[3]]['ec'])+sep+ str(a[x[3]]['v4']) + sep+str(len(a[x[3]]['pop'])) + sep
        line += x[4]+ '\n'
    except KeyError as e:
        line=""
        pass
    return line
    
    
    
stats = {}
monitor_eventset=dict()
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
        stats.update({x[0]:{'degree': str(int(x[1])+int(x[2])+int(x[3])+int(x[4])),'p2p':str(float(x[1])/(int(x[1])+int(x[2])+int(x[3])+int(x[4]))),'s2s':str(float(x[2])/(int(x[1])+int(x[2])+int(x[3])+int(x[4]))),'p2c':str(float(x[3])/(int(x[1])+int(x[2])+int(x[3])+int(x[4]))),'c2p':str(float(x[4])/(int(x[1])+int(x[2])+int(x[3])+int(x[4]))), 'c': 0,'v4': 0 , 'v6': 0 , 'pop': set() ,'ec':0} })
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
file = open('/home/asemwal/raw_data/2018/proc/eigenvectorcentrallityrelationships','r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    try:
        stats[x[0]]['ec'] = x[1]
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



monitor = set()
monitor_file = open('/home/asemwal/raw_data/monitor','r')
l = str(monitor_file.readline()).strip()
while l != '':
    monitor_eventset.update({l:{'bad':set(),'good':set()}})
    monitor.add(l)
    l = str(monitor_file.readline()).strip()
    
event = dict()
event_file = open('/home/asemwal/raw_data/evam_list','r')
l = str(event_file.readline()).strip()
while l != '':
    x = l.split("|")
    event.update({x[0]:{'attacker':x[2],'victim':x[1], 'misc':x[4]}})
    l = str(event_file.readline()).strip()
evam = ""
sep = "|"
out = open('/home/asemwal/raw_data/evam_file_dummy','w')
d='/home/asemwal/raw_data/newbgp/'
for k in event.keys():
    bgpdata = open(d+k+'.txt','r')
    l = str(bgpdata.readline()).strip()
    good = monitor.copy()
    bad = set()
    while l != '':
        x = l.split("|")
        if x[1] in ['R','A']:
            if event[k]['attacker'] in x[9].split(" ") and x[5] in good:
                good.remove(x[5])
                bad.add(x[5])
        l = str(bgpdata.readline()).strip()
        
    for g in good:
        monitor_eventset[g]['good'].add(k)
        line = prepareline([k,event[k]['victim'],event[k]['attacker'],g,'0'] , stats)
        #evam += k+sep+ event[k]['victim']+sep+event[k]['attacker']+sep+g+sep+'0'+'\n'
        evam+=line
    for b in bad:
        monitor_eventset[b]['bad'].add(k)
        line = prepareline([k,event[k]['victim'],event[k]['attacker'],b,'1'] , stats)
        #evam += k+sep+ event[k]['victim']+sep+event[k]['attacker']+sep+b+sep+'1'+'\n'
        evam+=line
    out.write(evam)
    out.flush()
    evam=''
out.close()

                
out = open('/home/asemwal/raw_data/monitor_event_list','w')

for k in monitor_eventset.keys():
    l = k+sep +str(len(monitor_eventset[k]['bad']))+sep + ",".join(list(monitor_eventset[k]['bad'])) +sep +str(len(monitor_eventset[k]['good']))+sep + ",".join(list(monitor_eventset[k]['good'])) +"\n"
    out.write(l)
    out.flush()
    
out.close()

        