# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 13:01:09 2018

@author: asemwal
"""

#!/usr/bin/env python
"""
Compute some network properties for the lollipop graph.
"""
#    Copyright (C) 2004 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from networkx import *

import math
import time
import networkx as nx
G = nx.Graph()
f='relationships'
print(time.time())
file = open('/home/asemwal/raw_data/2018/proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        G.add_edge(str(x[0]), str(x[1]))
    l = (file.readline()).strip()

nodes = set()
file = open('/home/asemwal/raw_data/2018/proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        nodes.add(str(x[0]))
        nodes.add(str(x[1]))
    l = (file.readline()).strip()
    
    
pathlengths=[]

print("source vertex {target:length, }")
for v in G.nodes():
    spl=single_source_shortest_path_length(G,v)
    #print('%s %s' % (v,spl))
    for p in spl.values():
        pathlengths.append(p)

print('')
print("average shortest path length %s" % (sum(pathlengths)/len(pathlengths)))

# histogram of path lengths
dist={}
for p in pathlengths:
    if p in dist:
        dist[p]+=1
    else:
        dist[p]=1

print('')
print("length #paths")
verts=dist.keys()
for d in sorted(verts):
    print('%s %d' % (d,dist[d]))

print("radius: %d" % radius(G))
print("diameter: %d" % diameter(G))
print("eccentricity: %s" % eccentricity(G))
print("center: %s" % center(G))
print("periphery: %s" % periphery(G))
print("density: %s" % density(G))