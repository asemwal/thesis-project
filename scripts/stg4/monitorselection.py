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

def generategraph(f = None, n = 0, flip = False,key='p2c'):
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
    c = {'p2p':'peer-to-peer','p2c':'provider-to-customer'}
    if n > 0:
        edgesall  = list(g.edges())
        edges = []
        for i in edgesall:
            if g.get_edge_data(i[0],i[1])['relationship'] == c[key]:
                edges.append(i)
        edgesall = list(edges)
        print len(edges), 'first'
        if key == 'p2p':
            edges = list()
            for i in edgesall:
                if (i[1],i[0]) not in edges:
                    edges.append(i)
        length = int(n * len(edges))
        print len(edges), 'second'
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
    
    
def generategraph3(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
#    c = {0: 'peer-to-peer', -1: 'provider-to-customer'}
    g = nx.DiGraph()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            #g.add_edge(x[0].split("_")[1], x[1].split("_")[1] , relationship =  (x[2]))
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

def elimination3(g, monitors , key, moncustcone = dict()):
    print("{} elimination stage".format(key))
    #return monitors
    maindegreeMap = dict(degreemap(g)) 
        
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
    ranks = dict()
    rank = 1
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))     
    while len(sorted_r2r ) > 0 :
        print(len(sorted_r2r))
        print "sorted r2r"
        element1 = sorted_r2r.pop(-1)
        element2 = sorted_r2r.pop(-1)
        element = ()
        removeedges = set(b.edges(element1[0]))
        print removeedges
        ranks[rank] = set(element1[0])
        while element1[1] == element2[1]:
            element1 = element2
            removeedges.intersection_update(set(b.edges(element1[0])))
            ranks[rank].add(element1[0])
            if len(sorted_r2r)>0:
                element2 = sorted_r2r.pop(-1)
            else:
                break
                
        for i in removeedges:
            #if c[i[2]] == key:
                b.remove_edge(i[0],i[1])
                b.remove_edge(i[1],i[0])
        if len(removeedges) == 0:
            print "removing nodes"
            b.remove_nodes_from(list(ranks[rank]))
        nodedegree = dict(degreemap(b))
        rank+=1
        r2r = dict()
        for n in nodedegree.keys():
            if nodedegree[n][key] > 0:
                r2r[n] = nodedegree[n][key]
        sorted_r2r = sorted(r2r.items() , key = operator.itemgetter(1))

    print("{} Monitors found after peer elimination, at {}".format( len(newset), time.time()))
    newset = set()
    rankkeys = list(ranks.keys())
    rankkeys.sort()
    ranklen = dict()
    for i in rankkeys:
        ranklen[i] = {}
        ranklen[i]['len']=len(ranks[i])
        ranklen[i]['sel']=0
    observed = set()
    for i in rankkeys:
        if ranklen[i]['len']==1:
            newset.add(i)
            observed = observed.union(moncustcone[i])
    for i in newset:
        rankkeys.remove(i)
    ranklen = dict()
    for i in rankkeys:
        ranklen[i] = {}
        ranklen[i]['len']=len(ranks[i])
        ranklen[i]['sel']=0
    for i in ranklen.keys():
        m = ranks[i].pop()
        ob = moncustcone[m]
        while len(ranks[i])!=0:
            print "here"
            m2 =  ranks[i].pop()
            ob2 = moncustcone[m]
            edges = list(g.edges())
            if (m,m2) in edges:
                if len(ob) < len(ob2):
                    ob=ob2
                    m=m2
                newset.add(m)
            else:
                newset.add(m)
                newset.add(m1)
    return newset

