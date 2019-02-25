# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
gname='p2p'
degree = dict()
peering= dict()
monset= dict()
average = dict()
median = dict()
percentile25 = dict()
percentile75 = dict()
sdev0 = dict()
sdev1 = dict()
y = [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
keys=[100,200,300,400,500,600]
for i in keys:
    degree[i] = dict()
    peering[i] = dict()
    average[i]=dict()
    median[i]=dict()
    percentile25[i]=dict()
    percentile75[i]=dict()
    sdev0[i]=dict()
    sdev1[i]=dict()
    for j in y:
        degree[i][j]=[[],[],[]]
        peering[i][j]=[[],[],[]]
        average[i][j]=[]
        median[i][j]=[]
        percentile25[i][j]=[]
        percentile75[i][j]=[ ]
        sdev0[i][j] =[ ]
        sdev1[i][j]=[ ]
        
file = open('/home/asemwal/raw_data/experiments/results/impact_visibility5'+gname,'r')
l=str(file.readline()).strip()
p=2
d=5
while l != '':
    rec = l.split("|")
    print rec
    i = int(rec[0].split('_')[0])
    j=float(rec[1])
    k=0
    peering[i][j][k].append(float(rec[p+k]))
    k+=1
    peering[i][j][k].append(float(rec[p+k]))
    k+=1
    peering[i][j][k].append(float(rec[p+k]))
    k=0
    degree[i][j][k].append(float(rec[d+k]))
    k+=1
    degree[i][j][k].append(float(rec[d+k]))
    k+=1
    degree[i][j][k].append(float(rec[d+k]))
    l=str(file.readline()).strip()

label = []

l = False
y.remove(1.0)
for i in keys:
    for j in y:
        average[i][j].append(list((np.average(degree[i][j], axis=1))))
        average[i][j].append(list((np.average(peering[i][j], axis=1))))
        
        median[i][j].append(list((np.average(degree[i][j], axis=1))))
        median[i][j].append(list((np.average(peering[i][j], axis=1))))
        
        percentile25[i][j].append(list(np.percentile(degree[i][j], [25.],axis=1))[0])
        percentile25[i][j].append(list(np.percentile(peering[i][j], [25.],axis=1))[0])

        percentile75[i][j].append(list(np.percentile(degree[i][j], [75.],axis=1))[0])
        percentile75[i][j].append(list(np.percentile(peering[i][j], [75.],axis=1))[0])

        sdev0[i][j].append(list(np.average(degree[i][j],axis=1)-np.std(degree[i][j],axis=1)))
        sdev0[i][j].append(list(np.average(peering[i][j],axis=1)-np.std(peering[i][j],axis=1)))
    
        sdev1[i][j].append(list(np.average(degree[i][j],axis=1)+np.std(degree[i][j],axis=1)))
        sdev1[i][j].append(list(np.average(peering[i][j],axis=1)+np.std(peering[i][j],axis=1)))
  
label = ['Basic version', 'Refined version', 'Final version']

#label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
color = ['r', 'b', 'g', 'c', 'm', 'y', 'k', 'k','g']
#color = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
#matplotlib.rcParams['axes.prop_cycle']
#fig, ax1 = plt.subplots()

#ax1.set_xlabel('Normalized Invisibility Score', fontsize=8)
#ax1.set_ylabel('Link Coverage', fontsize=8)
#ax1.tick_params(axis='y' )
#ax2 = ax1.twinx()
#ax2.set_ylabel('Monitor Set Size', fontsize=8)
#ax2.tick_params(axis='y' )
for i in keys:
    for k in [0,1,2]:
        x=[]
        x1=[]
        x2=[]
        plt.ylim((50,95))
        plt.xlim((0,0.9))
        plt.xlabel('Removed link (normalized)', fontsize=16)
        plt.ylabel('Link coverage', fontsize=16)
        for j in y:
            x.append(average[i][j][1][k])
            x1.append(sdev0[i][j][1][k])
            x2.append(sdev1[i][j][1][k])
        #print x
        plt.plot(y,x ,color = color[k], label=label[k], lw=3)
        plt.fill_between(y,x1,x2,color = color[k], alpha=0.25)
    plt.legend(loc=0,fontsize=14)
    plt.savefig('visibilityimpact_'+str(i)+gname+'.pdf', format='pdf', dpi=5000)
    plt.show()