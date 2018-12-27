# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 09:28:04 2018

@author: asemwal
"""
import time
if True:
    f='peer_collector'
    file = open('/home/asemwal/thesis/bgpreader/proc/'+f, 'r')
    l = str(file.readline()).strip()
    l = str(file.readline()).strip()
    peer = {}
    while(l !=''):
        x = l.split("|")
        if( x[0]+"|"+x[1] in peer.keys()):
            pass
        else:
            peer.update({x[0]+"|"+x[1]:0})
            print('newpeer')
        l = str(file.readline()).strip()
            

line=""
print(time.time())
while(True):
    try:
        x = peer.popitem()
        line += str(x[0])+"\n"
    except KeyError as e:
        break;
out = open('/home/asemwal/thesis/bgpreader/proc/dedup_'+file.name.split('/')[-1], 'w')
out.write(line)
out.flush()
out.close()