def longtermshorttermelimination(g, monitors,key, decisions = dict()  ):
    print("entering {} elimination stage with {} monitors".format(key, len(monitors)))
    #return monitors
    maindegreeMap = dict(degreemap(g)) 
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
    itr=1
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))
    element1 = sorted_r2r.pop(-1) 
    #x=element1[0]    
    while len(sorted_r2r ) > 0 :
        element2 = sorted_r2r.pop(-1)
        if itr not in decisions.keys():
            print "breaking"
            break
        if element1[0] not in decisions[itr]['left'] and \
            element1[0] not in decisions[itr]['decided']:
                decisions[itr]['left'].append(element1[0])
        if decisions[itr]['status'] == 'U':
            decisions[itr]['status'] = 'S'
        while element2[1] == element1[1] and decisions[itr]['status'] =='S':
            element1 = element2
            if element1[0] not in decisions[itr]['left'] and \
            element1[0] not in decisions[itr]['decided']:
                    decisions[itr]['left'].append(element1[0])
        
            if len(sorted_r2r)>0:
                element2 = sorted_r2r.pop(-1)
        if decisions[itr]['status'] == 'S' and decisions[itr-1]['status'] == 'S':
            decisions[itr-1]['status'] = 'L'
        if len(decisions[itr]['left']) >0:
            x=decisions[itr]['left'].pop()
            print x
            #print decisions
            decisions[itr]['decided'].append(x)
        else:
            x = element1[0]
        print itr,x, decisions
        print list(b.edges(x))
        edges = list(b.edges(x , 'relationship'))
        print edges
        for i in edges:
            if c[i[2]] == key:
                print "removing edges"
                b.remove_edge(i[0],i[1])
                b.remove_edge(i[1],i[0])
        newset.add(x)
        nodedegree = dict(degreemap(b))
        r2r = dict()
        for n in nodedegree.keys():
            if nodedegree[n][key] > 0:
                r2r[n] = nodedegree[n][key]
        sorted_r2r = sorted(r2r.items() , key = operator.itemgetter(1))
        itr+=1
        
        
    return newset,decisions
     



def elimination2(g, monitors , key ):
    print("{} elimination stage".format(key))
    #return monitors
    maindegreeMap = dict(degreemap(g)) 
        
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
        element1 = sorted_r2r.pop(-1)
        element2 = sorted_r2r.pop(-1)
        element = ()
        if element1[1] == element2[1]:
            if maindegreeMap[element1[0]]['c2p'] > maindegreeMap[element2[0]]['c2p']:
                element = element1
            elif maindegreeMap[element1[0]]['c2p'] < maindegreeMap[element2[0]]['c2p']:
                element = element2
            elif maindegreeMap[element1[0]]['p2c'] > maindegreeMap[element2[0]]['p2c']:
                element = element1
            elif maindegreeMap[element1[0]]['p2c'] < maindegreeMap[element2[0]]['p2c']:
                element = element2
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element1
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element2
            elif element1[0] < element2[0]:
                element = element1
            else:
                element = element2
        else:
            element = element1
                
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

    print("{} Monitors found after peer elimination, at {}".format( len(newset), time.time()))
    return newset


def elimination4(g, monitors , key ):
    print("{} elimination stage".format(key))
    #return monitors
    newset = set()
    if len(monitors) > 0:
        print "subgraph created"
        b= nx.DiGraph(g.subgraph(list(monitors)))
    else:
        b= nx.DiGraph(g)
    edges = list(b.edges())
    maindegreeMap = dict(degreemap(b)) 
    nodedegree = dict(degreemap(b))
    r2r = dict()
    for n in nodedegree.keys():
        if nodedegree[n][key] > 0:
            r2r[n] = nodedegree[n][key]
        else:
            pass
            #newset.add(n)
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))     
    while len(sorted_r2r ) > 0 :
        print "size of sorted r2r is:"
        print(len(sorted_r2r))
        element1 = sorted_r2r.pop(-1)
        element = element1
        element2 = (-1,-1)
        if len(sorted_r2r) > 0:
           element2=sorted_r2r.pop(-1)
        while element2[1] == element1[1]:
            if maindegreeMap[element1[0]]['c2p'] > maindegreeMap[element2[0]]['c2p']:
                element = element1
            elif maindegreeMap[element1[0]]['c2p'] < maindegreeMap[element2[0]]['c2p']:
                element = element2
            elif maindegreeMap[element1[0]]['p2c'] > maindegreeMap[element2[0]]['p2c']:
                element = element1
            elif maindegreeMap[element1[0]]['p2c'] < maindegreeMap[element2[0]]['p2c']:
                element = element2
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element1
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element2
            elif element1[0] < element2[0]:
                element = element1
            else:
                element = element2
            if len(sorted_r2r)>0:
                element1 = element
                element2 = sorted_r2r.pop(-1)
            else:
                break
        m = element[0]

