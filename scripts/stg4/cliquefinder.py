# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 15:53:00 2018

@author: asemwal
"""

import networkx as nx
c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}

def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def degreemap(b):
    global c
    nodedegree = dict()
    nodes = list(b.nodes())
    for i in nodes:
        nodedegree.update({i:{'p2p':0,'s2s':0,'c2p':0,'p2c':0}})
    for i in nodes:
        edges = list(b.edges(i))
        for j in edges:
            nodedegree[i][c[b.get_edge_data(j[0],j[1])['relationship']]]+=1
    return nodedegree
arank= {'0': 'peer-to-peer', '-1': 'provider-to-customer'}
    
def generategraphARank(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
#    c = {0: 'peer-to-peer', -1: 'provider-to-customer'}
    g = nx.DiGraph()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            g.add_edge(x[0], x[1] , relationship =  (arank[x[2]]))
            g.add_edge(x[1], x[0] , relationship = inverselink( arank[(x[2])]))
            
        
        l = str(file.readline()).strip()
    return g

def generategraphAStop(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
#    c = {0: 'peer-to-peer', -1: 'provider-to-customer'}
    g = nx.DiGraph()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            g.add_edge(x[0], x[1] , relationship =  (x[2]))            
        
        l = str(file.readline()).strip()
    return g



def generategraph2(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
#    c = {0: 'peer-to-peer', -1: 'provider-to-customer'}
    g = nx.DiGraph()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            g.add_edge(x[0], x[1] , relationship =  (x[2]))
            g.add_edge(x[1], x[0] , relationship = inverselink( (x[2])))
            
        
        l = str(file.readline()).strip()
    return g
    
graphfile1='/home/asemwal/raw_data/scripts/plots/ARank/20181001.as-rel2.txt'
y=generategraphARank(graphfile1)
d=degreemap(y)
nodes = []
file = open('/home/asemwal/raw_data/scripts/plots/ARank/20181001.as-t1-cliques.txt','w')
for i in d.keys():
    if d[i]['c2p'] == 0:
        nodes.append(i)        

x=nx.DiGraph(y.subgraph(nodes))
e= list(x.edges())
for i in e:
    if x.get_edge_data(i[0],i[1])['relationship'] != 'peer-to-peer':
        x.remove_edge(i[0],i[1])
        

file.write("ASes with no providers|"+str(len(nodes))+"|"+",".join(nodes))
file.write('\n')
e= list(x.edges())
len(e)
a=nx.Graph(x)
c=nx.find_cliques(a)
i = c.next()
tier1 = set()
while True == True:
    nodes = list(i)
    file.write(str(len(nodes))+"|" + ", ".join(nodes))
    file.write('\n')
    if len(tier1) < len(nodes):
        tier1 = set(nodes)
    try:
        i = c.next()
    except StopIteration as e:
        break
        
tier2 = set()
graphfile1='/home/asemwal/raw_data/scripts/plots/ARank/20181001.as-rel2.txt'
y=generategraphARank(graphfile1)
file.write("Tier1|"+str(len(tier1))+"|" + ", ".join(list(tier1)))
file.write('\n')
mind_t2 = 0
for i in tier1:
    edges = list(y.edges(i))
    for j in edges:
        if y.get_edge_data(j[0],j[1])['relationship'] == 'provider-to-customer':
            if mind_t2 < d[j[1]]['p2p'] :
                mind_t2=d[j[1]]['p2p'] 
            if d[j[1]]['p2p'] > 25:
                tier2.add(j[1])

file.write("Tier2|"+str(len(tier2))+"|"+ str(mind_t2)+"|" + ", ".join(list(tier2)))
file.write('\n')
tier3 = set()
mind_t3 = 0
for i in tier2:
    edges = list(y.edges(i))
    for j in edges:
        if y.get_edge_data(j[0],j[1])['relationship'] == 'provider-to-customer':
            tier3.add(j[1])
            if mind_t3 < d[j[1]]['p2p'] :
                mind_t3=d[j[1]]['p2p'] 

file.write("Tier3|"+str(len(tier3))+"|"+ str(mind_t3)+"|" + ", ".join(list(tier3)))
file.write('\n')
tier4 = set()
mind_t4 = 0
for i in tier3:
    edges = list(y.edges(i))
    for j in edges:
        if y.get_edge_data(j[0],j[1])['relationship'] == 'provider-to-customer':
            tier4.add(j[1])
            if mind_t4 < d[j[1]]['p2p'] :
                mind_t4=d[j[1]]['p2p'] 

file.write("Tier4|"+str(len(tier4))+"|"+ str(mind_t4)+"|" + ", ".join(list(tier4)))
file.write('\n')

tier5 = set()
mind_t5 = 0
for i in tier4:
    edges = list(y.edges(i))
    for j in edges:
        if y.get_edge_data(j[0],j[1])['relationship'] == 'provider-to-customer':
            tier5.add(j[1])
            if mind_t5 < d[j[1]]['p2p'] :
                mind_t5=d[j[1]]['p2p'] 

file.write("Tier5|"+str(len(tier5))+"|"+ str(mind_t5)+"|" + ", ".join(list(tier5)))
file.write('\n')

tier6 = set()
for i in tier5:
    edges = list(y.edges(i))
    for j in edges:
        if y.get_edge_data(j[0],j[1])['relationship'] == 'provider-to-customer':
            tier6.add(j[1])

file.write("Tier6|"+str(len(tier6))+"|" + ", ".join(list(tier6)))
file.write('\n')
file.write("Tier2|"+str(len(tier2.difference(tier1)))+"|" + ", ".join(list(tier2.difference(tier2.difference(tier1)))))
file.write('\n')
file.write("Tier3|"+str(len(tier3.difference(tier2.union(tier1))))+"|" + ", ".join(list(tier3.difference(tier2.union(tier1)))))
file.write('\n')
file.write("Tier4|"+str(len(tier4.difference(tier3.union(tier2.union(tier1)))))+"|" + ", ".join(list(tier4.difference(tier5.union(tier6)))))
file.write('\n')
file.write("Tier5|"+str(len(tier5.union(tier6)))+"|" + ", ".join(list(tier5.union(tier6))))
file.write('\n')


file.close()