# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 14:07:09 2019

@author: asemwal
"""

def combinations(nodes = list(), size = 4):
    combination = list()
    COMBO = list()
    nodes.sort()
    for i in range(0, len(nodes)):
        for j in range(i+1,len(nodes)):
            if [nodes[i],nodes[j]] not in combination:
                combination.append([nodes[i],nodes[j]])
    for i in combination:
        for j in combination:
            if j[0] not in i and j[1] not in i:
                combo = [i[0],i[1],j[0],j[1]]
                combo.sort()
                if combo not in COMBO:
                    COMBO.append(combo)
                
    print(len(COMBO))
    return COMBO
x=combinations(list(range(0,100)))