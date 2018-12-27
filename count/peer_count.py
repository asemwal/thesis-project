# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 09:28:04 2018

@author: asemwal
"""
import time
if True:
    f='dedup_peer_collector'
    file = open('/home/asemwal/thesis/bgpreader/proc/'+f, 'r')
    l = str(file.readline()).strip()
    l = str(file.readline()).strip()
    peer = {}
    while(l !=''):
        x = l.split("|")
        if( x[0]  in peer.keys()):
            peer[x[0]] +=1
        else:
            peer.update({x[0]:1})
            print('newpeer')
        l = str(file.readline()).strip()
            

line=""
print(time.time())
while(True):
    try:
        x = peer.popitem()
        line += str(x[0])+"|"+str(x[1])+"\n"
    except KeyError as e:
        break;
out = open('/home/asemwal/thesis/bgpreader/proc/count_'+file.name.split('/')[-1], 'w')
out.write(line)
out.flush()
out.close()