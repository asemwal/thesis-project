# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 14:58:36 2018

@author: asemwal
"""


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