# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 00:34:00 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""

import numpy as np
import matplotlib.pyplot as plt

avgn = 1; nepisodes = 250
data = range(0,1000,1)
data = np.load('/home/asemwal/Documents/1k5r_10_250_400_10_1_25.npy')
degree = []
peering= []
greedy = []
random= []
y = []
monset = []

file = open('/home/asemwal/raw_data/experiments/plotdata.csv','r')
l=str(file.readline()).strip()
l=str(file.readline()).strip()
i=0
while l != '':
    rec = l.split("|")
    print rec
    if rec[-1] == '1':
        degree.append([])
        peering.append([])
        greedy.append([])
        random.append([])
        monset.append([])
        y.append(int(rec[8]))
    monset[-1].append((float(rec[1])*100/y[-1]))
    greedy[-1].append(float(rec[3]))
    peering[-1].append(float(rec[4]))
    degree[-1].append(float(rec[5]))
    random[-1].append(float(rec[6]))
    
    l=str(file.readline()).strip()
a=0
average = [[],[],[],[],[]]
median = [[],[],[],[],[]]
percentile25 = [[],[],[],[],[]]
percentile75 = [[],[],[],[],[]]
sdev0 = [[],[],[],[],[]]
sdev1 = [[],[],[],[],[]]

for i in y:
    average[0].append(np.average(greedy[a]))
    average[1].append(np.average(peering[a]))
    average[2].append(np.average(degree[a]))
    average[3].append(np.average(random[a]))
    average[4].append(np.average(monset[a]))
    
    median[0].append(np.median(greedy[a]))
    median[1].append(np.median(peering[a]))
    median[2].append(np.median(degree[a]))
    median[3].append(np.median(random[a]))
    median[4].append(np.median(monset[a]))
    
    percentile25[0].append(np.percentile(greedy[a],[25.])[0])
    percentile25[1].append(np.percentile(peering[a],[25.])[0])
    percentile25[2].append(np.percentile(degree[a],[25.])[0])
    percentile25[3].append(np.percentile(random[a],[25.])[0])
    percentile25[4].append(np.percentile(monset[a],[25.])[0])
    
    percentile75[0].append(np.percentile(greedy[a],[75.])[0])
    percentile75[1].append(np.percentile(peering[a],[75.])[0])
    percentile75[2].append(np.percentile(degree[a],[75.])[0])
    percentile75[3].append(np.percentile(random[a],[75.])[0])
    percentile75[4].append(np.percentile(monset[a],[75.])[0])
    
    sdev0[0].append(average[0][-1]- np.std(greedy[a]))
    sdev0[1].append(average[1][-1]- np.std(peering[a]))
    sdev0[2].append(average[2][-1]- np.std(degree[a]))
    sdev0[3].append(average[3][-1]- np.std(random[a]))
    sdev0[4].append(average[4][-1]- np.std(monset[a]))
    
    sdev1[0].append(average[0][-1]+ np.std(greedy[a]))
    sdev1[1].append(average[1][-1]+ np.std(peering[a]))
    sdev1[2].append(average[2][-1]+ np.std(degree[a]))
    sdev1[3].append(average[3][-1]+ np.std(random[a]))
    sdev1[4].append(average[4][-1]+ np.std(monset[a]))
    
    a+=1
label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
color = ['g','b','m','r','c']
fig, ax1 = plt.subplots()

ax1.set_ylim((58,105))
ax1.set_xlabel('Graph Size', fontsize=16)
ax1.set_ylabel('Link Coverage', fontsize=16)
ax1.tick_params(axis='y' )

ax2 = ax1.twinx()
ax2.set_ylim((3,18))

ax2.set_ylabel('Monitor Set Size', fontsize=16)
ax2.tick_params(axis='y' )

ax1.plot(y,average[0],color[0],label= label[0],lw=3 )
ax1.plot(y,average[1],color[1],label= label[1],lw=3)
ax1.plot(y,average[2],color[2],label=label[2],lw=3)
ax1.plot(y,average[3],color[3],label=label[3],lw=3)
ax2.plot(y,average[4],color[4],label=label[4],lw=3)
ax1.fill_between(y,sdev0[0],sdev1[0],color = color[0], alpha=0.25)
ax1.fill_between(y,sdev0[1],sdev1[1],color = color[1],alpha=0.25)
ax1.fill_between(y,sdev0[2],sdev1[2],color = color[2],alpha=0.25)
ax1.fill_between(y,sdev0[3],sdev1[3],color = color[3],alpha=0.25)
ax2.fill_between(y,sdev0[4],sdev1[4],color = color[4],alpha=0.25)