#    for m in maindegreeMap.keys():
        if m not in maindegreeMap.keys():
            pass
        elif maindegreeMap[m]['p2p'] > 0 and m in list(b.nodes()):
            edges = list(b.edges(m))
            removeProv = set()
            removeCust = set()
            removePeer = set()
            removeProvEdge = set()
            for i in edges:
                if c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                    removeProv.add(i[1])
                    removeProvEdge.add(i)
                if c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                    removePeer.add(i)
            prov = set(removeProv)
            while len(prov) > 0 :
                x=prov.pop()
                edges = list(b.edges(x))
                for i in edges:
                    if c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                        removeProv.add(i[1])
                        prov.add(i[1])
                        removeProvEdge.add(i)
                    if c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                        removePeer.add(i)
                    
                    
            edges = [] 
            for i in removeProvEdge:
                if  c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                    b.remove_edge(i[0],i[1])
                    #b.remove_edge(i[1],i[0])
            for i in removePeer:
                #if  c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                try:
                    b.remove_edge(i[0],i[1])
                    b.remove_edge(i[1],i[0])
                except:
                    print "err"
                    pass
            remove = removeCust.union(removePeer.union(removeProv))
            for i in removeProv:
                b.remove_node(i)
                #newset.add(i)
            maindegreeMap = dict(degreemap(b))
            nodedegree = dict(degreemap(b))
            r2r = dict()
            for n in nodedegree.keys():
                if nodedegree[n][key] > 0:
                    r2r[n] = nodedegree[n][key]
            x= set()
            if m in list(b.nodes()):
                x = set(b.neighbors(m))
            cust =set()
            nodedegree = dict(degreemap(b))
            newset.add(m)
            r2r_new = dict()
            for cc in x:
                if c[b.get_edge_data(m,cc)['relationship']] == 'p2c':
                    if  nodedegree[cc]['p2p']>0:
                        cust.add(cc)
                        r2r_new[cc] = nodedegree[cc][key]
            #b.remove_node(m)
            if len(cust) >0:
                newset.remove(m)
                sorted_r2r = sorted(r2r_new.items() , key = operator.itemgetter(1))
            else:
                sorted_r2r = sorted(r2r.items() , key = operator.itemgetter(1))
            maindegreeMap = dict(degreemap(b))
            nodedegree = dict(degreemap(b))
    print set(b.nodes())
    print(list(b.edges()))
#    newset = set(b.nodes())            
    print("{} Monitors found after peer elimination, at {}".format( len(newset), time.time()))
    return newset



def elimination5(g, monitors , key , conflictpair = [], oldconflictpair = list()):
    print("{} elimination stage".format(key))
    #return monitors
    newset = set()
    if len(monitors) > 0:
        print "subgraph created"
        b= nx.DiGraph(g.subgraph(list(monitors)))
    else:
        b= nx.DiGraph(g)
    edges = list(b.edges())
    maindegreeMap = dict(degreemap(b)) 
    nodedegree = dict(degreemap(b))
    r2r = dict()
    for n in nodedegree.keys():
        if nodedegree[n][key] > 0:
            r2r[n] = nodedegree[n][key]
        else:
            pass
            #newset.add(n)
    sorted_r2r = sorted(r2r.items(), key=operator.itemgetter(1))     
    while len(sorted_r2r ) > 0 :
        print "size of sorted r2r is:"
        print newset
        print(len(sorted_r2r))
        element1 = sorted_r2r.pop(-1)
        element = element1
        element2 = (-1,-1)
        if len(sorted_r2r) > 0:
           element2=sorted_r2r.pop(-1)
        while element2[1] == element1[1]:
            if element2[0] in conflictpair:
                print "conflict pair detected"
                if (element2[0],element1[0]) == conflictpair:
                    element=element1
                else:
                    element=element2
                break
            elif maindegreeMap[element1[0]]['c2p'] > maindegreeMap[element2[0]]['c2p']:
                element = element1
            elif maindegreeMap[element1[0]]['c2p'] < maindegreeMap[element2[0]]['c2p']:
                element = element2
            elif maindegreeMap[element1[0]]['p2c'] > maindegreeMap[element2[0]]['p2c']:
                element = element1
            elif maindegreeMap[element1[0]]['p2c'] < maindegreeMap[element2[0]]['p2c']:
                element = element2
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element1
            elif maindegreeMap[element1[0]]['s2s'] > maindegreeMap[element2[0]]['s2s']:
                element = element2
            elif element1[0] < element2[0]:
                element = element1
            else:
                element = element2
            if len(sorted_r2r)>0:
                element1 = element
                element2 = sorted_r2r.pop(-1)
            else:
                break
        m = element[0]

