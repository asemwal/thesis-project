# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 08:42:40 2018

@author: asemwal
"""

"""
Toy Graph Generator

"""

import networkx as nx
import numpy as np
import time
import monitorselection as ms


def prefixassociation( customer = None, moas = [] , k = 1  ):
    prefixassoc = dict()
    prob = [1.0] * len(customer)
    prob /= np.sum(prob)
    multi_provider = list()
    for i in moas:
        if i == 1:
            r= np.exp(-1 *k* i)
        else:
            r= np.exp(-1 *k* i*10)            
        multi_provider.append(r)
    
    multi_provider /= np.sum(multi_provider)
    prefixes = set()
    prefixprob = []
    ip1 = list(range(0,256,1))
    ip1_p = [1.0]*len(ip1)
    ip1_p /= np.sum(ip1_p)
    
    ip2 = list(range(0,256,1))
    ip2_p = [1.0]* len(ip2)
    ip2_p /= np.sum(ip2_p)
    
    ip3 = list(range(0,256,1))
    ip3_p = [1.0]* len(ip3)
    ip3_p /= np.sum(ip3_p)

    while len(prefixes) < len(customer):
        l = list()
        temp = list( np.random.choice(ip1, 1, p=ip3_p))
        l.append(str(temp[0]))
        temp = list( np.random.choice(ip2, 1, p=ip3_p))
        l.append(str(temp[0]))
        temp = list( np.random.choice(ip3, 1, p=ip3_p))
        l.append(str(temp[0]))
        l+= [ '0/24']
        print(l)
        prefixes.add(".".join(l))
        
        
    for p in prefixes:
        p_count =  np.random.choice(moas , 1, p=multi_provider)
        print(p_count)
        customers = list(np.random.choice(customer, p_count[0] , p=prob))
        
        #print(providers)
        for c in customers:
            try:
                prefixassoc[p].append(c)
            except KeyError:
                prefixassoc.update({p:[c]})
        
    return prefixassoc
            
            
            
        
        
def addprovider(customer = None , provider = None, list_of_provider = [], k =1, relationship = 'provider-to-customer' ):
    global g
    multi_provider = list()
    for i in list_of_provider:
        r= np.exp(-1 *k* i)
        multi_provider.append(r)
            
    multi_provider /= np.sum(multi_provider)
    multi_provider = list(multi_provider)
    print(multi_provider)
    for c in customer:
        p_count =  np.random.choice(list_of_provider, 1, p=multi_provider,replace = False)
        #print(p_count)
        removed = False
        index = -1
        temp = 0.0
        if c in provider:
            index = provider.index(c)
            provider.remove(c)
            
            removed = True
        prob = [1.0] * len(provider)
        prob /= np.sum(prob)
        prob = list(prob)
    
        providers = list(np.random.choice(provider, p_count[0], p=prob, replace = False))
        #print(providers)
        for p in providers:
            if p != c:
                g.add_edge(p,c , relationship = relationship)
                g.add_edge(c,p , relationship = inverselink(relationship))
        if removed == True:
            provider.insert(index, c)
            
        
    




def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def graph(nodes = 10):
    G = nx.DiGraph()
    for i in range(1,nodes+1):
        G.add_node(str(i))
    
    return G
    

def addpeeredges(tier = None, prob = None, relationship = 'peer-to-peer', threshold = 3):
    global g
    choice = [1 ,0 ]
    while len(tier) > 1:
        i = tier.pop()
        count = 0
        while count <= threshold:
            for j in tier:
                chosen = np.random.choice(choice, 1, p=prob)
                if chosen[0] == 1:
                    g.add_edge(i , j , relationship = relationship)
                    g.add_edge(j , i , relationship = inverselink(relationship))
                    count += 1

    
def addprovideredges(tier = None , nexttier = None, prob = None, relationship = 'customer-to-provider', threshold = 1):
    global g
    choice = [1 ,0 ]
    while len(tier) > 1:
        i = tier.pop()
        count = 0
        while count < threshold:
            for j in nexttier:
                chosen = np.random.choice(choice, 1, p=prob, replace = False)
                if chosen[0] == 1:
                    g.add_edge(i , j , relationship = relationship)
                    g.add_edge(j , i , relationship = inverselink(relationship))
                    count += 1
                    if count > threshold:
                        break
   

def tiernodes(tier = None , nodes = None , start = None, end  = None):
    tier_n = list()
    for i in range(start , end):
        tier_n.append(str(tier)+str(nodes[i]))
    return tier_n
    
def toygraphgenerator(graphsize = 100):
    global g
    if graphsize < 100:
        return
    g = graph(graphsize)
    print(g.number_of_nodes())
    #return
    T1 = max(3 , int(g.number_of_nodes()* 0.0003 )) ##Core
    T2 = max(10 , int(g.number_of_nodes()* 0.007 ))  ## T2
    T3 = max(30 , int(g.number_of_nodes()* 0.0927 ))  ## ISP
    T4 = g.number_of_nodes() - T1 - T2 - T3  ## Enterprises

    print("{},{},{},{}".format(T1,T2,T3,T4))

    nodes = list(g.nodes())
    nodes.sort()
    start = 0;
    end = T1
    tier = nodes[start:end]
    tier_1 = list(tiernodes('T1_' , nodes , start , end))
    if len(tier_1) != len(tier):
        return 1+'a'
    
    start = end
    end = end+T2
    tier = nodes[start:end]
    tier_2 = list(tiernodes('T2_' , nodes , start , end))
    if len(tier_2) != len(tier):
        return 1+'a'
    
    start = end
    end = end+T3
    tier = nodes[start:end]
    tier_3 = list(tiernodes('T3_' , nodes , start , end))
    if len(tier_3) != len(tier):
        return 1+'a'
    
    start = end
    end = end + T4
    tier = nodes[start:end]
    tier_4 = list(tiernodes('T4_' , nodes , start , end))
    if len(tier_4) != len(tier):
        return 1+'a'

    g = nx.DiGraph()
    g.add_nodes_from(tier_1)
    g.add_nodes_from(tier_2)
    g.add_nodes_from(tier_3)
    g.add_nodes_from(tier_4)
    prob = [1.0] + [19.0] 
    prob /= np.sum(prob)     

    prefixowners = set()
    prefixowners.update(prefixowners.union(set(tier_4 )))
    prefixassoc = prefixassociation(list(prefixowners) , [1 , 2] , k = 1)

    addprovider(list(tier_4), list(tier_3) , list_of_provider= [1,2,3,4,5], k  = 5 , relationship= 'provider-to-customer')
    addprovider(list(tier_4), list(tier_2) , list_of_provider= [0,1 ], k  = 4 , relationship= 'provider-to-customer')
    addprovider(list(tier_3), list(tier_2) , list_of_provider= [1,2,3], k  = 2 , relationship= 'provider-to-customer')
    addprovider(list(tier_3), list(tier_1) , list_of_provider= [0,1 ], k  = 4 , relationship= 'provider-to-customer')
    addprovider(list(tier_2), list(tier_1) , list_of_provider= [1,2], k  = 1 , relationship= 'provider-to-customer')


    print(g.number_of_edges())
    print(len(tier_3))
    addprovider(list(tier_3), list(tier_3) , list_of_provider=  list(range(1,int(0.3*(len(tier_3)-1)))) , k  = 3 , relationship= 'peer-to-peer')
    addprovider(list(tier_2), list(tier_2) , list_of_provider=  list(range(0,int(0.6*(len(tier_2)-1)))), k  = -1 , relationship= 'peer-to-peer')
    addprovider(list(tier_1), list(tier_1) , list_of_provider= list(range(0,len(3)-1)), k  = -1 , relationship= 'peer-to-peer')


    print("Customers")

    d = dict(nx.degree(g))
    for i in d.keys():
        if d[i] <1:
            g.remove_node(i)
            print(i)

    print(g.number_of_edges() )
    print("^^^ Edges")
    print(g.number_of_nodes())
    stamp = str(g.number_of_nodes())+ "_" + str(int(time.time()))
    dir = '/home/asemwal/raw_data/experiments/graphs/'
    out = open(dir+'graph_'+   stamp ,'w')
    edges = list(g.edges())
    out.write("#Graph Properties\n")
    out.write("#Edges :" + str(g.number_of_edges())+"  \tNodes : " + str(g.number_of_nodes()) +"\n")
    out.write("#Tier1: "+ str(", ".join(tier_1)) +"\n")
    out.write("#Tier2: "+ str(", ".join(tier_2)) +"\n")
    out.write("#Tier3: "+ str(", ".join(tier_3)) +"\n")
    out.write("#\n")
    for e in edges:
        l = list()
        l.append(e[0])
        l.append(e[1])
        l.append(g.get_edge_data(e[0] , e[1])['relationship'])
        out.write("|".join(l)+"\n")

    out.close()

    out = open(dir+'prefixassoc_'+ stamp ,'w')
    for p in prefixassoc.keys():
        l = list()
        l.append(str(p))
        l.append(",".join(prefixassoc[p]))
        out.write("|".join(l)+"\n")

    out.close()
    return stamp
    
def testgraohgeneration(n = 10, size = 300):    
    dir = '/home/asemwal/raw_data/experiments/graphs/'     
    for i in range(0,n):
        timestamp = toygraphgenerator(size)
        ms.monitorselection(dir+ "graph_"+timestamp , timestamp)
        time.sleep(1)
