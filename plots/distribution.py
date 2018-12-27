# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
avgn = 1; nepisodes = 250
data = range(0,1000,1)
data = np.load('/home/asemwal/Documents/1k5r_10_250_400_10_1_25.npy')
degree = []
peering= []
greedy = []
random= []
y = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
monset = []

file = open('/home/asemwal/raw_data/experiments/results/impact_visibility','r')
l=str(file.readline()).strip()
l=str(file.readline()).strip()
i=0
d = dict()
files = dict()
while l != '':
    rec = l.split("|")
    print rec
    k = rec[0].split('_')[0]
    k = rec[0]
    if k not in d.keys():
        files.update({k:{}})
    l=str(file.readline()).strip()
resDir = '/home/asemwal/raw_data/experiments/results/distribution_'
for fname in files.keys():
    file = open(resDir+fname,'r')
    l = str(file.readline()).strip()  
    x=fname.split("_")[0]
    while l != '':
        rec = l.split("|")
        k = rec[0] 
        if x not in d.keys():
            d.update({x:{}})
        if k not in d[x].keys():
            d[x].update({k:[[],[]]})
        d[x][k][0].append(float(rec[1]))
        d[x][k][1].append(float(rec[2]))
        l = str(file.readline()).strip() 
    file.close()
    
data = []
a=0
average = [ ]
median = [ ]
percentile25 = [ ]
percentile75 = [ ]
sdev0 = [ ]
sdev1 = [ ]

average1 = [ ]
median1 = [ ]
percentile251 = [ ]
percentile751 = [ ]
sdev01 = [ ]
sdev11 = [ ]

label = []
label1 = []
for j in d.keys():
    
    average.append([])
    median.append([])
    percentile25.append([])
    percentile75.append([])
    sdev0.append([])
    sdev1.append([])
    
    average1.append([])
    median1.append([])
    percentile251.append([])
    percentile751.append([])
    sdev01.append([])
    sdev11.append([])
l = False
for i in range(1,250):
    a=0
    for j in d.keys():
        if l == False:
            label.append('Graph of Size '+str(j))
        if str(i) in d[j].keys():    
            average[a].append(np.average(d[j][str(i)][0]))
            median[a].append(np.median(d[j][str(i)][0]))
            percentile25[a].append(np.percentile(d[j][str(i)][0],[25.])[0])
            percentile75[a].append(np.percentile(d[j][str(i)][0],[75.])[0])
            sdev0[a].append(average[a][-1]- np.std(d[j][str(i)][0]))
            sdev1[a].append(average[a][-1]+ np.std(d[j][str(i)][0]))

            average1[a].append(np.average(d[j][str(i)][1]))
            median1[a].append(np.median(d[j][str(i)][1]))
            percentile251[a].append(np.percentile(d[j][str(i)][1],[25.])[0])
            percentile751[a].append(np.percentile(d[j][str(i)][1],[75.])[0])
            sdev01[a].append(average1[a][-1]- np.std(d[j][str(i)][1]))
            sdev11[a].append(average1[a][-1]+ np.std(d[j][str(i)][1]))

        
        a+=1
    l = True
#label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'k','g']
#color = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
#matplotlib.rcParams['axes.prop_cycle']
#plt.ylim((0,90))
#plt.xlim((0,0.9))
y = range(1,100)
#fig, ax1 = plt.subplots()

#ax1.set_xlabel('Normalized Invisibility Score', fontsize=8)
#ax1.set_ylabel('Link Coverage', fontsize=8)
plt.xlabel('Number of Monitors', fontsize=16)
plt.ylabel('Link Coverage', fontsize=16)
#ax1.tick_params(axis='y' )
#ax2 = ax1.twinx()
#ax2.set_ylabel('Monitor Set Size', fontsize=8)
#ax2.tick_params(axis='y' )
for i in [5,0,4,3,8,2]:
    y=list(range(1,len(average[i])+1))
    plt.plot(y,average[i] ,color = color[i], label=label[i],lw=3)
    plt.fill_between(y,sdev0[i],sdev1[i],color = color[i], alpha=0.25)
 
plt.legend(loc=4,fontsize=16)
#ax2.legend(loc=2,fontsize=8)


plt.savefig('greedydistribution.pdf', format='pdf', dpi=5000)
plt.show()
"""
plt.plot(y,average,lw=2)
plt.plot(y,average1,lw=2)
#plt.fill_between(y,percentile25,percentile75,alpha=0.25)
plt.fill_between(y,sdev0,sdev1,alpha=0.25)
plt.fill_between(y,sdev01,sdev11,alpha=0.25)


d= np.array(degree)
r= np.array(random)
g= np.array(greedy)
p= np.array(peering)
yt = []
for i in range(0,10):
    yt.append(100)
for i in range(0,10):
    yt.append(200)

y = np.array(yt)
average=[]
median=[]
percentile25=[]
percentile75=[]
sdev0 =[]
sdev1=[]
average.append(np.average(d[0:10]))
sdev0.append(average[-1]- np.std(d[0:10]))
sdev1.append(average[-1]+ np.std(d[0:10]))
median.append(np.average(d[0:10]))
percentile25.append(np.percentile(d[0:10],[25.])[0])
percentile75.append(np.percentile(d[0:10],[75.])[0])
average.append(np.average(d[10:20]))
sdev0.append(average[-1]- np.std(d[10:20]))
sdev1.append(average[-1]+ np.std(d[10:20]))
median.append(np.average(d[10:20]))
percentile25.append(np.percentile(d[10:20],[25.])[0])
percentile75.append(np.percentile(d[10:20],[75.])[0])

d= np.array(peering)
average1=[]
median1=[]
percentile251=[]
percentile751=[]
sdev01 =[]
sdev11=[]
average1.append(np.average(d[0:10]))
sdev01.append(average1[-1]- np.std(d[0:10]))
sdev11.append(average1[-1]+ np.std(d[0:10]))
median1.append(np.average(d[0:10]))
percentile251.append(np.percentile(d[0:10],[25.])[0])
percentile751.append(np.percentile(d[0:10],[75.])[0])
average1.append(np.average(d[10:20]))
sdev01.append(average1[-1]- np.std(d[10:20]))
sdev11.append(average1[-1]+ np.std(d[10:20]))
median1.append(np.average(d[10:20]))
percentile251.append(np.percentile(d[10:20],[25.])[0])
percentile751.append(np.percentile(d[10:20],[75.])[0])
y = [100.,150.]
plt.plot(y,average,lw=2)
plt.plot(y,average1,lw=2)
#plt.fill_between(y,percentile25,percentile75,alpha=0.25)
plt.fill_between(y,sdev0,sdev1,alpha=0.25)
plt.fill_between(y,sdev01,sdev11,alpha=0.25)
plt.legend(['degree based', 'peering-based' ])
plt.xlabel('Graph Size', fontsize=14)
plt.ylabel('Link Coverage', fontsize=14)
plt.show()
"""