# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 13:44:30 2018

@author: asemwal
"""

import utils
import networkx as nx
import time
import random as rand
import networkx.algorithms.isomorphism as iso

edgeslist = list()
def addedges(vector):
    edgeslist.append(list(vector))
count = 0
def stgN(nodes = list(), stg = 0, vector = list()):
    global count, depth
    if stg == depth:
        nodeList = list(nodes)
        for i in nodeList:
            if i not in vector:
                vector.insert(0,i)
            #G = nx.DiGraph(g.subgraph(vector))
                print(vector)
                addedges(v)
                vector.pop(0)
                count+=1
    else:
        stg_N = list(nodes)
        if len(stg_N) > depth:
            newElem  = stg_N.pop(0)
        else: 
            return
        vector.append(newElem)
        stg = stg +1
        stgN(stg_N,stg,vector)
nodes =  list( range(10,20))
depth = 9
while len(nodes) > 0:
    v=list()
    i = nodes.pop(0)
    stg1 = list(nodes) 
    #stg1.remove(i)
    v.append(i)
    stgN(stg1 , 2, v)