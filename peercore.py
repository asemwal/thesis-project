# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 18:01:43 2018

@author: asemwal
"""

import math
import time
import networkx as nx
import utils

purpose='peercore'
g = nx.DiGraph()
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/proc/peerpathvisibility_1530709999_1530773099','r')
purpose='neighbour_cliques'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'


print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while l != '':
    x= l.split("|")
    if len(x) > 1:
        newases = x[1].split(" ")
        ases = [newases[0]]
        for i in range(1,len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
            x[1] = " ".join(ases)
        if x[0] == ases[0] and len(ases)>1:
            g.add_edge(ases[0], ases[1])
        else:
            g.add_edge(x[0], ases[0])
            if len(ases)>1:
                g.add_edge(ases[0], ases[1])
    l = (file.readline()).strip()
      
    
nodes = list(g.nodes())
for i in nodes:
    if g.degree(i) > 2:
        print("{}|{}".format(i, g.degree(i)))
