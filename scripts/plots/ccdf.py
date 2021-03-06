# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 19:57:25 2018

@author: asemwal
"""

import networkx as nx
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from mpltools import annotation
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
r='c2p'

#y=generategraphARank('/home/asemwal/raw_data/scripts/plots/ARank/20170901.as-rel2.txt')
#x=generategraphARank('/home/asemwal/raw_data/scripts/plots/ARank/20180801.as-rel2.txt')
#x=generategraphAStop('/home/asemwal/raw_data/experiments/AStop/AStop_6300_1545553753')
#x=generategraph2('/home/asemwal/raw_data/experiments/graphs/done//home/asemwal/raw_data/experiments/graphs/done/graph_100_1540810042')

def plotccdf(graphfile1='/home/asemwal/raw_data/scripts/plots/ARank/20181001.as-rel2.txt'):
    y=generategraphARank(graphfile1)
    x=generategraphAStop('/home/asemwal/raw_data/experiments/AStop/AStop_62773_1545844643')
    y=generategraphAStop('/home/asemwal/raw_data/experiments/AStop/AStop_62773_1545844643')
    #y=generategraphAStop('/home/asemwal/raw_data/experiments/AStop/AStop_16300_1545765609')
    #x=generategraph2('/home/asemwal/raw_data/experiments/graphs/done/graph_600_1540810167')
    #y=generategraph2('/home/asemwal/raw_data/experiments/graphs/done/graph_600_1540810165')
    
    ccdf= {'c2p':{} , 'p2p':{} , 'p2c':{} }
    ccdf2= {'c2p':{} , 'p2p':{} , 'p2c':{} }
    peering= {'c2p':[] , 'p2p':[] , 'p2c':[] }
    y2= {'c2p':[] , 'p2p':[] , 'p2c':[] }
    y1= {'c2p':[] , 'p2p':[] , 'p2c':[] }
    x2= {'c2p':[] , 'p2p':[] , 'p2c':[] }
    x1= {'c2p':[] , 'p2p':[] , 'p2c':[] }
    peering2= {'c2p':[] , 'p2p':[] , 'p2c':[] }

    dr=degreemap(y)
    d = degreemap(x)
    r='p2p'
    for i in dr.keys():
        if int(dr[i][r]) in ccdf2[r].keys():
            ccdf2[r][int(dr[i][r])]+=1
        else:
            ccdf2[r].update({int(dr[i][r]):1})
        
    for i in d.keys():
        if int(d[i][r]) in ccdf[r].keys():
            ccdf[r][int(d[i][r])]+=1
        else:
            ccdf[r].update({int(d[i][r]):1})
    x1[r] = list(ccdf[r].keys())
    x2[r]= list(ccdf2[r].keys())
    x1[r].sort()
    x2[r].sort()
    sum=0
    while len(x1[r]) > 0 :
        q=x1[r].pop(-1)
        y1[r].append(  q)
        sum+=ccdf[r][q]
        val = float(sum)/x.number_of_nodes()
        peering[r].append(val)
    sum=0
    while len(x2[r]) > 0 :
        q=x2[r].pop(-1)
        y2[r].append(  q)
        sum+=ccdf2[r][q]
        val = float(sum)/y.number_of_nodes()
        peering2[r].append(val)

    r='p2c'
    for i in dr.keys():
        if int(dr[i][r]) in ccdf2[r].keys():
            ccdf2[r][int(dr[i][r])]+=1
        else:
            ccdf2[r].update({int(dr[i][r]):1})
        
    for i in d.keys():
        if int(d[i][r]) in ccdf[r].keys():
            ccdf[r][int(d[i][r])]+=1
        else:
            ccdf[r].update({int(d[i][r]):1})
    sum=0
    x1[r] = list(ccdf[r].keys())
    x2[r]= list(ccdf2[r].keys())
    x1[r].sort()
    x2[r].sort()
    while len(x1[r]) > 0 :
        q=x1[r].pop(-1)
        y1[r].append(  q)
        sum+=ccdf[r][q]
        val = float(sum)/x.number_of_nodes()
        peering[r].append(val)

    sum=0
    while len(x2[r]) > 0 :
        q=x2[r].pop(-1)
        y2[r].append(  q)
        sum+=ccdf2[r][q]
        val = float(sum)/y.number_of_nodes()
        peering2[r].append(val)
        
    r='c2p'
    for i in dr.keys():
        if int(dr[i][r]) in ccdf2[r].keys():
            ccdf2[r][int(dr[i][r])]+=1
        else:
            ccdf2[r].update({int(dr[i][r]):1})
    
    for i in d.keys():
        if int(d[i][r]) in ccdf[r].keys():
            ccdf[r][int(d[i][r])]+=1
        else:
            ccdf[r].update({int(d[i][r]):1})



    x1[r] = list(ccdf[r].keys())
    x2[r]= list(ccdf2[r].keys())
    x1[r].sort()
    x2[r].sort()
    sum=0
    while len(x1[r]) > 0 :
        q=x1[r].pop(-1)
        y1[r].append(  q)
        sum+=ccdf[r][q]
        val = float(sum)/x.number_of_nodes()
        peering[r].append(val)
        sum=0
    while len(x2[r]) > 0 :
        q=x2[r].pop(-1)
        y2[r].append(  q)
        sum+=ccdf2[r][q]
        val = float(sum)/y.number_of_nodes()
        peering2[r].append(val)
                

    data = []
    a=0
    average = [ ]
    median = [ ]
    percentile25 = [ ]
    percentile75 = [ ]
    sdev0 = [ ]
    sdev1 = [ ]
    
    average1 = [ ]
    median1 = [ ]
    percentile251 = [ ]
    percentile751 = [ ]
    sdev01 = [ ]
    sdev11 = [ ]
    
    l = False 
    #y = [100,200,300,400,500,600] 
    
    #label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
    color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'k','g']
    #color = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    #matplotlib.rcParams['axes.prop_cycle']
    #plt.ylim((0,90))
    #plt.xlim((0,0.9))
    #fig, ax1 = plt.subplots()
    
    #ax1.set_xlabel('Normalized Invisibility Score', fontsize=8)
    #ax1.set_ylabel('Link Coverage', fontsize=8)
    plt.xlabel('Degree', fontsize=16)
    plt.ylabel('CCDF', fontsize=16)
    #ax1.tick_params(axis='y' )
    #ax2 = ax1.twinx()
    #ax2.set_ylabel('Monitor Set Size', fontsize=8)
    #ax2.tick_params(axis='y' )
    
    #    y=  d.keys() 
    label = ['p2p','p2p_2','p2c','p2c_2','c2p','c2p_2']
    plt.loglog( y1['p2p'],peering['p2p'],'bo',label = label[0] )
    #plt.loglog( y2['p2p'],peering2['p2p'],'ro',label = label[1] )
    plt.loglog( y1['p2c'],peering['p2c'],'rs' ,label = label[2] )
    #plt.loglog( y2['p2c'],peering2['p2c'],'rs',label = label[3] )
    plt.loglog( y1['c2p'],peering['c2p'],'mx' ,label = label[4] )
    #plt.loglog( y2['c2p'],peering2['c2p'],'rx',label = label[5] )
    
    annotation.slope_marker((10, 2), (1, 2),  
                        text_kwargs={'color': 'cornflowerblue'},
                        poly_kwargs={'facecolor': (0.73, 0.8, 1)})
    #ax2.set_title('loglog, custom colors')
    plt.legend(loc=1,fontsize=16)
    #ax2.legend(loc=2,fontsize=8)
    
    
    plt.savefig('astop_ccdf.pdf', format='pdf', dpi=5000)
    plt.show()

