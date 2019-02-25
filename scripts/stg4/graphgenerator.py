# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 22:26:04 2019

@author: asemwal
"""

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
import random


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
            
def xyz():
    D=dict()
    for i in range(1,No+1):
        x = list(np.random.choice(list(range(2,len(p)+2)), 1, p=p, replace = False))
            #x =  rand.randint(2,No-1)
        D[i] = int(beta*(x[0]**-alpha))
        counter+=1
                


def addprovider2(customer = None , provider = None, minmaxD = (), k =1, relationship = 'provider-to-customer' ):
    global g
    multi_customer = dict()
    for i in customer:
        x = random.randint(minmaxD[0],minmaxD[1])
        r=  int((x**-1.7)*minmaxD[1])+1
        multi_customer[i]=r

    multi_provider= dict()
    for i in provider:
        x = random.randint(minmaxD[0],minmaxD[1])
        r=  int((x**-1.7)*minmaxD[1])+3
        print r
        multi_provider[i]=r


    for c in customer:
        prov_set = list()
        for mp_keys in multi_provider.keys():
            #print mp_keys+"|"+str(multi_provider[mp_keys])
            if multi_provider[mp_keys] > 0 and c != mp_keys:
                #print "here"
                prov_set.append(mp_keys)
        prov_prob = [1.0]*len(prov_set)
        prov_prob /= np.sum(prov_prob)
        #print prov_prob
        #print prov_set
        prov =  np.random.choice(prov_set, 1, p=prov_prob,replace = False)
        #print(p_count)
        edges = list(g.edges())
        if (prov,c) not in edges:
            g.add_edge(prov[0],c , relationship = relationship)
            g.add_edge(c,prov[0] , relationship = inverselink(relationship))
            multi_customer[c]-=1
            multi_provider[prov[0]]-=1
            if multi_customer[c] ==0:
                multi_customer.pop(c)
            if multi_provider[prov[0]] ==0:
                multi_provider.pop(prov[0])            

def addprovider3(customer = None , provider = None, minmaxD = (), k =1, relationship = 'provider-to-customer' ):
    global g,D
    keys = dict()
    keys['provider-to-customer'] = 'p2c'
    keys['customer-to-provider'] = 'c2p'
    keys['peer-to-peer'] = 'p2p'
    keys['sibling-to-sibling'] = 's2s'
    dmap = dict(ms.degreemap(g))
    cust_set = list()
    for i in customer:
        if dmap[i][ keys[ inverselink(relationship)]]  < D[i][inverselink(relationship)]:
            cust_set.append(i)
            
    prov_set = list()
    for i in provider:
                #if dmap[i]['p2p']+dmap[i]['p2c']+dmap[i]['c2p']+dmap[i]['s2s'] < D[i]['peer-to-peer']+D[i]['provider-to-customer']+D[i]['customer-to-provider']+D[i]['sibling-to-sibling'] :
        if dmap[i][ keys[ (relationship)]]  < D[i][(relationship)]:
            prov_set.append(i)
    for c in cust_set:
        x= random.randint(minmaxD[0],minmaxD[1])
        for j in range(0,x):
            if c not in cust_set:
                break
            degreeSum =0
            degreeval = list(dict(g.degree()).values())
            degreeSum = np.sum(degreeval)
            prov_prob = []
            for i in prov_set:
                #degreeSum+= dmap[i][keys[(relationship)]]
                prov_prob.append(dmap[i][keys[ (relationship)]])    
            if np.sum(degreeSum )==0:
                prov_prob=[1.0]* len(prov_set) 
            prov_prob  /= np.sum(prov_prob)
            stuck  = 0
            while True== True:
                #print prov_set
                #print prov_prob
                if len(prov_set) ==0:
                    print "breaking"
                    break
                prov = np.random.choice(prov_set, 1, p=prov_prob,replace = False)
                edges = list(g.edges())
                if (prov[0],i) not in edges:
                    stuck = 0
                    g.add_edge(prov[0],c , relationship = relationship)
                    g.add_edge(c,prov[0] , relationship = inverselink(relationship))
                    D[prov[0]][ inverselink(relationship)]-=1
                    D[c][ (relationship)]-=1
                    if D[c][(relationship)] <=0:
                        cust_set.remove(c)
                    if D[prov[0]][ inverselink(relationship) ] <=0:
                        prov_set.remove(prov[0])

                    break
                else:
                    stuck+=1
                    if stuck > 2:
                        print "breaking due to failure"
                        break
                    print "failed... searching again"
        
        
        
        
        
def addprovider(customer = None , provider = None, minmaxD = (), k =1, relationship = 'provider-to-customer' ):
    global g,D
    dmap = ms.degreemap(g)
    multi_provider = list()
    for i in range(minmaxD[0],minmaxD[1]):
        x = random.randint(minmaxD[0]+1,minmaxD[1]+1)
        r=  -((x**-1.7)*minmaxD[1])
        r=1.0
        multi_provider.append(r)
            
    multi_provider /= np.sum(multi_provider)
    multi_provider = list(multi_provider)
    #print(multi_provider)
    for c in customer:
        p_count =  np.random.choice(range(minmaxD[0],minmaxD[1]), 1, p=multi_provider,replace = False)
        #print(p_count)
        removed = False
        index = -1
        temp = 0.0
        if c in provider:
            index = provider.index(c)
            provider.remove(c)
            
            removed = True
        degree = dict(g.degree())
        D=0
        prob = []
        for i in degree.keys():
            D+=degree[i]
        for i in provider:
            if D == 0:
                prob.append(1.0)
            else:
                prob.append(degree[i]/float(D))
#        prob = [1.0] * len(provider)
        prob /= np.sum(prob)
        prob = list(prob)
        try:
            providers = list(np.random.choice(provider, p_count[0], p=prob, replace = False))
        except ValueError:
            prob = [1.0]*len(provider)
            prob/=np.sum(prob)
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
    global g,D
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
    D = dict()    
    alpha_p2c=-0.9790423303
    alpha_p2p=-1.1053266485
    alpha_c2p=-3.3803525079
    beta_p2p = 6000
    beta_p2c=6000
    beta_c2p = 40
    
    
    
    listx= list(range(1,6000)) #p2p
    listy = list(range(1,40)) #c2p
    listz = list(range(1,6000)) #s2s
    probx = [1.0]*len(listx)
    proby = [1.0]*len(listy)
    probz = [1.0]*len(listz)
    probx /= np.sum(probx)
    proby /= np.sum(proby)
    probz /= np.sum(probz)
    for i in tier_1:
        D[i] = dict()
        x = np.random.choice( listx, 1, p=probx, replace=False)
        y = np.random.choice( listy, 1, p=proby, replace=False)
        z = np.random.choice( listz, 1, p=probz, replace=False)
        D[i]['peer-to-peer']  = beta_p2p*(x[0]**alpha_p2p)
        D[i]['customer-to-provider']  = beta_c2p*(y[0]**alpha_c2p)
        D[i]['provider-to-customer']  = beta_p2c*(z[0]**alpha_p2c)
        D[i]['sibling-to-sibling']  = 0

    print("done")
    addprovider3(list(tier_1), list(tier_1) , minmaxD= (len(tier_1)-1,len(tier_1)), k  = -1 , relationship= 'peer-to-peer')
    print("done")
    
    g.add_nodes_from(tier_2)
    listx= list(range(1,6000)) #p2p
    listy = list(range(1,40)) #c2p
    listz = list(range(1,6000)) #s2s
    probx = [1.0]*len(listx)
    proby = [1.0]*len(listy)
    probz = [1.0]*len(listz)
    probx /= np.sum(probx)
    proby /= np.sum(proby)
    probz /= np.sum(probz)
    for i in tier_2:
        D[i] = dict()
        x = np.random.choice( listx, 1, p=probx, replace=False)
        y = np.random.choice( listy, 1, p=proby, replace=False)
        z = np.random.choice( listz, 1, p=probz, replace=False)
        D[i]['peer-to-peer']  = beta_p2p*(x[0]**alpha_p2p)
        D[i]['customer-to-provider']  = beta_c2p*(y[0]**alpha_c2p)
        D[i]['provider-to-customer']  = beta_p2c*(z[0]**alpha_p2c)
        D[i]['sibling-to-sibling']  = 0
    
    print("done")
    
    g.add_nodes_from(tier_3)
    listx= list(range(1,6000)) #p2p
    listy = list(range(1,40)) #c2p
    listz = list(range(1,6000)) #s2s
    probx = [1.0]*len(listx)
    proby = [1.0]*len(listy)
    probz = [1.0]*len(listz)
    probx /= np.sum(probx)
    proby /= np.sum(proby)
    probz /= np.sum(probz)
#    for i in tier_3:
#        D[i] = dict()
#        x = np.random.choice( listx, 1, p=probx, replace=False)
#        y = np.random.choice( listy, 1, p=proby, replace=False)
#        z = np.random.choice( listz, 1, p=probz, replace=False)
#        D[i]['peer-to-peer']  = beta_p2p*(x[0]**alpha_p2p)
#        D[i]['customer-to-provider']  = beta_c2p*(y[0]**alpha_c2p)
#        D[i]['provider-to-customer']  = beta_p2c*(z[0]**alpha_p2c)
#        D[i]['sibling-to-sibling']  = 0
    
    print("done")
    
    g.add_nodes_from(tier_4)
    listx= list(range(1,6000)) #p2p
    listy = list(range(1,40)) #c2p
    listz = list(range(1,6000)) #s2s
    probx = [1.0]*len(listx)
    proby = [1.0]*len(listy)
    probz = [1.0]*len(listz)
    probx /= np.sum(probx)
    proby /= np.sum(proby)
    probz /= np.sum(probz)
#    for i in tier_4:
#        D[i] = dict()
#        x = np.random.choice( listx, 1, p=probx, replace=False)
#        y = np.random.choice( listy, 1, p=proby, replace=False)
#        z = np.random.choice( listz, 1, p=probz, replace=False)
#        D[i]['peer-to-peer']  = beta_p2p*(x[0]**alpha_p2p)
#        D[i]['customer-to-provider']  = beta_c2p*(y[0]**alpha_c2p)
#        D[i]['provider-to-customer']  = beta_p2c*(z[0]**alpha_p2c)
#        D[i]['sibling-to-sibling']  = 0

    print("done4")
    
    addprovider3(list(tier_2), list(tier_2) , minmaxD= (int(0.5*T2),int(0.7*T2)), k  = -1 , relationship= 'peer-to-peer')
    print("done")
    #addprovider3(list(tier_3), list(tier_3) , minmaxD= (int(0.3*T3),int(0.5*T3)), k  = 3 , relationship= 'peer-to-peer')
    print("done")
    
    #addprovider3(list(tier_2), list(tier_1) , minmaxD= (1,3), k  = 1 , relationship= 'provider-to-customer')
    print("done")
    #addprovider3(list(tier_3), list(tier_2) , minmaxD= (2,7), k  = 2 , relationship= 'provider-to-customer')
    print("done")
    #addprovider3(list(tier_3), list(tier_1) , minmaxD= (1,3), k  = 4 , relationship= 'provider-to-customer')
    print("done")
    #addprovider3(list(tier_4), list(tier_3) , minmaxD= (1,3), k  = 5 , relationship= 'provider-to-customer')
    print("done")
    #addprovider3(list(tier_4), list(tier_2) , minmaxD= (1,3) , k  = 4 , relationship= 'provider-to-customer')
    print("done")
    

    #print(len(tier_3))
    
    #prefixowners = set()
    #prefixowners.update(prefixowners.union(set(tier_4 )))
    #prefixassoc = prefixassociation(list(prefixowners) , [1 , 2] , k = 1)
    

    d = dict(nx.degree(g))
    for i in d.keys():
        if d[i] <1:
            g.remove_node(i)
            #print(i)

    print(g.number_of_edges() )
    print("^^^ Edges^^^")
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

#    out = open(dir+'prefixassoc_'+ stamp ,'w')
#    for p in prefixassoc.keys():
#        l = list()
#        l.append(str(p))
#        l.append(",".join(prefixassoc[p]))
#        out.write("|".join(l)+"\n")
#
#    out.close()
    return stamp
    
def testgraohgeneration(n = 1, size = 62775):    
    dir = '/home/asemwal/raw_data/experiments/graphs/'     
    for i in range(0,n):
        timestamp = toygraphgenerator(size)
        #ms.monitorselection(dir+ "graph_"+timestamp , timestamp)
        time.sleep(1)
