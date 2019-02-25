# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 13:06:46 2018

@author: asemwal
"""

import numpy as np
import random as rand
import networkx as nx
import time

def phase2(No = 0 , Nc = 0 , Lc = 0, X = 0):
    global g, D, Ngt0
    custSet = set()
    R = Lc - Nc
    print("R="+str(R)+"   Nc:"+str(Nc)+"   No:"+str(No)+"   Lc:"+str(Lc))
    i = No
    while i < No+Nc:
        p = prefProb(Ngt0)
        p_keys= list(p.keys())
        p_keys.sort()
        prob = []
        s=0
        for j in range(0, len(p_keys)):
            prob.append(p[p_keys[j]])
            s+=p[p_keys[j]]
        for j in range(0, len(p_keys)):
            prob[j]/=s                
        link = list(np.random.choice(p_keys, 1, p=prob, replace = False))
        print "edge---> " + str(link[0]) +":"+str(i)
        g.add_edge(link[0],i,relationship = 'provider-to-customer')
        g.add_edge(i, link[0],relationship = 'customer-to-provider')
        D[link[0]]-=1
        if D[link[0]] <=0:
            Ngt0.remove(link[0])
        if g.degree(i) < X:
            custSet.add(i)
        i+=1
    print 'here'
    
    for i in range(0,R):
        custprob = [1.0]*len(custSet)
        for j in range(0,len(custprob)):
            custprob[j]/=len(custSet)
        p = prefProb(Ngt0)
        prob = []
        plist = list(p.keys())
        s=0
        plist.sort()
        for j in range(0,len(plist)):
            prob.append(p[plist[j]])
            s+=p_keys[i]
    
        for i in range(0, len(p_keys)):
            prob[i] = prob[i]/s
        while True == True:
            cust = list(np.random.choice(list(custSet), 1, p=custprob, replace = False))
            prov = list(np.random.choice(plist, 1, p=prob, replace = False))
        #print "edge---> " + str(prov[0]) +":"+str(cust[0])
            edges = list(g.edges(cust[0]))
            if (cust,prov) not in edges:
                break;
        if i%100 ==  0:
           print i, len(Ngt0)
        g.add_edge(prov[0], cust[0], relationship= 'provider-to-customer')
        g.add_edge(cust[0], prov[0], relationship= 'customer-to-provider')
        D[prov[0]] -=1
        if g.degree(cust[0]) >= X:
            custSet.remove(cust[0])
        if D[prov[0]] <= 0:
            Ngt0.remove(prov[0])
        
        

def AStop(No = 6276 , Nc = 56499 , alpha = -1.8686217868, c = 6000 , beta = 6000): 
    global D ,g, Ngt0
    D = dict()
    L  = 0
    for i in range(0,No):
        x =  rand.randint(2,No-1)
        D[i] = int( c*(x**-alpha))
        L += D[i]
    print L
    Lc = int(L*0.33*0.005)
    Lo = int(L*0.67*0.005)
    Lc = 123606
    Lo = 568054
    g = nx.DiGraph()
    phase1(Lo)
    phase2(No,Nc,Lc,6)
    printgraph(No=No, Nc=Nc,Lo=Lo,Lc=Lc, alpha=alpha, beta=beta, X=beta)
    
def printgraph(No = 0 , Nc= 0 , Lo = 0 , Lc=0, alpha = 0 , beta = 0,X =4):
    global g,D
    stamp = str(g.number_of_nodes())+ "_" + str(int(time.time()))
    dir = '/home/asemwal/raw_data/experiments/AStop/'
    out = open(dir+'AStop_'+   stamp ,'w')
    core = list()
    for i in D.keys():
        core.append(str(i))
    edges = list(g.edges())
    out.write("#Graph Properties\n")
    out.write("#Edges :" + str(g.number_of_edges())+"  \tNodes : " + str(g.number_of_nodes()) +"\n")
    out.write("#Core: "+ str(", ".join(core )) +"\n")
    out.write("#Lo: "+ str(Lo) +"#No: "+ str(No) +"\n")
    out.write("#Lc: "+ str(Lc) +"#Nc: "+ str(Nc) +"\n")
    out.write("#aplha: "+ str(alpha) +"#beta: "+ str(beta) +"\n")
    out.write("#X: "+ str(X)  +"\n")
    out.write("#\n")
    for e in edges:
        l = list()
        l.append(str(e[0]))
        l.append(str(e[1]))
        l.append(g.get_edge_data(e[0] , e[1])['relationship'])
        out.write("|".join(l)+"\n")

    out.close()
    
 
        
def prefProb(nodeset = set()):
    global g
    d= dict(g.degree())
    p = dict()
    sum = 0
    for i in d.keys():
        sum+= d[i]
    prob = 0.0
    if sum == 0:
        sum = len(d.keys())
    for i in nodeset:
        p[i] = d[i]/sum
        prob += p[i]
    if prob == 0:
        for i in p.keys():
            p[i]= 1.0
    return p
    
def phase1( Lo = 0):
    global D,g, Ngt0   
    g.add_nodes_from(list(D.keys()))
    Ngt0 = D.keys()
    i=0
    while i  < Lo:
       addlink( )
       i+=1
       if i%100 == 0:
           print i, len(Ngt0)
    return g
    
    
    
def addlink():
    global g, Ngt0,D
    p = prefProb(Ngt0)
    prob = []
    p_keys = list(p.keys())
    p_keys.sort()
    s = 0
    for i in range(0, len(p_keys)):
        prob.append(p[p_keys[i]])
        s+=p[p_keys[i]]
    
    for i in range(0, len(p_keys)):
        prob[i] = prob[i]/s
    while True == True:
        link = list(np.random.choice(p_keys, 2, p=prob, replace = False))
        link2 = (link[0],link[1])   
        edges = list(g.edges(link[0]))
        if link2 not in edges:
            break
    g.add_edge(link[0],link[1],relationship = 'peer-to-peer')
    g.add_edge(link[0],link[1],relationship = 'peer-to-peer')
    #print "edge---> " + str(link[0]) +":"+str(link[1])
    D[link[0]]-=1
    D[link[1]]-=1
    if D[link[0]] == 0:
        Ngt0.remove(link[0])
    if D[link[1]] == 0:
        Ngt0.remove(link[1])
    return Ngt0    
    
g=AStop()
