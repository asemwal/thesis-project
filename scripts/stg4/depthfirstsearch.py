# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 19:23:54 2018

@author: asemwal
"""

import networkx as nx
import time 
def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r
        
def dfs(G,v):
    global visited, customer
    #visited = set()
    if v in visited:
        return customer[v]
    visit = list(G.neighbors(v))
    c=set()
    visiting = v
    visited.insert(0,v)
    #print("{} {}".format(v,visited))
    print(v)
    if len(visit) == 0:
        customer[v] = set()
    cust = set()
    while len(visit) > 0:
        q = visit.pop()
        if G.get_edge_data(visiting,q)['relationship'] =='provider-to-customer':
            cust.add(q)
            
            cust = cust.union(dfs(G,q))
            #print("lala::: {} {}".format(v,cust))
        
    customer[v] = cust
    #print("cust:::{} {}".format(v,cust))
    return cust
    
    
        
        
        
visited = list()
cust = set()
customer = dict()
g = nx.DiGraph()
f='links'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
purpose='neighbour_cliques'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'

print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3):
        if x[2] == 'customer-to-provider' or inverselink(x[2]) == 'customer-to-provider':
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inverselink(x[2]))
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])
        else:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = inverselink(x[2]))
    l = (file.readline()).strip()
print("working...")

nodes = list(g.nodes())
for n in nodes:
    customer.update({n:set()})
for n in nodes:
    dfs(g,n)
    
file = open('/home/asemwal/raw_data/2018/old_proc/relationships','r')
purpose='neighbour_cliques'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'



print(time.time())
#file = open(location+year+'proc/'+f, 'r')
g = nx.DiGraph()
l = (file.readline()).strip()
weight = {'provider-to-customer':1,'sibling-to-sibling':1,'peer-to-peer':2,'customer-to-provider':4}
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2] , weight = weight[x[2]])
        g.add_edge(str(x[1]), str(x[0]) ,  relationship = inverselink(x[2]), weight = weight[inverselink(x[2])])
    l = (file.readline()).strip()
print("working...")


   
paths = dict()
def customerpaths(graph = None ):
    global paths,customer
    if graph == None:
        return
    G = nx.DiGraph(graph)
    nodes = list(G.nodes())
    for i in nodes:
        paths.update({i:dict()})
    for i in nodes:
        sg_nodes = list(customer[i])
        sg_nodes.append(i)
        graph = G.subgraph(sg_nodes)
        for j in customer[i]:
            temp  = list(nx.shortest_path(graph,i,j))
            print("path from {} to {} is {}".format(i,j," ".join(temp)))
            paths[i][j] = " ".join(temp)
            temp.reverse()
            paths[j][i] = " ".join(temp)

  
def shortestpath(graph = None):
    if graph == None:
        return
    G = nx.DiGraph(graph)
    count  = 0 
    nodes = list(G.nodes())
    for i in nodes:
        for j in nodes:
            if i != j :
                if i in paths.keys():
                    if j  not in paths[i].keys():
                        count+=1
    print count            
            
def shortestpaths(graph = None , src  = None):
    global paths, customer
    if graph == None:
        return
    G = nx.DiGraph(graph)
    paths.update({src:dict()})
    nodes = list(G.nodes())
    nodes.remove(src)
    for i in nodes:
        print(i)
        g = nx.DiGraph(G)
        found = False
        asn = src
        sg_nodes = list()
        sg_nodes.append(src)
        while found == False:
            peer = False
            if i in customer[asn]:
                sg_nodes += list(customer[asn]) 
                g = g.subgraph(n)
                paths[src][i] = nx.shortest_path(g,src,i)
                found = True
            else:
                neighbors  = list(g.neighbors(asn))
                for n in neighbors:
                    if g.get_edge_data(asn,n)['relationship'] == 'peer-to-peer':
                        if i == n:
                            sg_nodes.append(n)
                            paths[src][i] = nx.shortest_path(g,src,i)
                            found = True
                            peer = True
                            break
                        elif i in customer[n]:
                            asn = i
                            sg_nodes += [asn]
                            peer = True
                            break
                for n in neighbors:
                    if peer == True:
                        break
                    try:
                        if g.get_edge_data(asn,n)['relationship'] == 'customer-to-provider':
                            if i == n:
                                sg_nodes.append(n)
                                paths[src][i] = nx.shortest_path(g,src,i)
                                found = True
                                break
                            elif i in customer[n]:
                                asn = i
                                sg_nodes += [asn]
                                break
                            else:
                                asn = n
                                break
                    except TypeError as e:
                        print("typeerr")
                        print(asn)
                        print(n)
    
    
"""
out = open(file.name+'_cust','w')
for c in customer.keys():
    out.write(c+"|"+ str(len(customer[c]))+"|" + ", ".join(list(customer[c])) +"\n")
    out.flush()
out.close()
"""