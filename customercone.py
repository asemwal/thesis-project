# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 11:36:20 2018

@author: asemwal
"""
import math
import time
import networkx as nx
import utils


def customerCone(g, node):
     c  = set()
     a=set()
     a.add(node)
     #print(node)
     while len(a) >0:
         x = a.pop()
         r = list(g.edges(x))
         for i in range(0,len(r)):
             if (g.get_edge_data(r[i][0], r[i][1])['relationship'] == 'provider-to-customer' ):
                 
                 if r[i][1] not in c:
                     a.add(r[i][1])
                     c.add(r[i][1])
     return c
    
            




y='174,6939,3320,6762,1299,2914,3356,6453,3491,286,12956,6461,6830,5580,3257,209,7922,2828,4134,20940,5511,1239,701,7018'.split(',')
#y='3320,6762,1299,2914,3356,6453,3491,286,12956,6461,6830,5580,3257,209,7922,2828,4134,20940,5511,1239,701,7018'.split(',')
g = nx.DiGraph()
f='links'
#file = open(location+year+f, 'r')
file = open('/home/asemwal/raw_data/2018/old_proc/relationships','r')
purpose='neighbour_cliques'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'


print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
while(l !=''):
    x= l.split('|')
    if(len(x) ==3 ):
        if(str(x[0]) in y and str(x[1]) in y):
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = 'peer-to-peer')
        elif(str(x[0]) in y and str(x[1]) not in y):
            g.add_edge(str(x[0]), str(x[1]) , relationship = 'provider-to-customer')
        elif(str(x[0]) not in y and str(x[1]) in y ):
            g.add_edge(str(x[0]), str(x[1]) ,  relationship = 'customer-to-provider')
        else:
            g.add_edge(str(x[0]), str(x[1]) , relationship = 'undefined')
    l = (file.readline()).strip()
links = list(g.edges)
tier2nodes = set()
remove = set()
for i in range (0, len(links)):
    if g.get_edge_data(links[i][0],links[i][1])['relationship'] != 'undefined':
        remove.add(links[i]) # add tier1 p2p and p2c,c2p links b/w tier1 and tier2 ASes
        if g.get_edge_data(links[i][0],links[i][1])['relationship'] == 'customer-to-provider':
            tier2nodes.add(links[i][0])
        elif g.get_edge_data(links[i][0],links[i][1])['relationship'] == 'provider-to-customer':
            tier2nodes.add(links[i][1])

a = g.subgraph(list(tier2nodes))
edgelist = list(a.edges())
for i in range(0,len(edgelist)):
    if g.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship'] == 'undefined':
        g.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship'] ='peer-to-peer'
        remove.add(edgelist[i]) # add tier2 p2p links for removing from graph
del(a)

edges = list(g.edges())
p2c=0
c2p=0
p2p=0
u=0
for i in range(0, len(edges)):
    if g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'undefined':
        u +=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'peer-to-peer':
        p2p+=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'customer-to-provider':
        c2p+=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'provider-to-customer':
        p2c+=1    
print("p2p:{}\tp2c:{}\tc2p:{}\tu:{}".format(p2p,p2c,c2p,u))

nodes = list(g.nodes())
customer = {}
for i in range(0, len(nodes)):
    c = customerCone(g,nodes[i])
    customer.update({nodes[i]: (c , len(c))})

#g.remove_edges_from(list(remove))

#nodes = list(g.nodes())
#for i in range(0, len(nodes)):
#    if g.degree(nodes[i]) ==0:
#        g.remove_node(nodes[i])

factor = 5
G=nx.DiGraph( )
edges = list(g.edges())
for i in range(0, len(edges)):
    if g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'undefined':
        G.add_edge(edges[i][0],edges[i][1], relationship = 'undefined')
edgelist= list(G.edges())
for i in range(0,len(edgelist)):
    if g.degree(edgelist[i][0]) > factor* g.degree(edgelist[i][1]):
        if G.get_edge_data(edgelist[i][0],edgelist[i][1]) == None:
            G.remove_edge(edgelist[i][0],edgelist[i][1])
            G.add_edge(edgelist[i][0],edgelist[i][1], relationship = 'provider-to-customer2')
        else:
            G.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship'] = 'provider-to-customer2'
    elif g.degree(edgelist[i][1]) > factor* g.degree(edgelist[i][0]):
        if G.get_edge_data(edgelist[i][0],edgelist[i][1]) == None:
            G.remove_edge(edgelist[i][0],edgelist[i][1])
            G.add_edge(edgelist[i][0],edgelist[i][1], relationship = 'customer-to-provider2')
        else:
            G.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship'] = 'customer-to-provider2'
    elif g.degree(edgelist[i][1]) == g.degree(edgelist[i][0]) or True == True:
        if G.get_edge_data(edgelist[i][0],edgelist[i][1]) == None:
            G.remove_edge(edgelist[i][0],edgelist[i][1])
            G.add_edge(edgelist[i][0],edgelist[i][1], relationship = 'peer-to-peer2')
        else:
            G.get_edge_data(edgelist[i][0],edgelist[i][1])['relationship'] = 'peer-to-peer2'
    

edges = list(G.edges())
p2c=0
c2p=0
p2p=0
u=0
for i in range(0, len(edges)):
    g.get_edge_data(edges[i][0],edges[i][1])['relationship'] =G.get_edge_data(edges[i][0],edges[i][1])['relationship']
    if G.get_edge_data(edges[i][0],edges[i][1])  == None:
        u +=1
    elif G.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'undefined':
        u +=1
    elif G.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'peer-to-peer':
        p2p+=1
    elif G.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'customer-to-provider':
        c2p+=1
    elif G.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'provider-to-customer':
        p2c+=1    
print("p2p:{}\tp2c:{}\tc2p:{}\tu:{}".format(p2p,p2c,c2p,u))
      
edges = list(g.edges())
p2c=0
c2p=0
p2p=0
u=0
for i in range(0, len(edges)):
    if g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'undefined':
        u +=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'peer-to-peer':
        p2p+=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'customer-to-provider':
        c2p+=1
    elif g.get_edge_data(edges[i][0],edges[i][1])['relationship'] == 'provider-to-customer':
        p2c+=1    

print("p2p:{}\tp2c:{}\tc2p:{}\tu:{}".format(p2p,p2c,c2p,u))


file = open('/home/asemwal/raw_data/2018/proc/peerpathvisibility_1530740000_1530742499','r')
purpose='verification'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
path ={}
while(l !=''):
    x = l.split("|")
    ases = []
    if x[1] != '' and l.find("{") < 0:
        newases = x[1].split(" ")
        ases.append(newases[0])
        links = []
        for i in range(1, len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
        for i in range(1, len(ases)):
            links.append(g.get_edge_data(ases[i-1],ases[i])['relationship'])
        path.update({" ".join(ases): " ".join(links)})    
    l = (file.readline()).strip()

#all paths
line =''
file = open('/home/asemwal/raw_data/2018/proc/all_paths_somehow','w')
for i in path.keys():
    links = path[i].split(" ")
    line = i +'\n' +path[i]+'\n'
    file.write(line)
file.flush()
file.close()


#valley free routing violated
line =''
file = open('/home/asemwal/raw_data/2018/proc/customercone21_py','w')
for i in path.keys():
    links = path[i].split(" ")
    hill = False;
    
    for j in range(0,len(links)):
        if hill == False:
            if links[j] in ('peer-to-peer','sibling-to-sibling','customer-to-provider','peer-to-peer2','sibling-to-sibling2','customer-to-provider2'):
                pass
            elif links[j] in ( 'provider-to-customer','provider-to-customer2'):
                hill = True 
            else:
                line = i +'\n' +path[i]+'\n'
                file.write(line)
                break;
        elif hill == True:
            if links[j] in ('provider-to-customer','sibling-to-sibling', 'peer-to-peer','provider-to-customer2','sibling-to-sibling2', 'peer-to-peer2'):
                pass
            else:
                line = i +'\n' +path[i]+'\n'
                file.write(line)
                break;
file.flush()
file.close()








# '8492 9002 3356 14762': 'peer-to-peer customer-to-provider provider-to-customer',



    

print("{}->{}".format(nodelist[i],G.degree(nodelist[i])))

print(g.number_of_edges())
print(g.number_of_nodes())
tier2 = set()
neighbour = {}
for i in range(0, len(y)):
    neighbourlist = set()
    r = g.neighbors(y[i])
    while True:
        try:
            asn = r.next()
            if asn not in y:
                neighbourlist.add(asn)
                tier2.add(asn)
        except StopIteration:
            break
    neighbour.update({y[i]:neighbourlist})
line=""
while True:
    try:
        r = neighbour.popitem()
        line+= r[0]+"|" + str(len(r[1])) +"|"+ ", ".join(list(r[1]))+"\n"
    except KeyError:
        break;
line+="\n\n\n\n\n\nPrinting Tier2 Networks\n"
line+= 'Number of T2 networks: '+ str(len(tier2)) +'\n'
line+= ", ".join(list(tier2))
t2 = list(tier2)
tier3 = set()
neighbour = {}
for i in range(0, len(t2)):
    neighbourlist = set()
    r = g.neighbors(t2[i])
    while True:
        try:
            asn = r.next()
            if asn not in y and asn not in t2:
                neighbourlist.add(asn)
                tier3.add(asn)
        except StopIteration:
            break
    neighbour.update({t2[i]:neighbourlist})


if True:
    f='aspathsdups_deduped'
    file = open('/home/asemwal/thesis/bgpreader/proc/'+notier1, 'r')
    l = str(file.readline()).strip()
    peer = {}
    while(l !=''):
        x = l.split(" ")
        try:
            peer[x[0]] =1
        except KeyError as e:
            peer.update({x[0]:0})
            
    for k in peer.keys():
        g.remove_node(k);
    
    



print('finding cliques')
G=nx.Graph(g)
a=nx.find_cliques(G)
print(a)
line=''
while(True):
    try:
        r=a.next()
        line += str(len(r))+"|"+",".join(r) +"\n"
    except StopIteration as e:
        break;
        pass
out = open(location+year+'proc/'+purpose+utils.getTimeStamp(file.name.split('/')[-1]), 'w')
out.write(line)
out.flush()
out.close()

