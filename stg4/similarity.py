# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
import operator
monitor = {}
monitor_len ={}
#f=sys.argv[1]
purpose='greedy_result'
threshold = 25
print(time.time())
file = open('/home/asemwal/raw_data/2018/proc/link_monitor_aspathsdups_deduped', 'r')
f = file.name;
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases= l.split("|")
    monitor.update({ases[0]:set()})
    monitor_len.update({ases[0]:0})
    l = str(file.readline()).strip()
    
file = open('/home/asemwal/raw_data/2018/proc/link_monitor_aspathsdups_deduped', 'r')
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases= l.split("|")
    monitor[ases[0]].add("|".join(ases[1:3]))
    l = str(file.readline()).strip()

for i in monitor.keys():
    monitor_len[i] = len(monitor[i])
    
    
monitor_key = monitor.keys()

copy_monitor = monitor.copy()
visible_links = set()
vp =[]
sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
while len(sorted_x ) > 0:
    r = sorted_x.pop(-1)
    if r[1] > threshold:
        vp.append(r[0])
        visible_links = visible_links.union(copy_monitor[r[0]])
    copy_monitor.pop(r[0])
    monitor_len.pop(r[0])
    for i in copy_monitor.keys():
        copy_monitor[i] = copy_monitor[i].difference(visible_links)
        monitor_len[i] = len(copy_monitor[i])
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

print(time.time())
while(True):
    try:
        x = vp.pop(0)
        line += str(x) +"\n"
    except KeyError as e:
        break;
    except IndexError as e:
        break;
out = open(location+year+'proc/'+purpose+"_"+str(threshold)+'_'+utils.getTimeStamp(f.split("/")[-1]), 'w')


out.write(line)
out.flush()
out.close()