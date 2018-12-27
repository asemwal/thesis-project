# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 12:31:31 2018

@author: asemwal
"""


import networkx as nx
c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}
def generategraph(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
    g = nx.DiGraph()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            g.add_edge(x[0], x[1] , relationship = x[2])
            g.add_edge(x[1], x[0] , relationship = inverselink(x[2]))


        l = str(file.readline()).strip()
    return g

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
    
    
g=generategraph('/home/asemwal/raw_data/2018/proc/relationships')
dmap = degreemap(g)
    
out= open('/home/asemwal/raw_data/2018/proc/dmaprel','w')
for i in dmap.keys():
    l = list()
    l.append(i)
    l.append(str(dmap[i]['p2p']))
    l.append(str(dmap[i]['p2c']))
    l.append(str(dmap[i]['s2s']))
    out.write("|".join(l)+"\n")
    
out.close()

p2p = dict()
total = 0
for i in dmap.keys():
    try:
        p2p[dmap[i]['p2p']]+=1
        total +=1
    except KeyError:
        p2p[dmap[i]['p2p']] =1
        total +=1

out= open('/home/asemwal/raw_data/2018/proc/p2p_distribution','w')
for i in p2p.keys():
    l = list()
    l.append(str(i))
    l.append(str(p2p[i]))
    l.append(str(float(p2p[i])/total))
    out.write("|".join(l)+"\n")
    
out.close()        
p2p = dict()
total = 0
for i in dmap.keys():
    try:
        p2p[dmap[i]['p2c']]+=1
        total +=1
    except KeyError:
        p2p[dmap[i]['p2c']] =1
        total +=1

out= open('/home/asemwal/raw_data/2018/proc/p2c_distribution','w')
for i in p2p.keys():
    l = list()
    l.append(str(i))
    l.append(str(p2p[i]))
    l.append(str(float(p2p[i])/total))
    out.write("|".join(l)+"\n")
    
out.close()        

p2p = dict()
total = 0
for i in dmap.keys():
    try:
        p2p[dmap[i]['c2p']]+=1
        total +=1
    except KeyError:
        p2p[dmap[i]['c2p']] =1
        total +=1

out= open('/home/asemwal/raw_data/2018/proc/c2p_distribution','w')
for i in p2p.keys():
    l = list()
    l.append(str(i))
    l.append(str(p2p[i]))
    l.append(str(float(p2p[i])/total))
    out.write("|".join(l)+"\n")
    
out.close()        