#    for m in maindegreeMap.keys():
        if m not in maindegreeMap.keys():
            pass
        elif maindegreeMap[m]['p2p'] > 0 and m in list(b.nodes()):
            edges = list(b.edges(m))
            removeProv = set()
            removeCust = set()
            removePeer = set()
            removeProvEdge = set()
            for i in edges:
                if c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                    removeProv.add(i[1])
                    removeProvEdge.add(i)
                if c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                    removePeer.add(i)
            prov = set(removeProv)
            while len(prov) > 0 :
                x=prov.pop()
                edges = list(b.edges(x))
                for i in edges:
                    if c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                        removeProv.add(i[1])
                        prov.add(i[1])
                        removeProvEdge.add(i)
                    if c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                        removePeer.add(i)
                    
                    
            conflict = False
            print(removeProv,m)
            print "providers"
            for i in removeProv:
                neighbours  = set(g.neighbors(i))
                for j in neighbours:
                    if j in newset and c[g.get_edge_data(i,j)['relationship']]== 'p2p':
                        conflictpair = [j,i]
                        conflict=True
            if conflict == True and conflictpair not in oldconflictpair:
                print "conflict pair"
                print conflictpair, newset, m
                return set(), conflictpair
            edges = [] 
            for i in removeProvEdge:
                if  c[b.get_edge_data(i[0],i[1])['relationship']] == 'c2p':
                    b.remove_edge(i[0],i[1])
                    #b.remove_edge(i[1],i[0])
            for i in removePeer:
                #if  c[b.get_edge_data(i[0],i[1])['relationship']] == 'p2p':
                try:
                    b.remove_edge(i[0],i[1])
                    b.remove_edge(i[1],i[0])
                except:
                    print "err"
                    pass
            remove = removeCust.union(removePeer.union(removeProv))
            for i in removeProv:
                b.remove_node(i)
                if i in newset:
                    newset.remove(i)
                #newset.add(i)
            maindegreeMap = dict(degreemap(b))
            nodedegree = dict(degreemap(b))
            r2r = dict()
            for n in nodedegree.keys():
                if nodedegree[n][key] > 0:
                    r2r[n] = nodedegree[n][key]
            x= set()
            if m in list(b.nodes()):
                x = set(b.neighbors(m))
            cust =set()
            nodedegree = dict(degreemap(b))
            newset.add(m)
            r2r_new = dict()
            for cc in x:
                if c[b.get_edge_data(m,cc)['relationship']] == 'p2c':
                    if  nodedegree[cc]['p2p']>0:
                        cust.add(cc)
                        r2r_new[cc] = nodedegree[cc][key]
            #b.remove_node(m)
            if len(cust) >0:
                newset.remove(m)
                sorted_r2r = sorted(r2r_new.items() , key = operator.itemgetter(1))
            else:
                sorted_r2r = sorted(r2r.items() , key = operator.itemgetter(1))
            maindegreeMap = dict(degreemap(b))
            nodedegree = dict(degreemap(b))
    print set(b.nodes())
    print(list(b.edges()))
#    newset = set(b.nodes())            
    print("{} Monitors found after peer elimination, at {}".format( len(newset), time.time()))
    return newset, []



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

