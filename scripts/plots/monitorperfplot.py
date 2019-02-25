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

degree = dict()
peering= dict()
greedy = dict()
random= dict()
y = []
monset = dict()
average = dict()
median = dict()
percentile25 = dict()
percentile75 = dict()
sdev0 = dict()
sdev1 = dict()

keys = [100,200,300,400,500,600]
for i in keys:
    degree[i] = [[],[],[]]
    greedy[i] = [[],[],[]]
    peering[i] = [[],[],[]]
    random[i] = [[],[],[]]
    monset[i] = [[],[],[]]
    average[i] = []
    median[i] = []
    percentile25[i] = []
    percentile75[i] = []
    sdev0[i] = []
    sdev1[i] = []
file = open('/home/asemwal/raw_data/experiments/results/visibility_results5','r')
l=str(file.readline()).strip()
l=str(file.readline()).strip()
m=1
p=5
g=8
d=11
r=14
while l != '':
    rec = l.split("|")
    print rec
    k= int(rec[0].split("_")[0])
    i=0
    monset[k][i].append(float(rec[m+i])*100/k)
    i+=1
    monset[k][i].append(float(rec[m+i])*100/k)
    i+=1
    monset[k][i].append(float(rec[m+i])*100/k)
    
    i=0
    peering[k][i].append(float(rec[p+i]))
    i+=1    
    peering[k][i].append(float(rec[p+i]))
    i+=1
    peering[k][i].append(float(rec[p+i]))
    
    i=0
    greedy[k][i].append(float(rec[g+i]))
    i+=1    
    greedy[k][i].append(float(rec[g+i]))
    i+=1
    greedy[k][i].append(float(rec[g+i]))
    
    i=0
    degree[k][i].append(float(rec[d+i]))
    i+=1    
    degree[k][i].append(float(rec[d+i]))
    i+=1
    degree[k][i].append(float(rec[d+i]))
    
    i=0
    random[k][i].append(float(rec[r+i]))
    i+=1    
    random[k][i].append(float(rec[r+i]))
    i+=1
    random[k][i].append(float(rec[r+i]))
    
    l=str(file.readline()).strip()
a=0 
for i in keys:
    average[i].append(list((np.average(monset[i], axis=1))))
    average[i].append(list((np.average(peering[i], axis=1))))
    average[i].append(list((np.average(greedy[i], axis=1))))
    average[i].append(list((np.average(degree[i], axis=1))))
    average[i].append(list((np.average(random[i], axis=1))))

    median[i].append(list((np.average(monset[i], axis=1))))
    median[i].append(list((np.average(peering[i], axis=1))))
    median[i].append(list((np.average(greedy[i], axis=1))))
    median[i].append(list((np.average(degree[i], axis=1))))
    median[i].append(list((np.average(random[i], axis=1))))


    percentile25[i].append(list(np.percentile(monset[i], [25.],axis=1))[0])
    percentile25[i].append(list(np.percentile(peering[i], [25.],axis=1))[0])
    percentile25[i].append(list(np.percentile(greedy[i], [25.],axis=1))[0])
    percentile25[i].append(list(np.percentile(degree[i], [25.],axis=1))[0])
    percentile25[i].append(list(np.percentile(random[i], [25.],axis=1))[0])


    percentile75[i].append(list(np.percentile(monset[i], [75.],axis=1))[0])
    percentile75[i].append(list(np.percentile(peering[i], [75.],axis=1))[0])
    percentile75[i].append(list(np.percentile(greedy[i], [75.],axis=1))[0])
    percentile75[i].append(list(np.percentile(degree[i], [75.],axis=1))[0])
    percentile75[i].append(list(np.percentile(random[i], [75.],axis=1))[0])

    sdev0[i].append(list(np.average(monset[i],axis=1)-np.std(monset[i],axis=1)))
    sdev0[i].append(list(np.average(peering[i],axis=1)-np.std(peering[i],axis=1)))
    sdev0[i].append(list(np.average(greedy[i],axis=1)-np.std(greedy[i],axis=1)))
    sdev0[i].append(list(np.average(degree[i],axis=1)-np.std(degree[i],axis=1)))
    sdev0[i].append(list(np.average(random[i],axis=1)-np.std(random[i],axis=1)))
    
    sdev1[i].append(list(np.average(monset[i],axis=1)+np.std(monset[i],axis=1)))
    sdev1[i].append(list(np.average(peering[i],axis=1)+np.std(peering[i],axis=1)))
    sdev1[i].append(list(np.average(greedy[i],axis=1)+np.std(greedy[i],axis=1)))
    sdev1[i].append(list(np.average(degree[i],axis=1)+np.std(degree[i],axis=1)))
    sdev1[i].append(list(np.average(random[i],axis=1)+np.std(random[i],axis=1)))
    
