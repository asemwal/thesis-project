# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 11:36:20 2018

@author: asemwal
"""
import math
import time
import networkx as nx
import utils

y='6939,3320,6762,1299,2914,3356,6453,3491,286,12956,6461,6830,5580,3257,209,7922,2828,4134,20940,5511,1239,701,7018'.split(',')
y='3320,6762,1299,2914,3356,6453,3491,286,12956,6461,6830,5580,3257,209,7922,2828,4134,20940,5511,1239,701,7018'.split(',')
g = nx.Graph()
f='links'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/proc/link_monitor_aspathsdups_deduped','r')
purpose='neighbour_cliques'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'


print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==4 ):
        g.add_edge(str(x[1]), str(x[2]) )
    l = (file.readline()).strip()
    
    
print(g.number_of_edges())
print(g.number_of_nodes())
tier2 = set()
neighbour = {}
for i in range(0, len(y)):
    neighbourlist = set()
    r = g.neighbors(y[i])
    while True:
        try:
            asn = r.next()
            if asn not in y:
                neighbourlist.add(asn)
                tier2.add(asn)
        except StopIteration:
            break
    neighbour.update({y[i]:neighbourlist})
line=""
while True:
    try:
        r = neighbour.popitem()
        line+= r[0]+"|" + str(len(r[1])) +"|"+ ", ".join(list(r[1]))+"\n"
    except KeyError:
        break;
line+="\n\n\n\n\n\nPrinting Tier2 Networks\n"
line+= 'Number of T2 networks: '+ str(len(tier2)) +'\n'
line+= ", ".join(list(tier2))
t2 = list(tier2)
tier3 = set()
neighbour = {}
for i in range(0, len(t2)):
    neighbourlist = set()
    r = g.neighbors(t2[i])
    while True:
        try:
            asn = r.next()
            if asn not in y and asn not in t2:
                neighbourlist.add(asn)
                tier3.add(asn)
        except StopIteration:
            break
    neighbour.update({t2[i]:neighbourlist})


if True:
    f='aspathsdups_deduped'
    file = open('/home/asemwal/thesis/bgpreader/proc/'+notier1, 'r')
    l = str(file.readline()).strip()
    peer = {}
    while(l !=''):
        x = l.split(" ")
        try:
            peer[x[0]] =1
        except KeyError as e:
            peer.update({x[0]:0})
            
    for k in peer.keys():
        g.remove_node(k);
    
    



print('finding cliques')
a=nx.find_cliques(g)
print(a)
line=''
while(True):
    try:
        r=a.next()
        line += str(len(r))+"|"+",".join(r) +"\n"
    except StopIteration as e:
        break;
        pass
out = open(location+year+'proc/'+purpose+utils.getTimeStamp(file.name.split('/')[-1]), 'w')
out.write(line)
out.flush()
out.close()



