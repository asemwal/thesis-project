# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 11:43:51 2018

@author: asemwal
"""
import json
import networkx as nx
import os
import numpy as np
from os import listdir
from os.path import isfile, join
import monitorselection as mons
import toygraph as tg
import time


def aslinkset(monset = None , routing_table = None):
    rt_monselect  = dict() 
    pfx_monselect = set()
    #path_monselect = set()
    linkset = set()
    for i in monset:
        if i.isdigit() == True:
            rt_monselect[i] = routing_table[i]
        
    pathmonset = dict()
    for m in rt_monselect.keys():
        pathmonset.update({m:set()})
        for i in rt_monselect[m]:
            if i.find("/") > -1:
                pfx_monselect.add(i)
                for j in range(0,len(rt_monselect[m][i])):
                    path = rt_monselect[m][str(i)][j]['path']
                    path.reverse()
                    #path_monselect.add(" ".join(path))
                    pathmonset[m].add(" ".join(path))
            
                    #print("{}:::{}->>{}\t{}".format(m,rt_monselect[m][i][j]['prefix']," ".join(path) , rt_monselect[m][str(i)][j]['LOCAL_PREFERENCE']))
            else:
                print(i)

    linkmonset = dict()                
    for p in pathmonset.keys():
        linkmonset.update({p:set()})
        for q in pathmonset[p]:
            ases = q.split(" ")
            for i in range(1, len(ases)):
                linkmonset[p].add((ases[i-1],ases[i]))
                linkmonset[p].add((ases[i],ases[i-1]))
                linkset.add( "|".join([ases[i-1],ases[i]]))
                linkset.add( "|".join([ases[i],ases[i-1]]))
            
    return pathmonset, linkmonset,linkset

def origionallinks(f):
    file = open(f , 'r')
    l = str(file.readline()).strip()
    g = nx.DiGraph()
    org_links = set()
    while l != "":
        if l.find("#") > -1:
            pass
        else:
            x = l.split("|")
            org_links.add((x[0].split("_")[1],x[1].split("_")[1]))
            g.add_edge(x[0].split("_")[1], x[1].split("_")[1], relationship= x[2])


        l = str(file.readline()).strip()
    return list(g.edges()), g

def visibility(monset = None , routing_table = None):
    rt_monselect  = dict() 
    pfx_monselect = set()
    path_monselect = set()
    for i in monset:
        rt_monselect[i] = routing_table[i]
        

    for m in monset:
        for i in rt_monselect[m]:
            if i.find("/") > -1:
                pfx_monselect.add(i)
                for j in range(0,len(rt_monselect[m][i])):
                    path = rt_monselect[m][str(i)][j]['path']
                    #path.reverse()
                    path_monselect.add(" ".join(path))
            
                    #print("{}:::{}->>{}\t{}".format(m,rt_monselect[m][i][j]['prefix']," ".join(path) , rt_monselect[m][str(i)][j]['LOCAL_PREFERENCE']))
            else:
                print(i)

    links = set()                
    for p in path_monselect:
        ases = p.split(" ")
        for i in range(1, len(ases)):
            links.add((ases[i-1],ases[i]))
            links.add((ases[i],ases[i-1]))
            
    return links
    
def processfile(resultfile = None):
    simdir  = '/home/asemwal/thesis/bgp-python/data/simulator/'
    simdir  = '/home/asemwal/git/bgp-python/data/simulator/'
    in1 = open(simdir+ resultfile,'r')
    timestamp = "_".join(in1.name.split("/")[-1].split(".")[0].split("_")[-2:])
    j1 = in1.readline()
    in1.close()

    routing_table = json.loads(j1)

    in1 = open('/home/asemwal/raw_data/experiments/graphs/monitors_'+ timestamp,'r')
    org_links, g = origionallinks('/home/asemwal/raw_data/experiments/graphs/done/graph_'+timestamp)
    is_monset  = set()
    is_monset1  = set()
    is_monset2  = set()
    d_monset = set()
    d_monset1 = set()
    d_monset2 = set()
    r_monset = set()
    r_monset1 = set()
    r_monset2 = set()
    r30_monset = set()
    r30_monset1 = set()
    r30_monset2 = set()
    l = str(in1.readline()).strip()
    while l != '':
        x = l.split(":")
        y = x[1].split(",") 
        if x[0] == 'is_monset':
            print "is_monset"
            ismonset = mons.newmonitorselection(g, '/home/asemwal/raw_data/experiments/graphs/done/graph_'+str(timestamp), version =0)
            ismonset1 = mons.newmonitorselection(g, '/home/asemwal/raw_data/experiments/graphs/done/graph_'+str(timestamp), version =1)
            ismonset2 = mons.newmonitorselection(g, '/home/asemwal/raw_data/experiments/graphs/done/graph_'+str(timestamp), version =2)
            for i in ismonset:
                if i.find("_")>-1:
                    is_monset.add(i.split("_")[1])   
                else:
                    is_monset.add(i)
            for i in ismonset1:
                if i.find("_")>-1:
                    is_monset1.add(i.split("_")[1])   
                else:
                    is_monset1.add(i)
            for i in ismonset2:
                if i.find("_")>-1:
                    is_monset2.add(i.split("_")[1])   
                else:
                    is_monset2.add(i)
        elif x[0] == 'd_monset':
            print "dmonset"
            dmonset = mons.degreebased(len(is_monset), dict(g.degree()))
            dmonset1 = mons.degreebased(len(is_monset1), dict(g.degree()))
            dmonset2 = mons.degreebased(len(is_monset2), dict(g.degree()))
            for i in dmonset:
                if i.find("_")>-1:
                    d_monset.add(i.split("_")[1])   
                else:
                    d_monset.add(i)
            for i in dmonset1:
                if i.find("_")>-1:
                    d_monset1.add(i.split("_")[1])   
                else:
                    d_monset1.add(i)
            for i in dmonset2:
                if i.find("_")>-1:
                    d_monset2.add(i.split("_")[1])   
                else:
                    d_monset2.add(i)
        elif x[0] == 'r_monset':
            rmonset = mons.randombased(len(is_monset), list(g.nodes()))
            rmonset1 = mons.randombased(len(is_monset1), list(g.nodes()))
            rmonset2 = mons.randombased(len(is_monset2), list(g.nodes()))
            for i in rmonset:
                if i.find("_")>-1:
                    r_monset.add(i.split("_")[1])   
                else:
                    r_monset.add(i)
            for i in rmonset1:
                if i.find("_")>-1:
                    r_monset1.add(i.split("_")[1])   
                else:
                    r_monset1.add(i)
                    
            for i in rmonset2:
                if i.find("_")>-1:
                    r_monset2.add(i.split("_")[1])   
                else:
                    r_monset2.add(i)

        elif x[0] == 'r30_monset':
            for i in y:
                r30_monset.add(i.split("_")[1])   
        l = str(in1.readline()).strip()
    



    #t_links = visibility(routing_table.keys(), routing_table)
    #d_links = visibility(d_monset , routing_table)
    is_links  = visibility(is_monset , routing_table)
    is_links1  = visibility(is_monset1 , routing_table)
    is_links2  = visibility(is_monset2 , routing_table)
    r_links  = visibility(r_monset , routing_table)
    r_links1  = visibility(r_monset1 , routing_table)
    r_links2  = visibility(r_monset2 , routing_table)
    d_links  = visibility(d_monset , routing_table)
    d_links1  = visibility(d_monset1 , routing_table)
    d_links2  = visibility(d_monset2 , routing_table)
    pathmonset, linkmonset, linkset = aslinkset(set(routing_table.keys()), routing_table)
    g_links, distribution = mons.greedylink(linkmonset, linkset, timestamp, len(d_monset))
    g_links1, distribution1 = mons.greedylink(linkmonset, linkset, timestamp, len(d_monset1))
    g_links2, distribution2 = mons.greedylink(linkmonset, linkset, timestamp, len(d_monset2))
    #g_links3, distribution3 = mons.greedylink3(linkmonset, linkset, timestamp, len(d_monset))
    #g_links, distribution = mons.greedylink3(linkmonset, linkset, timestamp, len(d_monset))
    dd_links, d_distribution = mons.degreelink(linkmonset, linkset, timestamp, len(d_monset), g)
    dd_links1, d_distribution1 = mons.degreelink(linkmonset, linkset, timestamp, len(d_monset1), g)
    dd_links2, d_distribution2 = mons.degreelink(linkmonset, linkset, timestamp, len(d_monset2), g)
    r30_monset = mons.randomlink( len(distribution.keys()) , g)
    r30_monset1 = mons.randomlink( len(distribution.keys()) , g)
    r30_monset2 = mons.randomlink( len(distribution.keys()) , g)
    r30_links  = visibility(r30_monset , routing_table)
    r30_links1  = visibility(r30_monset1 , routing_table)
    r30_links2  = visibility(r30_monset2 , routing_table)
    #return routing_table, len(org_links)
    out = open('/home/asemwal/raw_data/experiments/results/visibility_results5' , 'a')
    l = list()
    l.append(timestamp)
    l.append(str(len(d_monset)))
    l.append(str(len(is_monset1)))
    l.append(str(len(is_monset2)))
    l.append(str(len(org_links)))
    #l.append(str(len(t_links)))
    l.append(str(round(len(is_links)*100.0/len(linkset),4)))        
    l.append(str(round(len(is_links1)*100.0/len(linkset),4)))        
    l.append(str(round(len(is_links2)*100.0/len(linkset),4)))        
    l.append(str(round(g_links *100.0/len(linkset),4)))
    l.append(str(round(g_links1 *100.0/len(linkset),4)))
    l.append(str(round(g_links2 *100.0/len(linkset),4)))
    #l.append(str(round(g_links3 *100.0/len(linkset),4)))
    l.append(str(round(len(d_links)*100.0/len(linkset),4)))
    l.append(str(round(len(d_links1)*100.0/len(linkset),4)))
    l.append(str(round(len(d_links2)*100.0/len(linkset),4)))
    l.append(str(round(len(r_links)*100.0/len(linkset),4)))
    l.append(str(round(len(r_links1)*100.0/len(linkset),4)))
    l.append(str(round(len(r_links2)*100.0/len(linkset),4)))
    #l.append(str(round(len(r30_links)*100.0/len(linkset),4)))
    #l.append(str(len(is_links.difference(d_links))))
    #l.append(str(len(d_links.difference(is_links))))
    #l.append(str(len(is_links.difference(r_links))))
    #l.append(str(len(r_links.difference(is_links))))
    #l.append(str(len(is_links.difference(r30_links))))
    #l.append(str(len(r30_links.difference(is_links))))
    #l.append(str(len( (is_links.union(d_links)))))
    #l.append(str(len( (is_links.union(r_links)))))
    #l.append(str(len( (is_links.union(r30_links)))))
    #l.append(str(len( (is_links.union(r_links.union(d_links.union(r30_links)))))))
    out.write("|".join(l)+"\n")
    print("|".join(l))
    out.flush()
    out.close()
    #return routing_table, len(linkset)
    out = open('/home/asemwal/raw_data/experiments/results/distribution5_'+timestamp , 'w')
    for i in distribution.keys():
        out.write(str(i)+"|" + str(distribution[i])+ "|"+str(distribution[i])+ "|" +str(d_distribution[i]) +"\n")
    out.flush()
    out.close()
    out = open('/home/asemwal/raw_data/experiments/results/path_monset5_'+timestamp , 'w')
    for i in linkmonset.keys():
        code = ""
        if i in d_monset:
            code+= "M#"
        else:
            code+="N#"
        out.write(str(i)+"#")
        for j in linkmonset[i]:
            out.write(str(j[0])+ "|" +str(j[1]) +",")
        out.write("#" + code + str(len(linkmonset[i]))+'#'+ str(len(linkset))+ "\n")
    out.flush()
    out.close()
    #return linkmonset, linkset, timestamp
    return routing_table, len(linkset)

def randomdistribution(bgpdata =  None , timestamp = None, routing_table = None, lenlinks = None):
    graphDir = '/home/asemwal/raw_data/experiments/graphs/done/'    
    g = mons.generategraph(graphDir+'graph_'+timestamp )
    outfile1 = open(graphDir+'../../results/random_monitors5','a')
    i = 0 
    length = int(g.number_of_nodes()* 0.1)
    nodes = list(g.nodes())
    result = list()
    result.append(timestamp)
    while i < 10:
        i+=1
        monitors = mons.randombased(length , nodes)
        r_monset = set()
        for m in monitors:
            r_monset.add(m.split("_")[1])
        r_links = visibility( r_monset , routing_table)
        result.append(str(round(len(r_links)*100.0/lenlinks)))
    outfile1.write("|".join(result)+'\n')
    outfile1.close()
        
    
    
def stage1():
    mypath = '/home/asemwal/thesis/bgp-python/data/simulator/'
    mypath = '/home/asemwal/git/bgp-python/data/simulator/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.find("routing_table") > -1]
    for f in onlyfiles:
        routing_table, lenlinks = processfile(f)
        timestamp = "_".join(f.split(".")[0].split("_")[-2:])
        visibilitystats2(mypath+f, timestamp,routing_table,  lenlinks,'p2p')
        visibilitystats2(mypath+f, timestamp,routing_table,  lenlinks,'p2c')
        randomdistribution(mypath+f, timestamp,routing_table,  lenlinks)
        os.rename(mypath + f , mypath+'done/' + f)
        os.rename(mypath + 'insert_announcements_demo_'+timestamp+ '.routing_state' , mypath+'done/' + 'insert_announcements_demo_'+timestamp+ '.routing_state' )
        os.rename(mypath + 'insert_announcements_demo_'+timestamp+ '.AS_graph' , mypath+'done/' + 'insert_announcements_demo_'+timestamp+ '.AS_graph' )
        
        #mons.greedylink(x, y, z)
        
def visibilitystats(bgpdata =  None , timestamp = None, routing_table = None, lenlinks = None):
    graphDir = '/home/asemwal/raw_data/experiments/graphs/done/'    
    i = 0
    result = []
    result_mon = []
    outfile1 = open(graphDir+'../../results/impact_visibility5','a')
    outfile2 = open(graphDir+'../../results/impact_visibility_monsize5','a')
    outfile3 = open(graphDir+'../../results/impact_relations5','a')
    outfile4 = open(graphDir+'../../results/impact_relations_monsize5','a')
    while i < 1.0:
        g = mons.generategraph(graphDir+'graph_'+timestamp , i)
        monitor = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=0))
        monitor1 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=1))
        monitor2 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=2))
        print(monitor)
        h_monitor = set()
        h_monitor1 = set()
        h_monitor2 = set()
        d_monitor = set()
        d_monitor1 = set()
        d_monitor2 = set()
        for m in monitor:
            h_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            h_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            h_monitor2.add(str(m.split('_')[1]))
        monitor = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor1 = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor2 = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        for m in monitor:
            d_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            d_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            d_monitor2.add(str(m.split('_')[1]))
        h_links = visibility( h_monitor , routing_table)
        h_links1 = visibility( h_monitor1 , routing_table)
        h_links2 = visibility( h_monitor2 , routing_table)
        d_links = visibility( d_monitor , routing_table)
        d_links1 = visibility( d_monitor1 , routing_table)
        d_links2 = visibility( d_monitor2 , routing_table)
        result.append(timestamp)
        result.append(str(i)) 
        result.append(str(round(len(h_links)*100.0/lenlinks)))
        result.append(str(round(len(h_links1)*100.0/lenlinks)))
        result.append(str(round(len(h_links2)*100.0/lenlinks)))
        result.append(str(round(len(d_links)*100.0/lenlinks)))
        result.append(str(round(len(d_links1)*100.0/lenlinks)))
        result.append(str(round(len(d_links2)*100.0/lenlinks)))
        result_mon.append(timestamp)
        result_mon.append(str(i))
        result_mon.append(str(round(len(h_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor2)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor2)*100.0/g.number_of_nodes(),4)))
        outfile1.write("|".join(result)+'\n')
        outfile2.write("|".join(result_mon)+'\n')
        result = list()
        result_mon = list()
        g = mons.generategraph(graphDir+'graph_'+timestamp , i, True)
        monitor = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=0))
        monitor1 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp,version=1))
        monitor2 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=2))
        h_monitor = set()
        h_monitor1 = set()
        h_monitor2 = set()
        d_monitor = set()
        d_monitor1 = set()
        d_monitor2 = set()
        for m in monitor:
            h_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            h_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            h_monitor2.add(str(m.split('_')[1]))
        monitor = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor1 = set(mons.degreebased(len(h_monitor1), dict(g.degree())))
        monitor2 = set(mons.degreebased(len(h_monitor2), dict(g.degree())))
        for m in monitor:
            d_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            d_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            d_monitor2.add(str(m.split('_')[1]))
        h_links = visibility( h_monitor , routing_table)
        h_links1 = visibility( h_monitor1 , routing_table)
        h_links2 = visibility( h_monitor2 , routing_table)
        d_links = visibility( d_monitor , routing_table)
        d_links1 = visibility( d_monitor1 , routing_table)
        d_links2 = visibility( d_monitor2 , routing_table)
        result.append(timestamp)
        result.append(str(i)) 
        result.append(str(round(len(h_links)*100.0/lenlinks)))
        result.append(str(round(len(h_links1)*100.0/lenlinks)))
        result.append(str(round(len(h_links2)*100.0/lenlinks)))
        result.append(str(round(len(d_links)*100.0/lenlinks)))
        result.append(str(round(len(d_links1)*100.0/lenlinks)))
        result.append(str(round(len(d_links2)*100.0/lenlinks)))
        result_mon.append(timestamp)
        result_mon.append(str(i))
        result_mon.append(str(round(len(h_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor2)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor2)*100.0/g.number_of_nodes(),4)))
        outfile3.write("|".join(result)+'\n')
        outfile4.write("|".join(result_mon)+'\n')
        result = list()
        result_mon = list()
        i+= 0.1
    
    outfile1.close()
    outfile2.close()
    outfile3.close()
    outfile4.close()
    
    
def visibilitystats2(bgpdata =  None , timestamp = None, routing_table = None, lenlinks = None, key = 'p2c'):
    graphDir = '/home/asemwal/raw_data/experiments/graphs/done/'    
    i = 0
    result = []
    result_mon = []
    outfile1 = open(graphDir+'../../results/impact_visibility5'+key,'a')
    outfile2 = open(graphDir+'../../results/impact_visibility_monsize5'+key,'a')
    outfile3 = open(graphDir+'../../results/impact_relations5'+key,'a')
    outfile4 = open(graphDir+'../../results/impact_relations_monsize5'+key,'a')
    while i < 1.0:
        g = mons.generategraph(graphDir+'graph_'+timestamp , i, False,key)
        monitor = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=0))
        monitor1 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=1))
        monitor2 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=2))
        h_monitor = set()
        h_monitor1 = set()
        h_monitor2 = set()
        d_monitor = set()
        d_monitor1 = set()
        d_monitor2 = set()
        for m in monitor:
            h_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            h_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            h_monitor2.add(str(m.split('_')[1]))
        monitor = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor1 = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor2 = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        for m in monitor:
            d_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            d_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            d_monitor2.add(str(m.split('_')[1]))
        h_links = visibility( h_monitor , routing_table)
        h_links1 = visibility( h_monitor1 , routing_table)
        h_links2 = visibility( h_monitor2 , routing_table)
        d_links = visibility( d_monitor , routing_table)
        d_links1 = visibility( d_monitor1 , routing_table)
        d_links2 = visibility( d_monitor2 , routing_table)
        result.append(timestamp)
        result.append(str(i)) 
        result.append(str(round(len(h_links)*100.0/lenlinks)))
        result.append(str(round(len(h_links1)*100.0/lenlinks)))
        result.append(str(round(len(h_links2)*100.0/lenlinks)))
        result.append(str(round(len(d_links)*100.0/lenlinks)))
        result.append(str(round(len(d_links1)*100.0/lenlinks)))
        result.append(str(round(len(d_links2)*100.0/lenlinks)))
        result_mon.append(timestamp)
        result_mon.append(str(i))
        result_mon.append(str(round(len(h_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor2)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor2)*100.0/g.number_of_nodes(),4)))
        outfile1.write("|".join(result)+'\n')
        outfile2.write("|".join(result_mon)+'\n')
        result = list()
        result_mon = list()
        g = mons.generategraph(graphDir+'graph_'+timestamp , i, True, key)
        monitor = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=0))
        monitor1 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp,version=1))
        monitor2 = set(mons.newmonitorselection( g, graphFile= graphDir+'graph_'+timestamp, version=2))
        h_monitor = set()
        h_monitor1 = set()
        h_monitor2 = set()
        d_monitor = set()
        d_monitor1 = set()
        d_monitor2 = set()
        for m in monitor:
            h_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            h_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            h_monitor2.add(str(m.split('_')[1]))
        monitor = set(mons.degreebased(len(h_monitor), dict(g.degree())))
        monitor1 = set(mons.degreebased(len(h_monitor1), dict(g.degree())))
        monitor2 = set(mons.degreebased(len(h_monitor2), dict(g.degree())))
        for m in monitor:
            d_monitor.add(str(m.split('_')[1]))
        for m in monitor1:
            d_monitor1.add(str(m.split('_')[1]))
        for m in monitor2:
            d_monitor2.add(str(m.split('_')[1]))
        h_links = visibility( h_monitor , routing_table)
        h_links1 = visibility( h_monitor1 , routing_table)
        h_links2 = visibility( h_monitor2 , routing_table)
        d_links = visibility( d_monitor , routing_table)
        d_links1 = visibility( d_monitor1 , routing_table)
        d_links2 = visibility( d_monitor2 , routing_table)
        result.append(timestamp)
        result.append(str(i)) 
        result.append(str(round(len(h_links)*100.0/lenlinks)))
        result.append(str(round(len(h_links1)*100.0/lenlinks)))
        result.append(str(round(len(h_links2)*100.0/lenlinks)))
        result.append(str(round(len(d_links)*100.0/lenlinks)))
        result.append(str(round(len(d_links1)*100.0/lenlinks)))
        result.append(str(round(len(d_links2)*100.0/lenlinks)))
        result_mon.append(timestamp)
        result_mon.append(str(i))
        result_mon.append(str(round(len(h_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(h_monitor2)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor1)*100.0/g.number_of_nodes(),4)))
        result_mon.append(str(round(len(d_monitor2)*100.0/g.number_of_nodes(),4)))
        outfile3.write("|".join(result)+'\n')
        outfile4.write("|".join(result_mon)+'\n')
        result = list()
        result_mon = list()
        i+= 0.1
    
    outfile1.close()
    outfile2.close()
    outfile3.close()
    outfile4.close()
        
    

stage1()

