# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
import operator


def inverselink(r):
    if r == 'c2p':
        return 'p2c'
    elif r == 'p2c':
        return 'c2p'
    else:
        return r
        
def computedifference(  m, popval):
    for k in m.keys():
        m[k]['p2p'] = m[k]['p2p'].difference(popval['p2p'])
        m[k]['s2s'] = m[k]['s2s'].difference(popval['s2s'])
        m[k]['c2p'] = m[k]['c2p'].difference(popval['c2p'])
        m[k]['p2c'] = m[k]['p2c'].difference(popval['p2c'])
    return m

def computelength(l,m):
    for i in monitor_len.keys():
        l[i]['p2p'] = len(m[i]['p2p'])
        l[i]['s2s'] = len(m[i]['s2s'])
        l[i]['c2p'] = len(m[i]['c2p'])
        l[i]['p2c'] = len(m[i]['p2c'])
    return l

def computesort(do,l,s):
    do = do;
    for i in l.keys():
        if do == 1:
            s[i]  = l[i]['p2p'] + l[i]['s2s'] + l[i]['c2p'] + l[i]['p2c']
        elif do == 2:
            s[i]  = l[i]['p2c'] 
        elif do == 3:
            s[i]  = l[i]['c2p'] 
        elif do == 4:
            s[i]  = l[i]['s2s'] 
        elif do == 5:
            s[i]  = l[i]['p2c'] + l[i]['c2p']  
        elif do == 6:
            s[i]  = l[i]['p2p'] + l[i]['p2c'] + l[i]['c2p']
        elif do == 7:
            s[i]  = l[i]['p2p']
    return s
    
   
    
    
stats ={}
relationship ={}
file = open('/home/asemwal/raw_data/2018/proc/ascount_1530662400_1530748799','r')
purpose='pathappendpathrelationship'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip();
while l !='':
    asn=l.split("|")[0]
    relationship.update({asn:dict()})
    l = str(file.readline()).strip();

print("{}: Neighbour list initialized... now populate neighbours".format(time.time()))
file.close()

"""
For all paths in AS update neighbour set and after that count degree
"""
f='/home/asemwal/raw_data/2018/proc/ascount_1530662400_1530748799'
file = open('/home/asemwal/raw_data/2018/proc/relationships','r')
l = str(file.readline()).strip();

c= {'provider-to-customer':'p2c', 'customer-to-provider':'c2p','peer-to-peer':'p2p','sibling-to-sibling':'s2s'}

while l!='':
    ases = l.split("|")
    if True:
        relationship[ases[0]].update({ases[1]:c[ases[2]]})
        relationship[ases[1]].update({ases[0]:inverselink(c[ases[2]])})
    l = str(file.readline()).strip();

do = 1
monitor = {}
globallinks = {'p2p':set(), 'c2p':set(),'s2s':set(),'p2c':set()}
monitor_len ={}
monitor_sort ={}
links2 = set()
if len(sys.argv) >=2:
    f=sys.argv[1]
purpose='greedy_2'
threshold = 1
print(time.time())
file = open('/home/asemwal/raw_data/2018/proc/vantagepoints', 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    monitor.update({l:{'p2p':set(),'p2c':set(),'s2s':set(),'c2p':set()}})
    monitor_len.update({l:{'p2p':0,'p2c':0,'s2s':0,'c2p':0}})
    monitor_sort.update({l:0})
    l = str(file.readline()).strip()
file.close()   
f='/home/asemwal/raw_data/2018/proc/vp_links3_1530662400_1530748799'
file = open(f, 'r')
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    rec= l.split("#")
    try:
        links = rec[1].split(",")
        for i in range(0,len(links)):
            relation = relationship[links[i].split("|")[0]][links[i].split("|")[1]]
            monitor[rec[0]][relation].add( links[i] )
            globallinks[relation].add(links[i])
            links2.add(links[i])
    except KeyError as e:
        pass
    l = str(file.readline()).strip()
    
monitor_len = computelength( monitor_len,monitor )
monitor_sort = computesort(do, monitor_len, monitor_sort )
monitor_key = monitor.keys()

copy_monitor = monitor.copy()
visible_links = {'p2p':set(),'s2s':set(),'c2p':set(),'p2c':set()}
vp =[]
sorted_x = sorted(monitor_sort.items(), key=operator.itemgetter(1))
while len(sorted_x ) > 0:
    r = sorted_x.pop(-1)
    if r[1] > threshold:
        vp.append(r[0])
        visible_links['p2p'] = visible_links['p2p'].union(copy_monitor[r[0]]['p2p'])
        visible_links['s2s'] = visible_links['s2s'].union(copy_monitor[r[0]]['s2s'])
        visible_links['c2p'] = visible_links['c2p'].union(copy_monitor[r[0]]['c2p'])
        visible_links['p2c'] = visible_links['p2c'].union(copy_monitor[r[0]]['p2c'])
    popval = copy_monitor.pop(r[0])
    monitor_len.pop(r[0])
    monitor_sort.pop(r[0])
    if (len(visible_links['c2p'])+len(visible_links['p2c'])+len(visible_links['p2p'])) == (len(globallinks['p2p'])+len(globallinks['s2s'])+len(globallinks['c2p'])+len(globallinks['p2c'])):
        print("broken")
        break;
    copy_monitor = computedifference(  copy_monitor,popval)
    monitor_len = computelength(monitor_len, copy_monitor)
    monitor_sort = computesort(do, monitor_len, monitor_sort)
    sorted_x = sorted(monitor_sort.items(), key=operator.itemgetter(1))

line="visible links:" +str((len(visible_links['c2p'])+len(visible_links['p2c'])+len(visible_links['p2p'])))+"\ttotal_links: " +str(len(links2))+"\n"
line+= "selected VP: "+ str(len(vp))+ "\ttotal VP: "+ str(len(monitor))+"\n"
line+= "Threshold :"+ str(threshold) +'\n'
print(time.time())
while(True):
    try:
        x = vp.pop(0)
        line += str(x) +"|"+ str(len(monitor[x]['p2p']))+"|"+ str(len(monitor[x]['p2c'])) +"|"+ str(len(monitor[x]['c2p'])) +"|"+ str(len(monitor[x]['s2s']))+"\n"
    except KeyError as e:
        break;        
    except IndexError as e:
        break;
f = file.name;

out = open(location+year+'proc/'+purpose+"_"+str(threshold)+'_'+utils.getTimeStamp(f.split("/")[-1]), 'w')


out.write(line)
out.flush()
out.close()