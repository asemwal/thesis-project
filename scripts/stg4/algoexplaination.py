# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 11:05:28 2019

@author: asemwal
"""

import networkx as nx
import matplotlib.pyplot as plt

def peertopeercycle():
    G = nx.DiGraph()
    G.add_edge(1,2,relationship='peer-to-peer')
    G.add_edge(2,1,relationship='peer-to-peer')


    G.add_edge(2,3,relationship='peer-to-peer')
    G.add_edge(3,2,relationship='peer-to-peer')

    G.add_edge(1,3,relationship='peer-to-peer')
    G.add_edge(3,1,relationship='peer-to-peer')



    G.add_edge(1,4,relationship='provider-to-customer')
    G.add_edge(4,1,relationship='customer-to-provider')
    G.add_edge(2,5,relationship='provider-to-customer')
    G.add_edge(5,2,relationship='customer-to-provider')
    G.add_edge(3,6,relationship='provider-to-customer')
    G.add_edge(6,3,relationship='customer-to-provider')

    G.add_edge(4,7,relationship='provider-to-customer')
    G.add_edge(7,4,relationship='customer-to-provider')
    G.add_edge(5,8,relationship='provider-to-customer')
    G.add_edge(8,5,relationship='customer-to-provider')
    G.add_edge(6,9,relationship='provider-to-customer')
    G.add_edge(9,6,relationship='customer-to-provider')

    G.add_edge(9,8,relationship='peer-to-peer')
    G.add_edge(8,9,relationship='peer-to-peer')
    G.add_edge(7,8,relationship='peer-to-peer')
    G.add_edge(8,7,relationship='peer-to-peer')
    G.add_edge(7,9,relationship='peer-to-peer')
    G.add_edge(9,7,relationship='peer-to-peer')
    
    return G


def peertopeercycle2():
    G = nx.DiGraph()
#    G.add_edge(1,2,relationship='peer-to-peer')
#    G.add_edge(2,1,relationship='peer-to-peer')
#
#
#    G.add_edge(2,3,relationship='peer-to-peer')
#    G.add_edge(3,2,relationship='peer-to-peer')
#
#    G.add_edge(1,3,relationship='peer-to-peer')
#    G.add_edge(3,1,relationship='peer-to-peer')
#
#
#
#    G.add_edge(1,4,relationship='provider-to-customer')
#    G.add_edge(4,1,relationship='customer-to-provider')
#    G.add_edge(2,5,relationship='provider-to-customer')
#    G.add_edge(5,2,relationship='customer-to-provider')
#    G.add_edge(3,6,relationship='provider-to-customer')
#    G.add_edge(6,3,relationship='customer-to-provider')
#
#    G.add_edge(4,7,relationship='provider-to-customer')
#    G.add_edge(7,4,relationship='customer-to-provider')
#    G.add_edge(5,8,relationship='provider-to-customer')
#    G.add_edge(8,5,relationship='customer-to-provider')
#    G.add_edge(6,9,relationship='provider-to-customer')
#    G.add_edge(9,6,relationship='customer-to-provider')
#
#    G.add_edge(9,12,relationship='provider-to-customer')
#    G.add_edge(12,9,relationship='customer-to-provider')
#    G.add_edge(10,13,relationship='provider-to-customer')
#    G.add_edge(13,10,relationship='customer-to-provider')
#    G.add_edge(11,14,relationship='provider-to-customer')
#    G.add_edge(14,11,relationship='customer-to-provider')
#
#    G.add_edge(15,12,relationship='customer-to-provider')
#    G.add_edge(12,15,relationship='provider-to-customer')
#
#
#    G.add_edge(9,8,relationship='peer-to-peer')
#    G.add_edge(8,9,relationship='peer-to-peer')
#    
#    G.add_edge(13,15,relationship='peer-to-peer')
#    G.add_edge(15,13,relationship='peer-to-peer')
#    
#    G.add_edge(11,12,relationship='peer-to-peer')
#    G.add_edge(12,11,relationship='peer-to-peer')
    G.add_edge(1,2,relationship='p2p')
    G.add_edge(2,1,relationship='p2p')


    G.add_edge(2,3,relationship='p2p')
    G.add_edge(3,2,relationship='p2p')

    G.add_edge(1,3,relationship='p2p')
    G.add_edge(3,1,relationship='p2p')



    G.add_edge(1,4,relationship='p2c')
    G.add_edge(2,5,relationship='p2c')
    G.add_edge(3,6,relationship='p2c')
    

    G.add_edge(4,7,relationship='p2c')
    G.add_edge(5,8,relationship='p2c')
    G.add_edge(6,9,relationship='p2c')
    
    G.add_edge(7,10,relationship='p2c')
    G.add_edge(8,11,relationship='p2c')
    
    G.add_edge(10,13,relationship='p2c')
    G.add_edge(9,12,relationship='p2c')
    G.add_edge(11,14,relationship='p2c')
    G.add_edge(12,15,relationship='p2c')
#    G.add_edge(14,11,relationship='c2p')
#    G.add_edge(11,8,relationship='c2p')
#    G.add_edge(6,3,relationship='c2p')
#    G.add_edge(4,1,relationship='c2p')
#    G.add_edge(5,2,relationship='c2p')
#    G.add_edge(7,4,relationship='c2p')
#    G.add_edge(8,5,relationship='c2p')
#    G.add_edge(9,6,relationship='c2p')
#    G.add_edge(10,7,relationship='c2p')
#    G.add_edge(12,9,relationship='c2p')
#    G.add_edge(13,10,relationship='c2p')
#    G.add_edge(15,12,relationship='c2p')
#    

    G.add_edge(7,8,relationship='p2p')
    G.add_edge(8,7,relationship='p2p')
    
    G.add_edge(13,15,relationship='p2p')
    G.add_edge(15,13,relationship='p2p')
    
    G.add_edge(11,12,relationship='p2p')
    G.add_edge(12,11,relationship='p2p')
    pos=dict()
    sepy=0
    sepx=.65

    pos[1] = (0,20)
    pos[2] = (10,-10)
    pos[3] = (-10,-10)

    pos[4] = (pos[1][0], pos[1][1]-2)
    pos[5] = (pos[2][0]-5, pos[2][1]+2)
    pos[6] = (pos[3][0]+5, pos[3][1]+2)

    pos[7] = (pos[1][0], pos[1][1]-4)
    pos[8] = (pos[2][0]-4, pos[2][1]+2)
    pos[9] = (pos[3][0]+4, pos[3][1]+2)

    pos[10] = (pos[1][0], pos[1][1]-6)
    pos[11] = (pos[2][0]-6, pos[2][1]+4)
    pos[12] = (pos[3][0]+6, pos[3][1]+4)


    pos[13] = (pos[1][0], pos[1][1]-8)
    pos[14] = (pos[2][0]-8, pos[2][1]+6)
    pos[15] = (pos[3][0]+8, pos[3][1]+6)

    pos[8] = (-.3,0)
    pos[7] = (0,-.35)
    pos[9] = (0,.35)
    pos[4] = (pos[7][0]+sepx, pos[7][1])
    pos[5] = (pos[8][0]+sepx, pos[8][1]+sepy)
    pos[6] = (pos[9][0]+sepx, pos[9][1]+sepy)

    pos[1] = (pos[4][0]+sepx, pos[4][1]+sepy)
    pos[2] = (pos[5][0]+sepx, pos[5][1]+sepy)
    pos[3] = (pos[6][0]+sepx, pos[6][1]+sepy)

    pos[10] = (pos[7][0]-sepx, pos[7][1]+sepy)
    pos[11] = (pos[8][0]-sepx, pos[8][1]+sepy)
    pos[12] = (pos[9][0]-sepx, pos[9][1]+sepy)

    pos[13] = (pos[10][0]-sepx, pos[10][1]+sepy)
    pos[14] = (pos[11][0], pos[11][1]-0.25)
    pos[15] = (pos[12][0]-sepx, pos[12][1]+sepy)

    #pos[5] = (pos[6][0] , pos[6][1]-.1)

        
    lables  = nx.get_edge_attributes(G, 'relationship')
    nx.draw(G, pos=pos, wih_labels=True , font_size= 12,node_size=750,node_color='w') 
    nx.draw_networkx_labels(G, pos,font_size= 12)
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [12,7], with_labels=True , font_size= 12,node_size=750,node_color='m', alpha=0.25) 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [ 2,4 ], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [2,4], with_labels=True , font_size= 16,node_size=1000,node_color='r') 
    #G.remove_edge(1,2)
    #G.remove_edge(2,1)    
    edges =list(G.edges()) 
    nx.draw_networkx_edges(G, pos=pos, edgelist = edges, with_labels=True , font_size= 12,node_size=750,node_color='w') 
    e= nx.draw_networkx_edge_labels(G, pos ,  lables , font_size= 12)
    for _,t in e.items():
        t.set_rotation('horizontal')
    for i in lables:
        print str(i[0])+"|"+str(i[1])+"|"+lables[i]
    plt.axis('off')
    #plt.savefig('/home/asemwal/raw_data/report/dummy4.pdf',format='pdf')
    plt.show()    

def newillustration():
    G=nx.DiGraph()
    G.add_edge(1,2,relationship = 'p2p')
    G.add_edge(2,1,relationship = 'p2p')

    G.add_edge(3,2,relationship = 'p2p')
    G.add_edge(2,3,relationship = 'p2p')

    G.add_edge(4,3,relationship = 'p2p')
    G.add_edge(3,4,relationship = 'p2p')

    G.add_edge(5,6,relationship = 'p2p')
    G.add_edge(6,5,relationship = 'p2p')

    G.add_edge(7,8,relationship = 'p2p')
    G.add_edge(8,7,relationship = 'p2p')

    G.add_edge(12,13,relationship = 'p2p')
    G.add_edge(13,12,relationship = 'p2p')
    
    G.add_edge(1,5,relationship = 'p2c')
    
    G.add_edge(2,6,relationship = 'p2c')
    
    G.add_edge(3,7,relationship = 'p2c')
    
    G.add_edge(4,8,relationship = 'p2c')
    
    G.add_edge(6,9,relationship = 'p2c')
    
    G.add_edge(7,10,relationship = 'p2c')
    G.add_edge(7,11,relationship = 'p2c')
    
    G.add_edge(9,12,relationship = 'p2c')
    
    G.add_edge(10,13,relationship = 'p2c')

    G.add_edge(11,14,relationship = 'p2c')

    G.add_edge(5,15,relationship = 'p2c')
#    G.add_edge(15,5,relationship = 'p2c')
    pos=dict()
    sepy=-10
    sepx=5
    pos[1] = (-1,-1)
    pos[2] = (pos[1][0]+sepx , pos[1][1])
    pos[3] = (pos[2][0]+sepx,pos[1][1])
    pos[4] = (pos[3][0]+sepx,pos[1][1])
    pos[5] = (pos[1][0],pos[1][1]+sepy)
    pos[6] = (pos[2][0],pos[5][1])
    pos[7] = (pos[3][0],pos[5][1])
    pos[8] = (pos[4][0],pos[5][1])
    pos[9] = (pos[6][0],pos[6][1]+sepy)
    pos[10] = (pos[7][0],pos[7][1]+sepy)
    pos[11] = (pos[7][0]+sepx,pos[7][1]+sepy)
    pos[12] = (pos[9][0], pos[9][1]+sepy)
    pos[13] = (pos[10][0], pos[10][1]+sepy)
    pos[14] = (pos[11][0], pos[11][1]+sepy)
    #g=nx.DiGraph(G.subgraph([1,2,3,4,5,6,7,8,12,13]))
    pos[12] = (pos[9][0], pos[9][1]+sepy)
    pos[13] = (pos[10][0], pos[10][1]+sepy)
    pos[15] = (pos[5][0],pos[5][1]+sepy)
    pos[16] = (pos[15][0],pos[15][1]+sepy)
    pos[17] = (pos[16][0]-sepx,pos[16][1])

    #G=nx.DiGraph(g)
    #G.remove_edge(1,5)
    #G.remove_edge(2,6)
    #G.remove_edge(3,7)
    #G.remove_edge(4,8)
    lables  = nx.get_edge_attributes(G, 'relationship')
    nx.draw(G, pos=pos, wih_labels=True , font_size= 16,node_size=1000,node_color='w') 
    nx.draw_networkx_labels(G, pos,font_size= 16)
    nx.draw_networkx_nodes(G, pos=pos, nodelist = [12,7], with_labels=True , font_size= 16,node_size=1000,node_color='m', alpha=0.25) 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [ 2,4 ], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [2,4], with_labels=True , font_size= 16,node_size=1000,node_color='r') 
    #G.remove_edge(1,2)
    #G.remove_edge(2,1)    
    edges =list(G.edges()) 
    nx.draw_networkx_edges(G, pos=pos, edgelist = edges, with_labels=True , font_size= 16,node_size=1000,node_color='w') 
    e= nx.draw_networkx_edge_labels(G, pos ,  lables , font_size= 16)
    for _,t in e.items():
        t.set_rotation('horizontal')
    for i in lables:
        print str(i[0])+"|"+str(i[1])+"|"+lables[i]
    plt.axis('off')
    #plt.savefig('/home/asemwal/raw_data/report/dummy3.pdf',format='pdf')
    plt.show()    
    return G
    
    


    #g= nx.DiGraph(nx.subgraph(G, [2,4 ]))
    #G= nx.DiGraph(g)
    #lables  = nx.get_edge_attributes(g, 'relationship')

    #G=nx.DiGraph(g)
    #G.remove_edge(1,5)
    #G.remove_edge(2,6)
    #G.remove_edge(3,7)
    #G.remove_edge(4,8)
    lables  = nx.get_edge_attributes(G, 'relationship')
    nx.draw(G, pos=pos, wih_labels=True , font_size= 16,node_size=1000,node_color='w') 
    nx.draw_networkx_labels(G, pos,font_size= 16)
    nx.draw_networkx_nodes(G, pos=pos, nodelist = [12,7], with_labels=True , font_size= 16,node_size=1000,node_color='m', alpha=0.25) 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [ 2,4 ], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [2,4], with_labels=True , font_size= 16,node_size=1000,node_color='r') 
    #G.remove_edge(1,2)
    #G.remove_edge(2,1)    
    edges =list(G.edges()) 
    nx.draw_networkx_edges(G, pos=pos, edgelist = edges, with_labels=True , font_size= 16,node_size=1000,node_color='w') 
    e= nx.draw_networkx_edge_labels(G, pos ,  lables , font_size= 16)
    for _,t in e.items():
        t.set_rotation('horizontal')
    for i in lables:
        print str(i[0])+"|"+str(i[1])+"|"+lables[i]
    plt.axis('off')
    #plt.savefig('/home/asemwal/raw_data/report/dummy3.pdf',format='pdf')
    plt.show()
    

def visibility():
    G=nx.DiGraph()
    G.add_edge(3,6,relationship = 'p2c')
    G.add_edge(2,5,relationship = 'p2c')
    G.add_edge(1,4,relationship = 'p2c')
    #G.add_edge(4,5,relationship = 'p2p')
    #G.add_edge(5,6,relationship = 'p2p')
    G.add_edge(1,2,relationship = 'p2p')
    G.add_edge(2,3,relationship = 'p2p')
    G.add_edge(2,1,relationship = 'p2p')
    G.add_edge(3,2,relationship = 'p2p')
    #G.add_edge(4,3,relationship = 'p2p')
    #G.add_edge(5,4,relationship = 'p2p')
    #G.add_edge(6,5,relationship = 'p2p')
    #G.add_edge(2,9,relationship = 'p2p')
    #G.add_edge(5,6,relationship = 'p2p')
    #G.add_edge(6,5,relationship = 'p2p')
    lables  = nx.get_edge_attributes(G, 'relationship')
    print lables
    #g= nx.DiGraph(nx.subgraph(G, [2,4 ]))
    #G= nx.DiGraph(g)
    #lables  = nx.get_edge_attributes(g, 'relationship')
    pos=dict()
    sep=-0.1
    sepx=5
    pos[1] =(-5,0)
    pos[2] =(pos[1][0]+sepx,pos[1][1])
    pos[3] =(pos[2][0]+sepx,pos[2][1])
    pos[4] =(pos[1][0],pos[1][1]+sep)
    pos[5] =(pos[2][0],pos[2][1]+sep)
    pos[6] =(pos[3][0],pos[3][1]+sep)
    nx.draw(G, pos=pos, wih_labels=True , font_size= 16,node_size=1000,node_color='w') 
    nx.draw_networkx_labels(G, pos,font_size= 16)
#    nx.draw_networkx_nodes(G, pos=pos, nodelist = [8,2,9], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [ 2,4 ], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    #nx.draw_networkx_nodes(G, pos=pos, nodelist = [2,4], with_labels=True , font_size= 16,node_size=1000,node_color='r') 
    G.remove_edge(1,2)
    G.remove_edge(2,1)    
    edges =list(G.edges()) 
    nx.draw_networkx_edges(G, pos=pos, edgelist = edges, with_labels=True , font_size= 16,node_size=1000,node_color='w') 
    #e= nx.draw_networkx_edge_labels(G, pos ,  lables , font_size= 16)
    #for _,t in e.items():
    #    t.set_rotation('horizontal')
    #for i in lables:
    #    print str(i[0])+"|"+str(i[1])+"|"+lables[i]
    plt.axis('off')
    #plt.savefig('/home/asemwal/raw_data/report/visib3.pdf',format='pdf')
    plt.show()

def mainfunc():
    G=nx.DiGraph()
    G.add_edge(1,2,relationship = 'p2c')
    G.add_edge(1,3,relationship = 'p2c')
    G.add_edge(1,4,relationship = 'p2c')
    G.add_edge(1,9,relationship = 'p2c')
    G.add_edge(2,5,relationship = 'p2c')
    G.add_edge(2,10,relationship = 'p2c')
    #G.add_edge(2,6,relationship = 'p2c')
    G.add_edge(3,7,relationship = 'p2c')
    G.add_edge(3,8,relationship = 'p2c')

    G.add_edge(3,2,relationship = 'p2p')
    G.add_edge(2,3,relationship = 'p2p')
    G.add_edge(3,4,relationship = 'p2p')
    G.add_edge(4,3,relationship = 'p2p')
    G.add_edge(9,2,relationship = 'p2p')
    G.add_edge(2,9,relationship = 'p2p')
    #G.add_edge(5,6,relationship = 'p2p')
    #G.add_edge(6,5,relationship = 'p2p')
    lables  = nx.get_edge_attributes(G, 'relationship')
    print lables
    #g= nx.DiGraph(nx.subgraph(G, [2,4 ]))
    #G= nx.DiGraph(g)
    #lables  = nx.get_edge_attributes(g, 'relationship')
    pos = {1:(0.8,0),9:(-0.3,-0.2),2:(0.4,-0.2),5:(0.525,-0.4), 4:(0.35,-0.4), 6:(0.65,-0.4), 7:(0.9,-0.4)}    
    pos[8]=(1.5,-0.4)
    pos[4]=(1.8,-0.2)    
    pos[3]=(1.1,-0.2)    
    pos[10] = (0,-0.4)
    nx.draw(G, pos=pos, wih_labels=True , font_size= 16,node_size=1000,node_color='w') 
    nx.draw_networkx_labels(G, pos,font_size= 16)
#    nx.draw_networkx_nodes(G, pos=pos, nodelist = [8,2,9], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    nx.draw_networkx_nodes(G, pos=pos, nodelist = [ 2,4 ], with_labels=True , font_size= 16,node_size=1000,node_color='b') 
    nx.draw_networkx_nodes(G, pos=pos, nodelist = [2,4], with_labels=True , font_size= 16,node_size=1000,node_color='r') 
    nx.draw_networkx_edges(G, pos=pos, edgelist = list(G.edges()), with_labels=True , font_size= 16,node_size=1000,node_color='w') 
    e= nx.draw_networkx_edge_labels(g, pos ,  lables , font_size= 16)
    for _,t in e.items():
        t.set_rotation('horizontal')
    for i in lables:
        print str(i[0])+"|"+str(i[1])+"|"+lables[i]
    plt.axis('off')
    #plt.savefig('/home/asemwal/raw_data/report/graph6.pdf',format='pdf')
    plt.show()
pos=peertopeercycle2()