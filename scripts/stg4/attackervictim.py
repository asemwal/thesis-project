# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 12:43:16 2018

@author: asemwal
"""
import utils
import networkx as nx
import time
import random as rand
import networkx.algorithms.isomorphism as iso


def attackervictimset(f = '/home/asemwal/raw_data/evam_list'):
    attacker = set()
    victim = set()
    attacker_d = dict()
    victim_d= dict()
    infile = open(f ,'r')
    l = str(infile.readline()).strip()
    while l != '':
        data = l.split("|")
        attacker.add(data[2])
        victim.add(data[1])
        try:
            attacker_d[data[2]]+=1
        except KeyError:            
            attacker_d.update({data[2]:1})
        try:
            victim_d[data[1]]+=1
        except KeyError:            
            victim_d.update({data[1]:1})
        l = str(infile.readline()).strip()
    infile.close()
    return attacker,victim, attacker_d, victim_d

def generategraph(f = None):
    print f
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
    #print(g.degree())
    return g


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
    for x in range(0,len(nodes)):
        mapping.update({nodes[x]:str(x)})
    edges = list(G.edges())
    
    for e in edges:
        try:
            newG.add_edge(mapping[e[0]], mapping[e[1]], relationship=G.get_edge_data(e[0],e[1])['relationship'])   
            newG.add_edge(mapping[e[1]], mapping[e[0]], relationship=G.get_edge_data(e[1],e[0])['relationship'])   
        except KeyError:
            print(e)
    return newG
    


def begin(attacker = None,  victim = None, g = None):
    motif = set()
    graphset = set()
    for i in attacker:
        nodes = list()
        if i in list(g.nodes()):
            nodes.append(i)
            nodes += list(g.neighbors(i))
            graphset.add(g.subgraph(nodes))
            
    print("End: {}".format(time.time()))
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
            motif.add(q)        
    motifs = list(motif)
    return motifs
    
def stg():
    g = generategraph('/home/asemwal/raw_data/2018/proc/relationships')
    attacker,victim, attacker_d, victim_d = attackervictimset()
    x = begin(attacker , victim, g)
    out = open('/home/asemwal/raw_data/2018/proc/relationships_motifbuilder', 'w')
    for c in x:
        l='MOTIF+++++\n'
        edges = list(c.edges())
        for e in edges:
            l+= e[0] +"-->" + c.get_edge_data(e[0],e[1])['relationship'] + "-->" + e[1] + "\n"
        l+='MOTIF+++++\n'
        out.write(l)
        out.flush()
    
    out.close()
    return x