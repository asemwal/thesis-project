# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 11:36:20 2018

@author: asemwal
"""
import math
import time
import networkx as nx
import utils

def expandnetwork(g, node, network):
    custnet = set()
    nettype = 'customer'
    visit = list(network[node][nettype]['net'])
    while len(visit) > 0:
        visiting = visit.pop(0)
        custnet.add(visiting)
        visit = list(network[visiting][nettype]['net']) + visit
        
    network[node][nettype]['net'] = set(custnet)
    network[node][nettype]['len'] = len(set(custnet))
    custnet = set()
    nettype = 'customer'
    visit = list(network[node]['peer']['net'])
    while len(visit) > 0:
        visiting = visit.pop(0)
        custnet.add(visiting)
        visit = visit + list(network[visiting][nettype]['net'])
        
    network[node]['peer']['net'] = set(custnet)
    network[node]['peer']['len'] = len(set(custnet))
    return network
        
        
    

def shortestpath(g,src,dst, network):
    G = nx.DiGraph(g)
    curr = src
    end = src
    sgnodes =set()
    sgnodes.add(src)
    if network[src]['expand'] == True:
        network = expandnetwork(g, src , network)
        network[src]['expand'] = False
    
    if dst in network[src]['customer']['net']:
        return sgnodes.union(network[src]['customer']['net'])
    elif dst in network[src]['peer']['net']:
        return sgnodes.union(network[src]['peer']['net'])
    providers = set(network[src]['provider']['net'])
    if dst in providers:
        return sgnodes.union(providers)
    providers = list(providers)
    temp = []
    while len(providers) > 0:
        provider = providers.pop(0)
        sgnodes.add(provider)
        if network[provider]['expand'] == True:
            network = expandnetwork(g, provider , network)
            network[provider]['expand'] = False
        if dst in network[provider]['customer']['net']:
            return sgnodes.union(network[src]['customer']['net'])
        elif dst in network[provider]['peer']['net']:
            return sgnodes.union(network[provider]['peer']['net'])
        elif dst in set(network[provider]['provider']['net']):
            return sgnodes.union(network[provider]['provider']['net'])
        else:
            temp = temp + list(network[provider]['provider']['net'])
        if len(providers) == 0:
            providers = list(temp)
            temp = list()
    return sgnodes     


def customernetwork(g, node):
     c  = set()
     a=set()
     a.add(node)
     #print(node)
     while len(a) >0:
         x = a.pop()
         r = list(g.edges(x))
         for i in range(0,len(r)):
             if (g.get_edge_data(r[i][0], r[i][1])['relationship'] == 'provider-to-customer' or g.get_edge_data(r[i][0], r[i][1])['relationship'] == 'sibling-to-sibling' ):
                 
                 if r[i][1] not in c:
                     
                     #a.add(r[i][1])
                     c.add(r[i][1])
     return c
  
def peernetwork(g, node, network):
     c  = set()
     a=set()
     a.add(node)
     #print(node)
     while len(a) >0:
         x = a.pop()
         r = list(g.edges(x))
         for i in range(0,len(r)):
             if (g.get_edge_data(r[i][0], r[i][1])['relationship'] == 'peer-to-peer' ):
                 
                 if r[i][1] not in c and r[i][1] != node:
                     c.add(r[i][1])
                     #c = c.union(network[r[i][1]]['customer']['net'] )
     return c

def provider(g, node):
     c  = set()
     a=set()
     a.add(node)
     #print(node)
     while len(a) >0:
         x = a.pop()
         r = list(g.edges(x))
         for i in range(0,len(r)):
             if (g.get_edge_data(r[i][0], r[i][1])['relationship'] == 'customer-to-provider' ):
                 
                 if r[i][1] not in c and r[i][1] != node:
                     c.add(r[i][1])
     return c   
          
def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r



f='relationships'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/old_proc/edgelist','r')
purpose='networks'
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
        if str(x[2]) == 'customer-to-provider':
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
        elif str(x[2]) == 'provider-to-customer':
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])
        else:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])    
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))

nodes = list(g.nodes())
network = {}
for i in range(0,len(nodes)):
    providers = set(provider(g,nodes[i]))
    network.update({nodes[i]:{'expand':True , 'provider':{'net':providers,'len':len(providers)},'customer':{'net': set(), 'len':0},'peer':{'net':set(),'len':0}}})
for i in range(0, len(nodes)):
    c = customernetwork(g,nodes[i])
    network[nodes[i]]['customer']['net'] = c
    network[nodes[i]]['customer']['len'] = len(c)
    print(i)
    
print("Identified Customer List at {}".format(time.time()))
for i in range(0, len(nodes)):
    p = peernetwork(g,nodes[i], network)
    #peer.update({nodes[i]: (p , len(p))})
    network[nodes[i]]['peer']['net'] = p
    network[nodes[i]]['peer']['len'] = len(p)
print("Identified Peer List at {}".format(time.time()))


for i in range(0, len(nodes)):
    print(i)
    network = expandnetwork(g, nodes[i], network)

print("Network expansion complete at {}".format(time.time()))
"""
print('finding cliques')
G=nx.Graph(g)
a=nx.find_cliques(G)
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
"""
