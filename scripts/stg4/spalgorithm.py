# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 21:15:38 2018

@author: asemwal
"""

import math
import time
import networkx as nx
import utils
def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def getpeers(g, node):
    c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
    peer = set()
    neighbors = list(g.neighbors(node))
    for i in  neighbors:
        if c[g.get_edge_data(node,i)['relationship']] == 'p2p':
            peer.add(i)
    return peer
    
def getproviders(g, node, path):
    c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
    providers = set()
    neighbors = list(g.neighbors(node))
    for i in  neighbors:
        if c[g.get_edge_data(node,i)['relationship']] == 'c2p':
            providers.add(i)
    return providers.difference(set(path.split(" ")))

def getcustomers(g, node,path):
    c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
    customers = set()
    neighbors = list(g.neighbors(node))
    for i in  neighbors:
        if c[g.get_edge_data(node,i)['relationship']] == 'p2c':
            customers.add(i)
    return customers.difference(set(path.split(" ")))
    
def getsiblings(g, node,path):
    c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
    siblings = set()
    neighbors = list(g.neighbors(node))
    for i in  neighbors:
        if c[g.get_edge_data(node,i)['relationship']] == 's2s':
            siblings.add(i)
    return siblings.difference(set(path.split(" ")))

def getneighbors(g, node, path):
    neighbors = set(g.neighbors(node))
    #print(path)
    #print(neighbors)
    return neighbors.difference(set(path.split(" ")))

def getrelationship(g, path):
    aspath = path.split(" ")
    c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
    if len(aspath) >=2:
        return c[g.get_edge_data(aspath[1],aspath[0])['relationship']]
    else:
        return "self"

f='relationships'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/old_proc/relationships','r')
purpose='nodedegree'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
weight = {'provider-to-customer':1,'sibling-to-sibling':1,'peer-to-peer':2,'customer-to-provider':4}
g = nx.DiGraph()
print("Beginning Processing at {}".format(time.time()))

#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        inv = inverselink(str(x[2]))
        g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
        g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])
        
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))

path = dict()
nodes = list(g.nodes())
for i in nodes:
    path.update({i:{}})
for i in nodes:
    for j in nodes:
        if i != j:
            path[i][j] = list()
        else:
            path[i][j] = list()
            path[i][j].append(i)

print("begin:{}".format(time.time()))
k = list(path.keys())
for src in k:
    neighbours = set(g.neighbors(src))
    temp = dict()
    count = 0 
    done = set()
    done.add(src)
    temp.update({src:neighbours})
    source, neighbours = temp.popitem()
    while len(neighbours) >0:
        for dst in neighbours:
            #done.add(dst)
            print(len(done))
            count +=1
            partialpath = []
            if 0 == 0:
                partialpath = list(path[src][source][-1].split(" "))
                partialpath.insert(0,dst)
                
            relation = getrelationship(g, " ".join(partialpath))
            #print("source :{}\t relation:{}".format(source, relation))
            n = set()
            if relation == 'p2p':
                n = n.union(getcustomers(g,dst," ".join(partialpath)))
                #print("p2p stg1 n:{}".format(n))
                n = n.union(getsiblings(g,dst," ".join(partialpath)))
                #print("p2p stg2 n:{}".format(n))
            elif relation == 'p2c':
                n = n.union(getcustomers(g,dst," ".join(partialpath)))
                n = n.union(getsiblings(g,dst," ".join(partialpath)))
            else:
                n = n.union(getneighbors(g,dst," ".join(partialpath)))                
            #n = set(g.neighbors(dst))
            temp.update({dst:n})
            #print("stg final n:{}".format(n))
            path[src][dst].append(" ".join(partialpath))
            if count == len(neighbours):
                neighbours = set()
                source = ''
                for x in temp.keys():
                    temp[x].difference_update(done)
                while len(neighbours) == 0:
                    try:
                        source, neighbours = temp.popitem()
                    except KeyError as err:
                        break                   
                count = 0
    
for src in path:
    for dst in path[src]:
        print("{}->{}::{}".format(dst,src,path[src][dst]))

print("end:{}".format(time.time()))