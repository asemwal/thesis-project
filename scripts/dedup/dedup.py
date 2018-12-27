# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import time
stats = {}
print(time.time())
f='evam_victim'
#file = open('/home/asemwal/raw_data/2018/proc/'+f, 'r')
file = open('/home/asemwal/raw_data/'+f, 'r')
#file = open('/home/asemwal/thesis/bgpreader/proc/peer_collector_1_2', 'r')
c=0;
l = file.readline().strip()
while(str(l).strip() !=''):
    try:
        stats[l] =1
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        try:
            stats.update({l:0})
        except KeyError as e:
            print(l)
            print(e)
            pass
        except IndexError:
            pass
        pass
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            line += str(x[0].strip())+"\n"
    except KeyError as e:
        break;
        
#for k in stats.keys():
#    line += str(k) + "|"+ str(stats[k])+"\n"
#out = open('/home/asemwal/raw_data/2018/proc/'+f+'_dedup', 'w')
out = open('/home/asemwal/raw_data/'+f+'_dedup', 'w')
out.write(line)
out.flush()
out.close()

#print(stats)
