# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 12:22:10 2018

@author: asemwal
"""

import numpy as np
def generateStats():
    f = '/home/asemwal/raw_data/experiments/results/impact_relations_monsize'
    infile = open(f,'r')
    l = str(infile.readline()).strip()
    l = str(infile.readline()).strip()
    rec = dict()
    while l != '':
        recs = l.split("|")
        s= recs[0].split("_")[0]
        t= recs[1]
        if t not in rec.keys():
            rec.update({t:dict()})
        if s not in rec[t].keys():
            rec[t].update({s:{0:[],1:[]}})
    
        rec[t][s][0].append(float(recs[2]))
        rec[t][s][1].append(float(recs[3]))
        l = str(infile.readline()).strip()
        
    return rec

def generateStats2():
    f = '/home/asemwal/raw_data/experiments/results/visibility_results'
    infile = open(f,'r')
    l = str(infile.readline()).strip()
    l = str(infile.readline()).strip()
    rec = dict()
    while l != '':
        recs = l.split("|")
        s= recs[0].split("_")[0]
        if s not in rec.keys():
            rec.update({s:[]})
        rec[s].append(float(recs[1]))
        l = str(infile.readline()).strip()
        
    return rec


def printstats2():
    rec = generateStats2()
    header = True
    
    for i in rec.keys():
        a = np.average(rec[i])
        a = a*100.0/float(i)
        print("{}|{}".format(i, a))

def printstats():
    rec = generateStats()
    header = True
    
    for i in rec.keys():
        H= ''
        R1= i
        R2= i
        for j in rec[i].keys():
            H += "|Graph "+str(j)
            a = np.average(rec[i][j][0])
            b = np.average(rec[i][j][1])
            R1 += '|' + str(a)
            R2 += '|' + str(a)
            #print("{}|{}|{}|{}".format(i,float(j), float(a), float(b)))
        if header == True:
            print H
            header = False
        print R1
        #print R2