label = ['Monitor set size', 'Peering degree based','Greedy link based','Degree based','Random' ]
color = ['g','g','m','c','r']



#ax2 = ax1.twinx()
#ax2.set_ylim((3,20))
#ax2.set_ylabel('Monitor set size', fontsize=16)
#ax2.tick_params(axis='y' )

for typ in [0,1,2]:
    plt.ylim((60,95))
    plt.xlabel('Graph size', fontsize=16)
    plt.ylabel('Link coverage', fontsize=16)    
    for i in [1,2,3,4]:
        x=[]
        x1=[]
        x2=[]
        y=keys
        for j in range(0,len(y)):
            x.append(average[y[j]][i][typ])
            x1.append(sdev0[y[j]][i][typ])
            x2.append(sdev1[y[j]][i][typ])
        plt.plot(y,x,color[i],label= label[i],lw=3 )
        plt.fill_between(y,x1,x2,color = color[i], alpha=0.25)

    plt.legend(loc=0,fontsize=14)
    #plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,fontsize=13, \
    #       ncol=2, mode="expand", borderaxespad=0.)
    plt.savefig('monperfplot_'+str(typ)+'.pdf', format='pdf', dpi=5000)
    plt.show() 


color = ['r','b','c','m','c']
label = ['Basic version', 'Refined version','Final version']

plt.ylim((0,30))
plt.xlabel('Graph size', fontsize=16)
plt.ylabel('Number of monitors (%)', fontsize=16)    
for typ in [0,1,2]:
    x=[]
    x1=[]
    x2=[]
    y=keys
    for i in [0]:
        for j in range(0,len(y)):
            x.append(average[y[j]][i][typ])
            x1.append(sdev0[y[j]][i][typ])
            x2.append(sdev1[y[j]][i][typ])
        plt.plot(y,x,color[typ],label= label[typ],lw=3 )
        plt.fill_between(y,x1,x2,color = color[typ], alpha=0.25)
plt.legend(loc=0,fontsize=14)
#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,fontsize=13, \
#          ncol=2, mode="expand", borderaxespad=0.)
plt.savefig('monperfplot_size.pdf', format='pdf', dpi=5000)
plt.show() 


color = ['r','b','c','m','c']
label = ['Basic version', 'Refined version','Final version']

plt.ylim((60,95))
plt.xlabel('Graph size', fontsize=16)
plt.ylabel('Link coverage (%)', fontsize=16)    
for typ in [0,1,2]:
    x=[]
    x1=[]
    x2=[]
    y=keys
    for i in [1]:
        for j in range(0,len(y)):
            x.append(average[y[j]][i][typ])
            x1.append(sdev0[y[j]][i][typ])
            x2.append(sdev1[y[j]][i][typ])
        plt.plot(y,x,color[typ],label= label[typ],lw=3 )
        plt.fill_between(y,x1,x2,color = color[typ], alpha=0.25)

plt.legend(loc=0,fontsize=14)
#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,fontsize=13, \
#           ncol=2, mode="expand", borderaxespad=0.)
plt.savefig('monperfplot_onlyschemes.pdf', format='pdf', dpi=5000)
plt.show() 