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


G= nx.DiGraph(g)
nodedegree={}
nodes = list(G.nodes())
for i in range(0,len(nodes)):
    try:
        nodedegree.update({nodes[i]:{'p2p':0,'s2s':0,'c2p':0,'p2c':0}})
    except KeyError as e:
        nodedegree.update({nodes[i]:{'p2p':0,'s2s':0,'c2p':0,'p2c':0}})
    

c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
for i in range(0,len(nodes)):
    edges = list(G.edges(nodes[i]))
    for j in range(0,len(edges)):
        nodedegree[nodes[i]][c[G.get_edge_data(edges[j][0],edges[j][1])['relationship']]]+=1
    

line=''
out = open(location+year+'proc/'+purpose+utils.getTimeStamp(file.name.split('/')[-1]), 'w')
out.write("H|p2p|s2s|p2c|c2p\n")
for k in nodedegree.keys():
    out.write(k+"|"+str(nodedegree[k]['p2p'])    +"|"+str(nodedegree[k]['s2s'])    +"|"+str(nodedegree[k]['p2c'])   +"|"+str(nodedegree[k]['c2p']) +"\n")    
out.flush()
out.close()



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
