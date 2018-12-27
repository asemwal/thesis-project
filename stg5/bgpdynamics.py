# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 18:34:29 2018

@author: asemwal
"""
import math
import time
import networkx as nx
import utils

relationships= {}
peer = set()
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
l = (file.readline()).strip()
while l != '':
    x = l.split("|")
    if x[2] == 'provider-to-customer':
        w1 = 1
        w2 = 4
    elif x[2] == 'sibling-to-sibling':
        w1=2
        w2=2
    elif x[2] == 'peer-to-peer':
        w1 = 3
        w2 = 3
    else :
        w1 = 4
        w2 = 1
    xx = x[0:2]
    relationships.update({"|".join(xx): w1})
    xx.reverse()
    relationships.update({"|".join(xx): w2})
    l = (file.readline()).strip()


G = nx.DiGraph()
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
        peer.add(x[0])
        G.add_edge(str(x[1]), str(x[2]), weight = relationships[str(x[1]) + "|" + str(x[2])])
        G.add_edge(str(x[2]), str(x[1]), weight = relationships[str(x[2]) + "|" + str(x[1])])
    l = (file.readline()).strip()
    
print(G.number_of_edges())
print(G.number_of_nodes())


    
   