# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 19:57:25 2018

@author: asemwal
"""

import networkx as nx
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 22:31:13 2018

@author: asemwal
"""

import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import networkx as nx
import os
import numpy as np
from os import listdir
from os.path import isfile, join
import datetime as dt

from datetime import datetime
from calendar import timegm

# Note: if you pass in a naive dttm object it's assumed to already be in UTC
def unix_time(dttm=None):
    if dttm is None:
       dttm = datetime.utcnow()

    return timegm(dttm.utctimetuple())

print "Unix time now: %d" % unix_time()
print "Unix timestamp from an existing dttm: %d" % unix_time(datetime(2014, 12, 30, 12, 0))

 

f='/home/asemwal/raw_data/scripts/plots/growth.txt'
file = open(f,'r')
data = {}
l = str(file.readline()).strip()
l = str(file.readline()).strip()
t=0
while l!='':
    if l.find("#") > -1:
        pass
    else:
        rec= l.split("|")
        t = unix_time(datetime(int(rec[0][0:4]),int(rec[0][4:6]),int(rec[0][6:8]),0,0))
        data.update({t: {'p2c':int(rec[1]),'p2p':int(rec[2]), 'nodes':int(rec[3]),'edges':int(rec[4])}})
    l = str(file.readline()).strip()
 
#y = [100,200,300,400,500,600] 
 
#label = [ 'Peering-degree based','Greedy-link Based','Degree Based','Random','Monitor Set Size' ]
color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'k','g']
#color = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
#matplotlib.rcParams['axes.prop_cycle']
#plt.ylim((0,90))
#plt.xlim((0,0.9))
#fig, ax1 = plt.subplots()

#ax1.set_xlabel('Normalized Invisibility Score', fontsize=8)
#ax1.set_ylabel('Link Coverage', fontsize=8)
#ax1.tick_params(axis='y' )
#ax2 = ax1.twinx()
#ax2.set_ylabel('Monitor Set Size', fontsize=8)
#ax2.tick_params(axis='y' )
#axarr[0, 0].set_ylabel('Nodes', fontsize=16)
#axarr[0, 0].set_xaxis ('Nodes', fontsize=16)

#    y=  d.keys() 
label = ['p2p_1','p2p_2','p2c_1','p2c_2','c2p_1','c2p_2']
xax = list(data.keys())
xax.sort()
print xax
#dates=[dt.datetime.fromtimestamp(ts) for ts in xax]
dates  = []
yax = {'nodes':[],'edges':[],'p2p':[],'p2c':[]}
for i in range(0,len(xax)):
    dates.append(dt.datetime.fromtimestamp(xax[i]))
    print dates
    yax['nodes'].append(data[xax[i]]['nodes'])
    yax['edges'].append(data[xax[i]]['edges'])
    yax['p2c'].append(data[xax[i]]['p2c'])
    yax['p2p'].append(data[xax[i]]['p2p'])
ax=plt.gca()
xfmt = md.DateFormatter('%YY-%m')
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)
#ax.xaxis.set_major_formatter(xfmt)
#plt.set_major_formatter(xfmt)
plt.xlabel('Year', fontsize=16)
plt.yscale("log", nonposx='clip')
plt.ylabel('Number of ASes', fontsize=16)
plt.legend(loc=0,fontsize=16)
plt.plot_date(dates,yax['nodes'], 'b-', xdate=True, label = 'AS Count') 
#plt.plot_date(dates,yax['p2c'], 'r.', xdate=True, label = 'provider-to-customer')
#plt.plot_date(dates,yax['edges'], 'mx', xdate=True, label = 'Total Links')
plt.xticks( rotation=0)
plt.grid(True)
datemin = np.datetime64(dates[1], 'Y')
datemax = np.datetime64(dates[-1], 'Y') + np.timedelta64(1, 'Y')
ax.set_xlim(datemin, datemax)
#plt.plot(xax,yax['edges'], 'r')
#plt.plot(xax,yax['p2p'], 'g')
#plt.plot(xax,yax['p2c'], 'm')
  
plt.legend(loc=2,fontsize=8)


plt.savefig('ASes_evolution.pdf', format='pdf', dpi=5000)
plt.show()

