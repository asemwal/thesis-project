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
import itertools as itr


def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def getcode(r):
    if r == 'customer-to-provider':
        return 'c2p'
    elif r == 'provider-to-customer':
        return 'p2c'
    elif r == 'peer-to-peer':
        return 'p2p'
    elif r == 'sibling-to-sibling':
        return 's2s'
    else:
        return r

def addedges(G):
    global edgeset,graphset
    graphset.append(G)


def motifcompiler(G):
    global motif
    nodes = list(G.nodes())
    mapping = dict()
    i=0
    newG = nx.DiGraph()
    for x in nodes:
        mapping.update({nodes[i]:"A"+str(i)})
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
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
purpose='newmotif'
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
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = 'customer-to-provider')
        else:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inverselink(x[2]))
            
    l = (file.readline()).strip()
print("working...")

nodes = list(g.nodes())
em = iso.categorical_edge_match('relationship', '')
motif2 = dict()

        
edgeset = list()
graphset = list()
motif = set()
count = 0
nodes=list(g.nodes())
deleting = list()
deletingFile = open('/home/asemwal/raw_data/2018/proc/deleting','r')
l = (deletingFile.readline()).strip()
while l != '':
    nodes.remove(str(l))    
    l = (deletingFile.readline()).strip()

deletingFile.close()
deletingFile = open('/home/asemwal/raw_data/2018/proc/deleting','a')
    
print("Begin: {}".format(time.time()))  
for n in nodes[0:5]:
    x = list(g.neighbors(n))
    comb = list(itr.combinations(x , 4))
    for i in comb:
        G = nx.subgraph(g, i)
        if nx.is_connected(nx.Graph(G)) == True:
            graphset.append(G)
    for x in graphset:
        q=motifcompiler(x)
        matched = False
        key = x.__hash__()
        for y in motif:
            if nx.is_isomorphic(q,y, edge_match=em) == False:
                pass
            else:
                matched = True
                key = y.__hash__()
                break;
        if matched == False:
            motif.add(x)
            motif2.update({key:{'count':1, 'graph':x}})
        else:
            motif2[key]['count'] +=1
        
    del comb, x
    print(n)
    deletingFile.write(str(n)+"\n")
deletingFile.close()
print("End: {}".format(time.time()))


print("Begin Motif Explorer: {}".format(time.time()))  
"""
for x in graphset:
    q=motifcompiler(x)
    matched = False
    key = x.__hash__()
    for y in motif:
        if nx.is_isomorphic(q,y, edge_match=em) == False:
            pass
        else:
            matched = True
            key = y.__hash__()
            break;
    if matched == False:
        motif.add(x)
        motif2.update({key:{'count':1, 'graph':x}})
    else:
        motif2[key]['count'] +=1
        
"""       
motifs = list(motif)
print("End Motif explorer: {}".format(time.time()))  
out = open(location+year+proc+purpose+str(int(time.time())), 'w')
for k in motif2.keys():
    l='MOTIF+++++\n'
    l+= "count:\t"+ str(motif2[k]['count']) +"\n"
    c = motif2[k]['graph']
    edges = list(c.edges())
    for e in edges:
        l+= e[0] +"-->" + c.get_edge_data(e[0],e[1])['relationship'] + "-->" + e[1] + "\n"
    l+='MOTIF+++++\n'
    out.write(l)
    out.flush()
out.write("counter: " + str(len(motif2.keys())) + " motifs\n")
out.flush()
out.close()
