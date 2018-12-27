# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 13:12:58 2018

@author: asemwal
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from os import listdir
from os.path import isfile, join
def tuneup(No = 12555 , Nc = 50218 , alpha = 0.91,   beta = 4000): 
    global D ,g, Ngt0
    D = dict()
    L  = 0
    p = [1.0] *  (No)
    for j in range(0,len(p)):
        p[j]/= (No)
    for i in range(0,No):
        x = list(np.random.choice(list(range(0,No)), 1, p=p, replace = False))
        D[i] = int(beta*(x[0]**-alpha))
        L += D[i]   
    print L
    Lc = int(L*0.33*0.005)
    Lo = int(L*0.67*0.005)
    Lc = 123606
    Lo = 568054
    MAX  = 0 
    MIN= 100000000
    for i in D.keys():
        if MAX < D[i]:
            MAX = D[i]
        if MIN > D[i]:
            MIN = D[i]
    
    print MIN,MAX, L
    d_keys = []
    for i in D.keys():
        d_keys.append(D[i])
    d_keys.sort()
    y = list(range(1,len(d_keys)+1))
    plt.plot( d_keys,y, 'bo' )
    #plt.loglog( y2['p2p'],peering2['p2p'],'ro',label = label[1] )
    plt.legend(loc=1,fontsize=16)
    #ax2.legend(loc=2,fontsize=8)
    
    
    #plt.savefig("_".join(graphfile1.split("/")[-1].split(".")[0:2]) +'_ccdf.pdf', format='pdf', dpi=5000)
    plt.show()

    return D

d = tuneup()