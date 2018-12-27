# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 01:18:21 2018

@author: asemwal
"""
import math
import time
import networkx as nx
gList=[]
i=0
y='6939,3320,6762,1299,2914,3356,6453,3491,286,12956,6461,6830,5580,3257,209,7922,2828,4134,20940,5511,1239,701,7018'.split(',')
while i < len(y):
    g = nx.Graph()
    file = open('/home/asemwal/raw_data/2018/proc/aspathsdups_deduped','r')
    print(time.time())
#file = open(location+year+'proc/'+f, 'r')
    l = (file.readline()).strip()
    while(l !=''):
        
        x= l.split('|')
        
        if(x[0] !=''  and y[i] == x[0].split(" ")[0] ):
            if len(x[0].split(" ")) > 1:
                if x[0].split(" ")[1] not in y:
                    g.add_path(x[0].split(" "), relation='P2C')
        l = (file.readline()).strip()

    print(g.number_of_edges())
    print(g.number_of_nodes())
    gList.append(g)
    i+=1
Un = nx.Graph()
for i in range(0,len(gList)):
    Un = nx.disjoint_union(Un, gList[i])
print(Un.number_of_edges())
print(Un.number_of_nodes())
"""
for j in range(0,len(y)):
    if True:
        g.remove_node(y[j])
a=nx.find_cliques(g)
print(a)
line=''
while(True):
    try:
        r=a.next()
        line += str(len(r))+"|"+",".join(r) +"\n"
    except StopIteration as e:
        break;
        pass
out = open('/home/asemwal/thesis/bgpreader/proc/notier1clieque', 'w')
out.write(line)
out.flush()
out.close()
        
#r.append(list(g.edges(y[i])))
#i+=1
"""
