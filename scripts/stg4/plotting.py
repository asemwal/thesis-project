import numpy as np
import matplotlib.pyplot as plt

avgn = 1; nepisodes = 250
data = range(0,1000,1)
data = np.load('/home/asemwal/Documents/1k5r_10_250_400_10_1_25.npy')
ns1  = data[0]
ns2  = data[1]
ns3  = data[2]
ns4  = data[3]
ns5  = data[4]
ns6  = data[5]
ns7  = data[6]

ns11 = np.average(ns1,axis=1)
ns10 = np.percentile(ns11,[25.,75.],axis=0)
ns11 = np.median(ns11,axis=0)
ns22 = np.average(ns2,axis=1)
ns20 = np.percentile(ns22,[25.,75.],axis=0)
ns22 = np.median(ns22,axis=0)
ns33 = np.average(ns3,axis=1)
ns30 = np.percentile(ns33,[25.,75.],axis=0)
ns33 = np.median(ns33,axis=0)
ns44 = np.average(ns4,axis=1)
ns40 = np.percentile(ns44,[25.,75.],axis=0)
ns44 = np.median(ns44,axis=0)
ns55 = np.average(ns5,axis=1)
ns50 = np.percentile(ns55,[25.,75.],axis=0)
ns55 = np.median(ns55,axis=0)
ns66 = np.average(ns6,axis=1)
ns60 = np.percentile(ns66,[25.,75.],axis=0)
ns66 = np.median(ns66,axis=0)
ns77 = np.average(ns7,axis=1)
ns70 = np.percentile(ns77,[25.,75.],axis=0)
ns77 = np.median(ns77,axis=0)
nt   = np.linspace(0,nepisodes,nepisodes//avgn)
plt.plot(nt,ns11,lw=2)
plt.plot(nt,ns22,lw=2)
plt.plot(nt,ns33,lw=2)
plt.plot(nt,ns44,lw=2)
plt.plot(nt,ns55,lw=2)
plt.plot(nt,ns66,lw=2)
plt.plot(nt,ns77,lw=2,ls=':')
plt.fill_between(nt,ns10[0],ns10[1],alpha=0.25)
plt.fill_between(nt,ns20[0],ns20[1],alpha=0.25)
plt.fill_between(nt,ns30[0],ns30[1],alpha=0.25)
plt.fill_between(nt,ns40[0],ns40[1],alpha=0.25)
plt.fill_between(nt,ns50[0],ns50[1],alpha=0.25)
plt.fill_between(nt,ns60[0],ns60[1],alpha=0.25)
plt.fill_between(nt,ns70[0],ns70[1],alpha=0.25)
plt.legend(['HRL with planning 0.9','HRL with planning 0.8','HRL with planning 0.65',\
	'HRL with planning 0.5','HRL with planning 0.25','HRL without planning 0','flat RL'])
plt.xlabel('Episodes', fontsize=14)
plt.ylabel('Time steps', fontsize=14)
plt.show()