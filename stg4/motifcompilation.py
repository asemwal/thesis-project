# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 15:02:24 2018

@author: asemwal
"""
import matplotlib.pyplot as plt
from networkx import Graph
import networkx as nx
import networkx.algorithms.isomorphism as iso
graphset = dict()
file = open('/home/asemwal/raw_data/2018/proc/relationships_motifbuilder','r')
l = str(file.readline()).strip()
G = nx.DiGraph()
em = iso.categorical_edge_match('relationship', '')
start = False
while l != '':
    if start == False:
        if l == 'MOTIF+++++':
            start = ~start
            G = nx.DiGraph()
    else:
        if l == 'MOTIF+++++':
            start = ~start
            key = G.__hash__()
            if G.number_of_nodes() >50:
                pass
            else:
                
                matched= False
                for y in graphset.keys():
                    if nx.is_isomorphic(nx.Graph(G), nx.Graph(graphset[y]['graph']), edge_match = em) == False:
                        pass
                    else:
                        matched = True
                        key = y
                        break;
                if matched == True:
                    graphset[key]['count'] += 1
                else:
                    graphset.update({key:{'graph':G,'count':1}})                    
                
            
        else:
            if l.find('count:') > -1 :
                counter = int(l.split(':')[1].strip())
            elif l.find("-->") > -1:
                x = l.split("-->")
                G.add_edge(x[0]  , x[2] , relationship = x[1])
            else:
                if l == 'counter':
                    break
               
    l = str(file.readline()).strip()

x = graphset.keys()
x = list(x)       
for i in x:
    edges = list(graphset[i]['graph'].edges())
    for e in edges:
        if graphset[i]['graph'].get_edge_data(e[0],e[1])['relationship'] == 'customer-to-provider':
            graphset[i]['graph'].remove_edge(e[0],e[1])
    lables  = nx.get_edge_attributes(graphset[i]['graph'], 'relationship')
    nx.draw_circular(graphset[i]['graph'],edge_lables=True)
    nx.draw_networkx_edge_labels(graphset[i]['graph'], nx.circular_layout(graphset[i]['graph']) ,  lables , font_size= 10)
    plt.savefig('/home/asemwal/raw_data/2018/motifsss/'+str(i)+'_count_'+str(graphset[i]['count'])+'.png')
    plt.show()
        