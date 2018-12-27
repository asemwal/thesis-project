# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:17:03 2018

@author: asemwal
"""
import operator
import utils
import time
 

events = set()
file = open('/home/asemwal/raw_data/monitor_event_list','r')
l = str(file.readline()).strip()
monset = dict()
monitor_len = dict()
while l !='':
    x = l.split("|")
    if int(x[1]) > 0:
        monset.update({x[0]:{'bad':set(x[2].split(",")),'good':set(x[4].split(","))}})
        monitor_len.update({x[0]: int(x[1])})        
        events = events.union(set(x[2].split(",")))
    l = str(file.readline()).strip()

vp = set()
monitor_key = monset.keys()

copy_monitor = monset.copy()
visible_events = set()
threshold = -1
sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))
while len(sorted_x ) > 0:
    r = sorted_x.pop(-1)
    if r[1] > threshold:
        vp.add(r[0])
        visible_events  = visible_events.union(copy_monitor[r[0]]['bad'])
    popval = copy_monitor.pop(r[0])
    monitor_len.pop(r[0])
    if (len(visible_events) == (len(events))):
        print("broken")
        break;
    for k in copy_monitor.keys():
        copy_monitor[k]['bad'] = copy_monitor[k]['bad'].difference(visible_events)
        monitor_len[k] = len(copy_monitor[k]['bad'])
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

line="visible events:" +str((len(visible_events)))+"\n"
line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monset))+"\n"
line+= "Threshold :"+ str(threshold) +'\n'
print(time.time())
while(True):
    try:
        x = vp.pop()
        line += str(x) +"|"+ str(len(monset[x]['bad']))+"|"+ str(len(monset[x]['good'])) +"\n"
    except KeyError as e:
        break;        
    except IndexError as e:
        break;
f = file.name;

out = open('/home/asemwal/raw_data/selectionvp', 'w')


out.write(line)
out.flush()
out.close()