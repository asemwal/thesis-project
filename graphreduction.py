# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 18:44:14 2018

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



f='relationships'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
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
    inv = inverselink(str(x[2]))
    if(len(x) ==3 and True == False):
        if str(x[2]) == 'customer-to-provider':
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
        elif str(x[2]) == 'provider-to-customer':
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])
        else:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
    else:
        g.add_edge(str(x[0]), str(x[1]) ,  relationship = str(x[2]), weight = weight[str(x[2])])
        g.add_edge(str(x[1]), str(x[0]) ,  relationship = inv , weight = weight[inv])
    l = (file.readline()).strip()

print("Graph Initialized at {}".format(time.time()))


G= nx.DiGraph(g)

degree=dict(G.degree())
degreemap = {}
for k in degree.keys():
    try:
        degreemap[degree[k]].append(k)
    except KeyError as e:
        degreemap.update({degree[k]:[k]})
        
degreemap[1]
len(degreemap[1])


removelist =  degreemap[2]
p2c=0
p2p=0
s2s=0
for i in range(0,len(removelist)):
    try:
        a=list(G.edges(removelist[i]))
        for j in range(0,len(a)):
            if G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'provider-to-customer':
                print(a[j][0])
                p2c+=1
            elif G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'peer-to-peer':
                p2p+=1
            elif G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'sibling-to-sibling':
                s2s+=1
    except IndexError as e:
        pass

print("p2p|p2c|s2s")
print("{}|{}|{}".format(p2p,p2c,s2s))




"""
for i in range(0, len(nodes)):
    network = expandnetwork(g, nodes[i], network)

print("Network expansion complete at {}".format(time.time()))

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

G= nx.DiGraph(g)

degree=dict(G.degree())
degreemap = {}
for k in degree.keys():
    try:
        degreemap[degree[k]].append(k)
    except KeyError as e:
        degreemap.update({degree[k]:[k]})
        
degreemap[1]
len(degreemap[1])


removelist =  degreemap[1]
p2c=0
p2p=0
s2s=0
for i in range(0,len(removelist)):
    try:
        a=list(G.edges(removelist[i]))
        for j in range(0,len(a)):
            if G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'provider-to-customer':
                print(a[j][0])
                p2c+=1
            elif G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'peer-to-peer':
                p2p+=1
            elif G.get_edge_data(a[j][0],a[j][1])['relationship'] == 'sibling-to-sibling':
                s2s+=1
    except IndexError as e:
        pass

print("p2p|p2c|s2s")
print("{}|{}|{}".format(p2p,p2c,s2s))


"""
