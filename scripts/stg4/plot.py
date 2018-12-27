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

file = open('/home/asemwal/raw_data/experiments/results/random_monitors','r')
l=str(file.readline()).strip()
i=0
d = dict()
files = dict()
while l != '':
    rec = l.split("|")
    print rec
    k = rec[0].split('_')[0]
    if k not in d.keys():
        d.update({k:[]})
    for i in range(1,len(rec)):
        d[k].append(float(rec[i]))
    l=str(file.readline()).strip()

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
y = []
l = False
y = []
for i in d.keys():
    y.append(float(i))
#y = [100,200,300,400,500,600]
y.sort()
for r in y:
        j = int(r)
        if l == False:
            label.append('Random-based Monitor Selection Performance')
        if True == True:    
            average.append(np.average(d[str(j)]))
            median.append(np.median(d[str(j)]))
            percentile25.append(np.percentile(d[str(j)],[25.])[0])
            percentile75.append(np.percentile(d[str(j)],[75.])[0])
            sdev0.append(average[-1]- np.std(d[str(j)]))
            sdev1.append(average[-1]+ np.std(d[str(j)]))
    
        
        l = True
#label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'k','g']
#color = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
#matplotlib.rcParams['axes.prop_cycle']
#plt.ylim((0,90))
#plt.xlim((0,0.9))
#fig, ax1 = plt.subplots()

#ax1.set_xlabel('Normalized Invisibility Score', fontsize=8)
#ax1.set_ylabel('Link Coverage', fontsize=8)
plt.xlabel('Graph Size', fontsize=8)
plt.ylabel('Link Coverage', fontsize=8)
#ax1.tick_params(axis='y' )
#ax2 = ax1.twinx()
#ax2.set_ylabel('Monitor Set Size', fontsize=8)
#ax2.tick_params(axis='y' )

for i in [0]:
#    y=  d.keys() 
    plt.plot( y,average ,color = color[i], label=label[i])
    plt.fill_between(y,sdev0,sdev1,color = color[i], alpha=0.25)
 
plt.legend(loc=0,fontsize=8)
#ax2.legend(loc=2,fontsize=8)


plt.savefig('randommonitor.pdf', format='pdf', dpi=5000)
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