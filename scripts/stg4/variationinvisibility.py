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
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
    while len(sorted_x ) > 0:
        r = sorted_x.pop(-1)
        if r[1] > threshold:
            vp.append(r[0])
            visible_links = visible_links.union(copy_monitor[r[0]])
            if len(vp) == monsetlen:
                vp_copy = vp_copy.union(visible_links)
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
    return len(vp_copy)




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
            
    return linkmonset,linkset

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
            org_links.add((x[0],x[1]))


        l = str(file.readline()).strip()
    return org_links

def visibility(monset = None , routing_table = None):
    rt_monselect  = dict() 
    pfx_monselect = set()
    path_monselect = set()
    newmonset = set()
    for i in monset:
        if i.find("T") >-1:
            newmonset.add(i.split("_")[1])
            rt_monselect[i.split("_")[1]] = routing_table[i.split("_")[1]]
        else:
            newmonset.add(i)
            rt_monselect[i] = routing_table[i]

    for m in newmonset:
        for i in rt_monselect[m]:
            if i.find("/") > -1:
                pfx_monselect.add(i)
                for j in range(0,len(rt_monselect[m][i])):
                    path = rt_monselect[m][str(i)][j]['path']
                    path.reverse()
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
    os.rename(simdir + resultfile , simdir+'done/' + resultfile)
    os.rename(simdir + 'insert_announcements_demo_'+timestamp+ '.routing_state' , simdir+'done/' + 'insert_announcements_demo_'+timestamp+ '.routing_state' )
    os.rename(simdir + 'insert_announcements_demo_'+timestamp+ '.AS_graph' , simdir+'done/' + 'insert_announcements_demo_'+timestamp+ '.AS_graph' )

    routing_table = json.loads(j1)

    in1 = open('/home/asemwal/raw_data/experiments/graphs/monitors_'+ timestamp,'r')
    is_monset  = set()
    d_monset = set()
    r_monset = set()
    l = str(in1.readline()).strip()
    while l != '':
        x = l.split(":")
        y = x[1].split(",") 
        g = mons.generategraph3('/home/asemwal/raw_data/experiments/graphs/done/graph_'+str(timestamp))
        if x[0] == 'is_monset':
            ismonset = mons.newmonitorselection(g, '/home/asemwal/raw_data/experiments/graphs/done/graph_'+str(timestamp))
            print ismonset
            for i in y:
                is_monset.add(i)    
        elif x[0] == 'd_monset':
            dmonset = mons.degreebased(len(ismonset), dict(g.degree()))
            for i in y:
                d_monset.add(i)
        elif x[0] == 'r_monset':
            rmonset = mons.randombased(len(ismonset), list(g.nodes()))
            for i in y:
                r_monset.add(i)
        l = str(in1.readline()).strip()
    



    org_links = origionallinks('/home/asemwal/raw_data/experiments/graphs/done/graph_'+timestamp)
    #t_links = visibility(routing_table.keys(), routing_table)
    d_links = visibility(dmonset , routing_table)
    is_links  = visibility(ismonset , routing_table)
    r_links  = visibility(rmonset , routing_table)
    linkmonset, linkset = aslinkset(set(routing_table.keys()), routing_table)
    print linkmonset.keys()
    g_links, var_gr = mons.greedylink(linkmonset, linkset, timestamp, len(ismonset))
    print var_gr
    #d_links, var_d = mons.degreelink(linkmonset, linkset, timestamp, len(ismonset))
    out = open('/home/asemwal/raw_data/experiments/results/visibility_results_latest_10jan' , 'a')
    l = list()
    l.append(timestamp)
    l.append(str(len(ismonset)))
    l.append(str(len(org_links)))
    #l.append(str(len(t_links)))
    l.append(str(len(is_links)))        
    l.append(str(g_links))
    l.append(str(len(d_links)))            
    l.append(str(len(r_links)))
    #l.append(str(len(is_links.difference(d_links))))
    #l.append(str(len(d_links.difference(is_links))))
    #l.append(str(len(is_links.difference(r_links))))
    #l.append(str(len(r_links.difference(is_links))))
    #l.append(str(len( (is_links.union(d_links)))))
    #l.append(str(len( (is_links.union(r_links)))))
    #l.append(str(len( (is_links.union(r_links.union(d_links))))))
    out.write("|".join(l)+"\n")
    print("|".join(l))
    out.flush()
    out.close()
    #return linkmonset, linkset, timestamp
    
def stage1():
    mypath = '/home/asemwal/thesis/bgp-python/data/simulator/'
    mypath = '/home/asemwal/git/bgp-python/data/simulator/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.find("routing_table") > -1]
    for f in onlyfiles:
        processfile(f)
        #mons.greedylink(x, y, z)

stage1()

