# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 21:51:28 2018

@author: asemwal
"""

import math
import time
import networkx as nx
import utils
import operator
import numpy as np

def randomlink(length  = None,  g = None):
    monitor = set(randombased( length , list(g.nodes())))
    return monitor;


def degreelink(monitor = None, links = None, timestamp = None , monsetlen = None, g = None):
    visible_links = set()
    vp =[]
    monitor_len = dict(g.degree())
    copy_monitor = dict(monitor)
    visible_prob = dict()
    for i in monitor.keys():
        monitor_len.update({i:len(monitor[i])})
        visible_prob.update({i:len(monitor[i])/float(len(links))})

    threshold = 1
    vp_copy =set()
    distribution = dict()
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
    while len(sorted_x ) > 0:
        r = sorted_x.pop(-1)
        if r[1] > threshold:
            vp.append(r[0])
            visible_links = visible_links.union(copy_monitor[r[0]])
            if len(vp) == monsetlen:
                vp_copy = vp_copy.union(visible_links)
            number = float(len(visible_links))*100.0/len(links)
            distribution.update({len(vp): number})
        copy_monitor.pop(r[0])
        monitor_len.pop(r[0])
        if len(visible_links) == len(links):
            break;
        sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

    line="visible links:" +str(len(visible_links))+"\ttotal_links: " +str(len(links))+"\n"
    line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monitor))+"\n"
    line+= "Threshold :"+ str(threshold) +'\n'
    #print(time.time())
    while(True):
        try:
            x = vp.pop(0)
            line += str(x) +"|"+ str(visible_prob[x]) +"\n"
#            line += str(x) +"|"+ str(0) +"\n"
        except KeyError as e:
            break;        
        except IndexError as e:
            break;

    out = open('/home/asemwal/raw_data/experiments/graphs/degreemonset_'+timestamp, 'w')
    

    out.write(line)
    out.flush()
    out.close()
    return vp_copy, distribution




def greedylink2(monitor = None, links = None, timestamp = None , monsetlen = None):
    visible_links = set()
    vp =[]
    monitor_len = dict()
    copy_monitor = dict(monitor)
    visible_prob = dict()
    for i in monitor.keys():
        for j in monitor.keys():
            if i!=j:
                monitor_len.update({i+"_"+j:len(monitor[i].union(monitor[j]))})
                visible_prob.update({i:len((monitor[i].union(monitor[j])))/float(len(links))})

    threshold = 1
    vp_copy =set()
    distribution = dict()
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
    while len(sorted_x ) > 0:
        r = sorted_x.pop(-1)
        if r[1] > threshold:
            vp.append(r[0].split("_")[0])
            vp.append(r[0].split("_")[1])
            visible_links = visible_links.union(copy_monitor[r[0].split("_")[0]])
            visible_links = visible_links.union(copy_monitor[r[0].split("_")[1]])
            if len(vp) == monsetlen:
                vp_copy = vp_copy.union(visible_links)
            number = float(len(visible_links))*100.0/len(links)
            distribution.update({len(vp): number})
        copy_monitor.pop(r[0].split("_")[0])
        copy_monitor.pop(r[0].split("_")[1])
        if len(visible_links) == len(links):
            break;
        for i in copy_monitor.keys():
            copy_monitor[i] = copy_monitor[i].difference(visible_links)
        monitor_len = dict()
        for i in copy_monitor.keys():
            for j in copy_monitor.keys():
                monitor_len.update({i+"_"+j:len(copy_monitor[i].union(copy_monitor[j]))})
        sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

    line="visible links:" +str(len(visible_links))+"\ttotal_links: " +str(len(links))+"\n"
    line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monitor))+"\n"
    line+= "Threshold :"+ str(threshold) +'\n'
    #print(time.time())
    while(True):
        try:
            x = vp.pop(0)
            line += str(x) +"|"+ str(visible_prob[x]) +"\n"
#            line += str(x) +"|"+ str(0) +"\n"
        except KeyError as e:
            break;        
        except IndexError as e:
            break;

    out = open('/home/asemwal/raw_data/experiments/graphs/greedymonset_'+timestamp, 'w')
    

    out.write(line)
    out.flush()
    out.close()
    return len(vp_copy), distribution



def greedylink(monitor = None, links = None, timestamp = None , monsetlen = None):
    visible_links = set()
    vp =[]
    monitor_len = dict()
    copy_monitor = dict(monitor)
    visible_prob = dict()
    for i in monitor.keys():
        monitor_len.update({i:len(monitor[i])})
        visible_prob.update({i:len(monitor[i])/float(len(links))})

    threshold = 1
    vp_copy =set()
    distribution = dict()
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
    while len(sorted_x ) > 0:
        r = sorted_x.pop(-1)
        if r[1] > threshold:
            vp.append(r[0])
            visible_links = visible_links.union(copy_monitor[r[0]])
            if len(vp) == monsetlen:
                vp_copy = vp_copy.union(visible_links)
            number = float(len(visible_links))*100.0/len(links)
            distribution.update({len(vp): number})
        copy_monitor.pop(r[0])
        monitor_len.pop(r[0])
        if len(visible_links) == len(links):
            break;
        for i in copy_monitor.keys():
            copy_monitor[i] = copy_monitor[i].difference(visible_links)
            monitor_len[i] = len(copy_monitor[i])
        sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

    line="visible links:" +str(len(visible_links))+"\ttotal_links: " +str(len(links))+"\n"
    line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monitor))+"\n"
    line+= "Threshold :"+ str(threshold) +'\n'
    #print(time.time())
    while(True):
        try:
            x = vp.pop(0)
            line += str(x) +"|"+ str(visible_prob[x]) +"\n"
#            line += str(x) +"|"+ str(0) +"\n"
        except KeyError as e:
            break;        
        except IndexError as e:
            break;

    out = open('/home/asemwal/raw_data/experiments/graphs/greedymonset_'+timestamp, 'w')
    

    out.write(line)
    out.flush()
    out.close()
    return len(vp_copy), distribution



def independentsetbased(graphFile = None,  visibility = 0):
    global c
    print("Initializing graph... process beginning at {}".format(time.time()))
    g = nx.DiGraph(generategraph( graphFile, visibility)) 

    G= nx.DiGraph(g)
    print("Initializing graph... process end at {}".format(time.time()))

    monitors = set(getPartialMonitorSet(g,G))
    safer = set(monitors)
    nodedegree_main_graph = dict(degreemap(G))
    #monitors  = set(elimination(g, monitors , 'c2p'))
    monitors  = set(elimination(g, monitors , 'p2p'))
    monitors  = set(elimination(g, monitors , 's2s'))

    safe_monitors_disc = monitors.copy()
    b = nx.DiGraph(g.subgraph(list(monitors)))
    nodedegree = dict(degreemap(b))

    final_monitors = set()
    #for k in nodedegree.keys():
    #    if nodedegree[k]['p2p'] + nodedegree[k]['p2c']+ nodedegree[k]['c2p'] + nodedegree[k]['s2s'] == 0:
    #        final_monitors.add(k)   
    print monitors
    #print final_monitors
    #monitors.difference_update(final_monitors)
    final_monitors = final_monitors.union(monitors)
    return g, final_monitors

def randombased(length = None, nodes = None):
    prob = [1.0] * len(nodes)
    prob /= np.sum(prob)
    monset =  np.random.choice(nodes, length, p=prob, replace = False)
    return list(monset)

def degreebased(length = None , degree = None):
    monset = set()    
    temp = sorted(degree.items(), key=operator.itemgetter(1)) 
    while len(monset ) < length:
        monset.add(temp.pop(-1)[0])
    return monset

def generategraph(f = None, n = 0, flip = False):
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
            #g.add_edge(x[1], x[0] , relationship = inverselink(x[2]))
            
        
        l = str(file.readline()).strip()
    #print(g.degree())
    if n > 0:
        G = nx.Graph(g)
        edges  = list(G.edges())
        length = int(n * len(edges))
        print length
        prob = [1.0] * len(edges)
        prob /= np.sum(prob)
        print len(prob)
        print len(edges)
        edgeset =  np.random.choice(list(range(0,len(edges))), length, p=prob, replace = False)
        for i in edgeset:   
            if flip == False:
                g.remove_edge(edges[i][0],edges[i][1])
                g.remove_edge(edges[i][1],edges[i][0])
            else:
                r = g.get_edge_data(edges[i][0],edges[i][1])['relationship']
                r = fliplink(r)
                g.get_edge_data(edges[i][0],edges[i][1])['relationship'] = r
                g.get_edge_data(edges[i][1],edges[i][0])['relationship'] = inverselink(r)
            
        d = dict(nx.degree(g))
        for i in d.keys():
            if d[i] <1:
                g.remove_node(i)
                print(i)
    return g
    
def fliplink(r):
    if r == 'customer-to-provider':
        return 'peer-to-peer'
    elif r == 'provider-to-customer':
        return 'peer-to-peer'
    elif r == 'sibling-to-sibling':
        return 'peer-to-peer'
    else:
        return 'provider-to-customer'
        


def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r
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
            #g.add_edge(x[1], x[0] , relationship = inverselink( (x[2])))
            
        
        l = str(file.readline()).strip()
    return g

def getPartialMonitorSet(g,G):
    #g = Main Graph
    #G - Copy of AS Graph
    
    nodedegree= dict(degreemap(G))
    monitors = set()
    customers = set()

    for k in nodedegree.keys():
        if nodedegree[k]['p2c'] == 0 :
            customers.add(k)
    print("{} ASes without customers found at {}".format(len(customers), time.time()))
    while len(customers) > 0:
        print("{} ASes without customers found at {} in recursive loop".format(len(customers), time.time()))
        providers = set()
        for k in customers:
            providers = providers.union(getproviders(g,k,monitors))
        
        customers = set()
        monitors = monitors.union(providers)
        customers = customers.union(providers)
        #for p in providers:
        #    customers = customers.union(getproviders(g,p,monitors))

    print("{} Monitors found at {}".format( len(monitors), time.time()))
    return monitors
 
def elimination(g, monitors , key):
    print("{} elimination stage".format(key))
    #return monitors
    b= nx.DiGraph(g.subgraph(list(monitors)))
    nodedegree = dict(degreemap(b))
    r2r = dict()
    for n in nodedegree.keys():
        r2r[n] = nodedegree[n][key]
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))        
    count =0
    for i in range(0,len(sorted_r2r)):
        if sorted_r2r[i][1] > 0:
            count += 1
    for i  in range(1,count+1):
        if sorted_r2r[i*-1][0] in monitors:
            print("node : {} peers : {}".format(sorted_r2r[i*-1][0] , sorted_r2r[i*-1][1]))
            monitors.difference_update(getneighbours(b,sorted_r2r[i*-1][0], key))
    
    print("{} Monitors found after peer elimination, at {}".format( len(monitors), time.time()))
    return monitors

def elimination2(g, monitors , key):
    print("{} elimination stage".format(key))
    #return monitors
    b= nx.DiGraph(g.subgraph(list(monitors)))
    edges = list(b.edges())
    for i in edges:
        if c[b.get_edge_data(i[0],i[1])['relationship']] == key:
            pass
        else:
            b.remove_edge(i[0], i[1])
    newset = set()            
    nodedegree = dict(degreemap(b))
    r2r = dict()
    for n in nodedegree.keys():
        if nodedegree[n][key] > 0:
            r2r[n] = nodedegree[n][key]
        else:
            newset.add(n)
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))     
    while len(sorted_r2r ) > 0 :
        print(len(sorted_r2r))
        element = sorted_r2r.pop(-1)
        edges = list(b.edges(element[0] , 'relationship'))
        for i in edges:
            if c[i[2]] == key:
                b.remove_edge(i[0],i[1])
                b.remove_edge(i[1],i[0])
        newset.add(element[0])
        nodedegree = dict(degreemap(b))
        r2r = dict()
        for n in nodedegree.keys():
            if nodedegree[n][key] > 0:
                r2r[n] = nodedegree[n][key]
        sorted_r2r = sorted(r2r.items() , key = operator.itemgetter(1))

    print("{} Monitors found after peer elimination, at {}".format( len(monitors), time.time()))
    return newset



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
    
        


def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def getneighbours(g, node, key):
    global c
    neighbour = set()
    edgelist = list(g.edges(node))
    for i in edgelist:
        if c[g.get_edge_data(i[0],i[1])['relationship']] == key:
            neighbour.add(i[1])
    return neighbour

def getpeers(g, node):
    global c
    peer = set()
    edgelist = list(g.edges(node))
    for i in edgelist:
        if c[g.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
            peer.add(i[1])
    return peer
    
def getproviders(g, node, monitors):
    global c
    providers = set()
    edgelist = list(g.edges(node))
    for i in edgelist:
        if c[g.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
            if i[1] not in monitors:
                providers.add(i[1])
    return providers

def getcustomers(g, node):
    global c
    customers = set()
    edgelist = list(g.edges(node))
    for i in range(0,len(edgelist)):
        if c[g.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship']] == 'p2c':
            customers.add(edgelist[i][1])
    return customers
    
def getsiblings(g, node):
    global c
    siblings = set()
    edgelist = list(g.edges(node))
    for i in edgelist:
        if c[g.get_edge_data(i[0],i[1])['relationship']] == 's2s':
            siblings.add(i[1])
    return siblings

c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}

def monitorselection(f = None, timestamp = None, visibility = 1):
    g, is_monset = independentsetbased(f, 1- visibility)
    is_monset = newmonitorselection(g , f)
    d_monset = degreebased(len(is_monset) , dict(nx.Graph(g).degree()))
    r_monset = randombased(len(is_monset) , list(g.nodes()))
    r30_monset = randombased(int(len(g.nodes())*0.3) , list(g.nodes()))
    out = open("/".join(f.split("/")[0:-1]) + "/monitors_"+timestamp,'w')
    out.write("is_monset:"+",".join(list(is_monset))+"\n")
    out.write("d_monset:"+",".join(list(d_monset))+"\n")
    out.write("r_monset:"+",".join(list(r_monset))+"\n")
    out.write("r30_monset:"+",".join(list(r30_monset))+"\n")
    out.close()
    return is_monset, d_monset , r_monset

def newmonitorselection( g = None , graphFile = ''):
    tier_1 = list(gettier1ASes(graphFile))            
    monitors = set()
    customers = set()
    for i in tier_1:
        monitors.add(i.strip())
        customers = customers.union(getcustomers(g , i.strip()))
        print("customers found {}".format(len(customers)))
        
    while len(customers) > 0:
        next_cust = set()
        for i in customers:
            peers = getpeers(g , i)
            providers = getneighbours(g, i , 'c2p' )
            if len(peers) > 0 :
                print("peers found")
                monitors.add(i)
            elif len(providers) >1:
                for p1 in providers:
                    s1 = getneighbours(g , p1 , 'c2p')
                    for p2 in providers:
                        if p1 != p2:
                            s2 = getneighbours(g , p2 , 'c2p')
                            if len(s1.intersection(s2)) > 0 :
                                monitors = monitors.union(s1.intersection(s2))
                #print("providers found")
                #monitors = monitors.union(providers)
            next_cust = next_cust.union(getcustomers(g , i))
        customers = set()
        customers = customers.union(next_cust)
    if True == False:
        monitors = set(elimination(g ,monitors, 'p2p'))
    else:
        monitors = set(elimination2(g ,monitors, 'p2p'))
    
    return monitors
    

def degreedistribution(g=None):
    d = dict()
    nodedegree=dict(g.degree())
    for i in nodedegree.keys():
        try:
            d[nodedegree[i]]+=1;
        except KeyError :
            d.update({nodedegree[i]:1})
    return d
    
def gettier1ASes(graphFile = None):
    tier_1 = list()
    infile = open(graphFile)
    l = str(infile.readline()).strip()
    while True == True:
        if l.find("Tier1") > -1:
            tier_1 = l.split(":")[1].split(",")
            break
        l = str(infile.readline()).strip()
    infile.close()
    return tier_1
    
