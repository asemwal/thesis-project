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
f='/home/asemwal/raw_data/2018/proc/vp_links_1530709999_1530769499_dedup'
links = set()
if len(sys.argv) >=2:
    f=sys.argv[1]
purpose='greedy_result'
threshold = 1
print(time.time())
file = open('/home/asemwal/raw_data/2018/proc/peer_collector', 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases= l.split("|")
    monitor.update({ases[1]:set()})
    monitor_len.update({ases[1]:0})
    l = str(file.readline()).strip()
    
file = open(f, 'r')
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases= l.split("|")
    try:
        monitor[ases[0]].add("|".join(ases[1:3]))
        links.add("|".join(ases[1:3]))
    except KeyError as e:
        monitor.update({ases[0]:set()})
        monitor_len.update({ases[0]:1})
        monitor[ases[0]].add("|".join(ases[1:3]))
        links.add("|".join(ases[1:3]))
        #print(l)
    l = str(file.readline()).strip()

for i in monitor.keys():
    monitor_len[i] = len(monitor[i])
    
visible_prob = monitor_len.copy()
for i in visible_prob.keys():
    visible_prob[i] = (visible_prob[i]/float(len(links)))
 
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
    if len(visible_links) == len(links):
        break;
    for i in copy_monitor.keys():
        copy_monitor[i] = copy_monitor[i].difference(visible_links)
        monitor_len[i] = len(copy_monitor[i])
    sorted_x = sorted(monitor_len.items(), key=operator.itemgetter(1))

line="visible links:" +str(len(visible_links))+"\ttotal_links: " +str(len(links))+"\n"
line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monitor))+"\n"
line+= "Threshold :"+ str(threshold) +'\n'
print(time.time())
while(True):
    try:
        x = vp.pop(0)
        line += str(x) +"|"+ str(visible_prob[x]) +"\n"
    except KeyError as e:
        break;        
    except IndexError as e:
        break;
f = file.name;

out = open(location+year+'proc/'+purpose+"_"+str(threshold)+'_'+utils.getTimeStamp(f.split("/")[-1]), 'w')


out.write(line)
out.flush()
out.close()