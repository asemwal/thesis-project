# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 21:54:13 2018

@author: asemwal
"""
import utils
import networkx as nx
import time
import random as rand
import networkx.algorithms.isomorphism as iso
def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def motifcompiler(G):
    global keys, motif
    nodes = list(G.nodes())
    mapping = dict()
    i=0
    newG = nx.DiGraph()
    for x in keys:
        if i < len(nodes):
            mapping.update({nodes[i]:x})
            i+=1
    edges = list(G.edges())
    
    for e in edges:
        try:
            newG.add_edge(mapping[e[0]], mapping[e[1]], relationship=G.get_edge_data(e[0],e[1])['relationship'])   
        except KeyError:
            print(e)
    return newG
 
        
cust = set()
visited = list()
customer = dict()
dfsvisited = list()
dfscustomer = dict()
bfsvisited = list()
bfscustomer = dict()
g = nx.DiGraph()
f='links'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/old_proc/relationships','r')
purpose='motif'
proc = 'proc/'
if len(file.name.split("/")) ==7:
    proc = str(file.name.split("/")[5])+'/'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'


print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        if x[2] == 'customer-to-provider':
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = 'provider-to-customer')
        else:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])
            
    l = (file.readline()).strip()
print("working...")

nodes = list(g.nodes())

        
edgeset = list()
graphset = list()
motif = set()
count = 0
nodes=list(g.nodes())
"""
sg=list()
while True == True:
    sg=list()
    while len(sg) < 5:
        inp = nodes[rand.randint(0,len(nodes)-1)]
        if inp not in sg:
            sg.append(inp)
    temp = nx.DiGraph(nx.subgraph(g,sg))
    if nx.is_connected(nx.Graph(temp)) == True:
        break
len(sg)
G=nx.subgraph(g,sg)
oldG= nx.DiGraph(g)
g=nx.DiGraph(G)
"""

def addedges(G):
    global edgeset,graphset
    graphset.append(G)
    edges = list(G.edges())
    edgeset.append(edges)
"""
def stgN(nodes = list(), stg = 0, vector = list()):
    global count
    if stg == 2:
        nodeList = list(nodes)
        for i in nodes:
            vector.insert(0,i)
            G = nx.DiGraph(g.subgraph(vector))
            print(vector)
            vector.pop(0)
            count+=1
            if nx.is_connected(nx.Graph(G)) == True:
                addedges(G)
    else:
        stg_N = list(nodes)
        newElem  = stg_N.pop(0)
        vector.append(newElem)
        stg = stg +1
        stgN(stg_N,stg,vector)

for i in nodes:
    v=list()
    stg1 = list(nodes) 
    stg1.remove(i)
    v.append(i)
    stgN(stg1 , 1, v)
"""    
print("Begin: {}".format(time.time()))  
"""
stg1 = list(g.nodes) 

while len(stg1) > 0:
    i=stg1.pop(0)
    stg2 = list(stg1)
    for j in stg2:
        stg3 = list(stg2)
        stg3.remove(j)
        for k in stg3:
            
                G = nx.DiGraph(g.subgraph([i,j,k]))
                count +=1
                if nx.is_connected(nx.Graph(G)) == True:
                    addedges(G)
"""
combinations = list(itertools.combinations(nodes, 5))
print(count)                    
print("End: {}".format(time.time()))
keys = ['i','j','k','l','m','n']


em = iso.categorical_edge_match('relationship', '')


for x in graphset:
    q=motifcompiler(x)
    matched = False
    for y in motif:
        if nx.is_isomorphic(q,y, edge_match=em) == False:
            pass
        else:
            matched = True
            break;
    if matched == False:
        motif.add(x)
        
        
motifs = list(motif)
  
out = open(location+year+proc+purpose+utils.getTimeStamp(file.name.split('/')[-1]), 'w')
for c in motifs:
    l='MOTIF+++++\n'
    edges = list(c.edges())
    for e in edges:
        l+= e[0] +"-->" + c.get_edge_data(e[0],e[1])['relationship'] + "-->" + e[1] + "\n"
    l+='MOTIF+++++\n'
    out.write(l)
    out.flush()
    
out.close()
