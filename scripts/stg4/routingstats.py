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
            
    return linkmonset,linkset, pathmonset

def processfile(resultfile = None):
    simdir  = '/home/asemwal/thesis/bgp-python/data/simulator/'
    simdir  = '/home/asemwal/git/bgp-python/data/simulator/'
    in1 = open(simdir+ resultfile,'r')
    timestamp = "_".join(in1.name.split("/")[-1].split(".")[0].split("_")[-2:])
    j1 = in1.readline()
    in1.close()

    routing_table = json.loads(j1)
    linkmonset,linkset, pathmonset = aslinkset(set(routing_table.keys()), routing_table)
    return pathmonset, linkmonset, routing_table, len(linkset)
 
def stage1():
    mypath = '/home/asemwal/thesis/bgp-python/data/simulator/'
    mypath = '/home/asemwal/git/bgp-python/data/simulator/'
    mydir = '/home/asemwal/raw_data/experiments/results/'
    onlyfiles = [
                f for f in listdir(mypath) 
                if isfile(join(mypath, f)) and f.find("routing_table") > -1]
    for f in onlyfiles:
        timestamp = "_".join(f.split(".")[0].split("_")[-2:])
        out = open(mydir +'vplinks_'+ timestamp,'w')
        pathmonset, linkmonset, routing_table, lenlinks = processfile(f)
        counter = dict()
        for i in linkmonset.keys():
            counter.update({i:0})
            for j in linkmonset[i]:
                #print("{}->{}--{}".format(i,j[0],j[1]))
                counter[i]+=1
        out.write("Total Links: "+str(lenlinks)+'\n')
        for i in counter.keys():
            out.write(str(i)+"|"+ str(counter[i]) +'\n')
        out.flush()
        out.close()
        out = open(mydir +'vp_paths'+ timestamp,'w')
        out.write("Total Links: "+str(lenlinks/2)+'\n')
        for i in pathmonset.keys():
            out.write(
                str(i)+"|" + str(len(pathmonset[i]))+"|" +
                str(len(linkmonset[i])/2) +"|")
            comma = True
            count = 0
            for j in pathmonset[i]:
                if comma == True:
                    out.write(str(j) )
                    comma = False
                else:
                    out.write(', '+ str(j))
            out.write('\n')
        out.flush()
        out.close()
            #print("{}|{}|{}".format(timestamp,i,counter[i]))
        os.rename(mypath + f , mypath+'done/' + f)
        os.rename(
            mypath + 'insert_announcements_demo_'+timestamp+
            '.routing_state' , mypath+'done/' +
            'insert_announcements_demo_'+timestamp+ '.routing_state')
        os.rename(
            mypath + 'insert_announcements_demo_'+timestamp+
            '.AS_graph' , mypath+'done/' + 
            'insert_announcements_demo_'+timestamp+ '.AS_graph')
        
        #mons.greedylink(x, y, z)

stage1()