def newmonitorselection( g = None , graphFile = '', version= 0):
    #tier_1 = list(gettier1ASes(graphFile))
    tier_1 = set()            
    monitors = set()
    customers = set()
    for i in tier_1:
        monitors.add(i.strip())
        customers = customers.union(getcustomers(g , i.strip()))
        print("customers found {}".format(len(customers)))
        
    while len(customers) > 0 and True == False:
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
    degreemapgraph = dict(degreemap(g))
    monitors = set()
    for i in degreemapgraph.keys():
        if degreemapgraph[i]['p2p'] > 0:
            monitors.add(i)
        if degreemapgraph[i]['c2p'] == 0:
            pass
            #monitors.add(i)
    #moncustcone = dict(dfsexplorer(g,monitors))
    if True == False:
        monitors = set(elimination(g ,monitors, 'p2p'))
    elif version == 2:
        print "final version"
        #time.sleep(10)
        conflictpair=[]
        oldconflictpair=[]
        counter = 10000
        while True == True:
            monitors , conflictpair= elimination5(g=g ,monitors=set(), key= 'p2p', conflictpair = conflictpair, oldconflictpair=oldconflictpair)
            if conflictpair not in oldconflictpair:
                oldconflictpair.append(conflictpair)
            counter-=1
            if len(conflictpair)==0 or counter==0:
                break
        if counter == 0 and len(conflictpair)!=0:
            print "counter expired"
            monitors= elimination4(g=g ,monitors=set(), key= 'p2p')
        print "here are he monitors"
        print monitors
    elif version == 1:
        print "refined version"
        print len(monitors)
        #time.sleep(10)
        monitors = set(elimination4(g ,monitors, 'p2p'))
        print "here are he monitors"
        print monitors
    elif version == 0:
        print "basic"
        print len(monitors)
        #stime.sleep(10)
        monitors = set(elimination2(g ,monitors, 'p2p'))
    else:
        print "going for eliminations"
        decisions = dict()
        for i in range(0,len(monitors)+1):
            decisions[i]=dict()
            decisions[i]['left'] = []
            decisions[i]['decided'] = []
            decisions[i]['status']='U'
        mm1, dsn = (longtermshorttermelimination(g ,monitors, 'p2p',decisions=decisions) )
        print "returned from eliminations"
        counter=0
        while counter <=100:
            mm2, dsn = longtermshorttermelimination(g ,monitors, 'p2p',decisions=dsn )
            counter+=1
            print len(mm2)
            print mm2
            if len(mm1) > len(mm2):
                mm1=mm2
    return monitors
    
def dfsexplorer(g = None , monitors = set()):
    moncustcone  = dict()
    for i in monitors:
        cust = getcustomers(g,i)
        moncustcone[i] = set()
        while len(cust) > 0:
            moncustcone[i] =  moncustcone[i].union(cust)
            newcust = set()
            for j  in cust:
                newcust= newcust.union(getcustomers(g,j))
            cust = newcust
    print " returning monitor"
    return moncustcone
        

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
    
 

def greedylink3(monitor = None, links = None, timestamp = None , monsetlen = None):
    visible_links = set()
    vp =[]
    monitor_len = dict()
    copy_monitor = dict(monitor)
    visible_prob = dict()
    monkeyset = list(monitor.keys())
    monkeyset.sort()
    for i in monkeyset:
        for j in monkeyset:
            for k in monkeyset:
                if i <j and j < k:
                    monitor_len.update({i+"_"+j+"_"+k:len(monitor[i].union(monitor[j].union(monitor[k])))})
                    visible_prob.update({i+"_"+j+"_"+k:len((monitor[i].union(monitor[j].union(monitor[k]))))/float(len(links))})
                    #monitor_len.update({i+"_"+j:len(monitor[i].union(monitor[j]))})
                    #visible_prob.update({i+"_"+j :len((monitor[i].union(monitor[j])))/float(len(links))})
    print("Important: {}|{}".format(len(monkeyset),len(monitor_len)))
    time.sleep(10)    
    threshold = 0
    vp_copy =set()
    distribution = dict()
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
    while len(sorted_x ) > 0:
        r = sorted_x.pop(-1)
        if r[1] > threshold:
            mons = r[0].split("_")
            for i in mons:
                vp.append(i)
                visible_links = visible_links.union(copy_monitor[i])
                if len(vp) == monsetlen:
                    vp_copy = vp_copy.union(visible_links)
                number = float(len(visible_links))*100.0/len(links)
                distribution.update({len(vp): number})
                copy_monitor.pop(i)
                monkeyset.remove(i)
                if len(visible_links) == len(links):
                    break;
        if len(visible_links) == len(links):
            break;
        for i in copy_monitor.keys():
            copy_monitor[i] = copy_monitor[i].difference(visible_links)
        monitor_len = dict()
        monkeyset.sort()
        for i in monkeyset:
            for j in monkeyset:
                for k in monkeyset:
                    if i <j  and j < k:
                        monitor_len.update({i+"_"+j+"_"+k:len(monitor[i].union(monitor[j].union(monitor[k])))})
                        visible_prob.update({i+"_"+j+"_"+k:len((monitor[i].union(monitor[j].union(monitor[k]))))/float(len(links))})
                        #monitor_len.update({i+"_"+j:len(monitor[i].union(monitor[j]))})
                        #visible_prob.update({i+"_"+j :len((monitor[i].union(monitor[j])))/float(len(links))})
        print("Important: {}|{}".format(len(monkeyset),len(monitor_len)))    
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