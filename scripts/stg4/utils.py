# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:58:36 2018

@author: asemwal
"""

def inverselink(r):
    if r == 'customer-to-provider':
        return 'provider-to-customer'
    elif r == 'provider-to-customer':
        return 'customer-to-provider'
    else:
        return r

def getcode(r):
    if r == 'customer-to-provider':
        return 'c2p'
    elif r == 'provider-to-customer':
        return 'p2c'
    elif r == 'peer-to-peer':
        return 'p2p'
    elif r == 'sibling-to-sibling':
        return 's2s'
    else:
        return r


def getKey(x, y):
    index = ''
    while(True):
        try:
            index+= (x[y.pop(0)]+"|")
        except IndexError:
            break;
    return index[0:-1]
            

def getTimeStamp(x):
    y = x.split("_")
    if len(y) >=3:
        return y[-2]+"_"+y[-1]
    else:
        return x
        

def getUniquePath(x):
    ases = list()
    ases.append(x[0])
    for i in range(0,len(x)):
        if ases[-1] != x[i]:
            ases.append(x[i])
            
    return ases