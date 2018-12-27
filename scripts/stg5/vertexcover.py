# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 08:38:59 2018

@author: asemwal
"""

import itertools


class Vertex_Cover:

    def __init__(self, graph):
        self.graph = graph

    def validity_check(self, cover):
        is_valid = True
        for i in range(len(self.graph)):
            for j in range(i+1, len(self.graph[i])):
                if self.graph[i][j] == 1 and cover[i] != '1' and cover[j] != '1':
                    return False

        return is_valid

    def vertex_cover_naive(self):
        n = len(self.graph)
        minimum_vertex_cover = 10
        a = list(itertools.product(*["01"] * n))
        for i in a:
            if Vertex_Cover.validity_check(ins, i):
                counter = 0
                for value in i:
                    if value == '1':
                        counter += 1
                minimum_vertex_cover = min(counter, minimum_vertex_cover)

        return minimum_vertex_cover
import math
import time
import networkx as nx

    
if __name__ == '__main__':
    graph =[[0, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 0]]
            
    ins = Vertex_Cover(graph)

    print 'the minimum vertex-cover is:', Vertex_Cover.vertex_cover_naive(ins)

if False and __name__ == '__main__':
    g = nx.Graph()
    f='links'
    print(time.time())
    file = open('/home/asemwal/thesis/bgpreader/proc/'+f, 'r')
    l = str(file.readline()).strip()
    while(l !=''):
        x= l.split('|')
        if(len(x) ==3 ):
            g.add_edge(str(x[0]), str(x[1]))
        l = (file.readline()).strip()
    #ins = Vertex_Cover(g)
    #print('the minimum vertex-cover is:'+ str(Vertex_Cover.vertex_cover_naive(ins)))

    