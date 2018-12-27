# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 16:15:00 2018

@author: asemwal
"""

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

g = nx.DiGraph()
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
        if x[2] == 'customer-to-provider' and False == True :
            g.add_edge(str(x[1]), str(x[0]) ,  relationship = 'provider-to-customer')
            #g.add_edge(str(x[0]), str(x[1]) ,  relationship = 'customer-to-provider')
        elif  x[2] == 'provider-to-customer' and False == True:
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])
            #g.add_edge(str(x[1]), str(x[0]) ,  relationship = inverselink(x[2]))
        elif  x[2] == 'peer-to-peer':
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = x[2])

    l = (file.readline()).strip()
print("working...")

graphs = list( nx.connected_component_subgraphs(nx.Graph(g)))
len(graphs)
    
for i in graphs:
    print(i.number_of_edges())
    print(i.number_of_nodes())