ax1.legend(loc=0,fontsize=16)
ax2.legend(loc=2,fontsize=16)


fig.tight_layout()  
plt.savefig('monperfplot.pdf', format='pdf', dpi=5000)
plt.show() 
"""
import numpy as np
import matplotlib.pyplot as plt

avgn = 1; nepisodes = 250
data = range(0,1000,1)
data = np.load('/home/asemwal/Documents/1k5r_10_250_400_10_1_25.npy')
degree = []
peering= []
greedy = []
random= []
y = []

file = open('/home/asemwal/raw_data/experiments/plotdata.csv','r')
l=str(file.readline()).strip()
l=str(file.readline()).strip()
i=0
while l != '':
    rec = l.split("|")
    print rec
    if rec[-1] == '1':
        degree.append([])
        peering.append([])
        greedy.append([])
        random.append([])
        y.append(int(rec[8]))
    greedy[-1].append(float(rec[3]))
    peering[-1].append(float(rec[4]))
    degree[-1].append(float(rec[5]))
    random[-1].append(float(rec[6]))
    
    l=str(file.readline()).strip()
a=0
average = [[],[],[],[]]
median = [[],[],[],[]]
percentile25 = [[],[],[],[]]
percentile75 = [[],[],[],[]]
sdev0 = [[],[],[],[]]
sdev1 = [[],[],[],[]]

for i in y:
    average[0].append(np.average(greedy[a]))
    average[1].append(np.average(peering[a]))
    average[2].append(np.average(degree[a]))
    average[3].append(np.average(random[a]))
    
    median[0].append(np.median(greedy[a]))
    median[1].append(np.median(peering[a]))
    median[2].append(np.median(degree[a]))
    median[3].append(np.median(random[a]))
    
    percentile25[0].append(np.percentile(greedy[a],[25.])[0])
    percentile25[1].append(np.percentile(peering[a],[25.])[0])
    percentile25[2].append(np.percentile(degree[a],[25.])[0])
    percentile25[3].append(np.percentile(random[a],[25.])[0])
    
    percentile75[0].append(np.percentile(greedy[a],[75.])[0])
    percentile75[1].append(np.percentile(peering[a],[75.])[0])
    percentile75[2].append(np.percentile(degree[a],[75.])[0])
    percentile75[3].append(np.percentile(random[a],[75.])[0])
    
    sdev0[0].append(average[0][-1]- np.std(greedy[a]))
    sdev0[1].append(average[1][-1]- np.std(peering[a]))
    sdev0[2].append(average[2][-1]- np.std(degree[a]))
    sdev0[3].append(average[3][-1]- np.std(random[a]))
    
    sdev1[0].append(average[0][-1]+ np.std(greedy[a]))
    sdev1[1].append(average[1][-1]+ np.std(peering[a]))
    sdev1[2].append(average[2][-1]+ np.std(degree[a]))
    sdev1[3].append(average[3][-1]+ np.std(random[a]))
    
    a+=1

color = ['g','b','m','r']
plt.plot(y,average[0],color[0])
plt.plot(y,average[1],color[1])
plt.plot(y,average[2],color[2])
plt.plot(y,average[3],color[3])
plt.fill_between(y,sdev0[0],sdev1[0],color = color[0], alpha=0.25)
plt.fill_between(y,sdev0[1],sdev1[1],color = color[1],alpha=0.25)
plt.fill_between(y,sdev0[2],sdev1[2],color = color[2],alpha=0.25)
plt.fill_between(y,sdev0[3],sdev1[3],color = color[3],alpha=0.25)

plt.legend([ 'Peering-degree based','Greedy-link Based','Degree Based','Random' ])
plt.xlabel('Graph Size', fontsize=14)
plt.ylabel('Link Coverage', fontsize=14)
plt.savefig('destination_path.pdf', format='pdf', dpi=5000)
plt.show()

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