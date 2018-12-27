# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 21:43:51 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 01:18:21 2018

@author: asemwal
"""
import math
import time
import networkx as nx
neighbour ={}
degree = {}
notpeering = {}
transient = {}
relationship ={}
file = open('/home/asemwal/raw_data/2018/proc/ascount_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l !='':
    asn=l.split("|")[0]
    neighbour.update({asn:set()})
    notpeering.update({asn:dict()})
    relationship.update({asn:dict()})
    transient.update({asn:dict()})
        
    degree.update({asn:0})
    l = str(file.readline()).strip();

print("{}: Neighbour list initialized... now populate neighbours".format(time.time()))
file.close()

"""
For all paths in AS update neighbour set and after that count degree
"""
file = open('/home/asemwal/raw_data/2018/proc/links_1530662400_1530748799','r')
l = str(file.readline()).strip();

while l!='':
    ases = l.split("|")
    neighbour[ases[0]].add(ases[1])
    neighbour[ases[1]].add(ases[0])
    if True:
        notpeering[ases[0]].update({ases[1]:0})
        notpeering[ases[1]].update({ases[0]:0})
        transient[ases[0]].update({ases[1]:0})
        transient[ases[1]].update({ases[0]:0})
        relationship[ases[0]].update({ases[1]:'Undefined'})
        relationship[ases[1]].update({ases[0]:'Undefined'})
    l = str(file.readline()).strip();

for i in neighbour.keys():
    degree[i] = len(neighbour[i])
    
print("{}: end of neighbour and degree processing".format(time.time()))
file.close()

file = open('/home/asemwal/raw_data/2018/proc/paths_append_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    aspath = l.split("|")[0]
    if aspath != '':
        newases = aspath.split(" ")
        ases = [newases[0]];
        for i in range(1, len(newases)):
            if ases[ -1] != newases[i]:
                ases.append(newases[i])
        minJ = 0;
        maxD = 0
        for i in range(0, len(ases)):
            if maxD <  degree[ases[i]]:
                maxD = degree[ases[ i ]]
                minJ = i
                
        for i in range(0, minJ):
            if ases[i] != ases[i+1]:
                transient[ases[i]][ases[i+1]] += 1
        for i in range(minJ, len(ases)-1):
            if ases[i] != ases[i+1]:
                transient[ases[i+1]][ases[i]] += 1
    l = str(file.readline()).strip();

print("{}: end of phase 2 for Gao's algorithm".format(time.time()))
file.close()


file = open('/home/asemwal/raw_data/2018/proc/links_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    ases = l.split("|")
    if (transient[ases[0]][ases[1]] > 1 and transient[ases[1]][ases[0]] >1) or (transient[ases[0]][ases[1]] ==1  and transient[ases[1]][ases[0]] ==1 ) :
            relationship[ases[0]][ases[1]]='sibling-to-sibling' 
    
    elif transient[ases[1]][ases[0]] >=1:
            relationship[ases[0]][ases[1]]='provider-to-customer' 
            relationship[ases[1]][ases[0]]='customer-to-provider' 
    elif transient[ases[0]][ases[1]] >=1:
            relationship[ases[0]][ases[1]]='customer-to-provider' 
            relationship[ases[1]][ases[0]]='provider-to-customer' 

    
    l = str(file.readline()).strip();
    
    
    
file.close()
print("{}: end of phase 3 for Gao's algorithm".format(time.time()))



file = open('/home/asemwal/raw_data/2018/proc/paths_append_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    aspath = l.split("|")[0]
    if aspath != '':
        newases = aspath.split(" ")
        ases = [newases[0]];
        for i in range(1, len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
        minJ = 0;
        maxD = 0
        for i in range(0, len(ases)):
            if maxD <  degree[ases[i]]:
                maxD = degree[ases[ i ]]
                minJ = i
        for i in range(0, minJ-1):
            if ases[i] != ases[i+1]:
                notpeering[ases[i]][ases[i+1]] =1

        for i in range(minJ+1, len(ases)-1):
            if ases[i] != ases[i+1]:
                notpeering[ases[i]][ases[i+1]] =1
        
        if minJ >0 and minJ < len(ases)-1 and ases[minJ-1] != ases[minJ] and ases[minJ+1] != ases[minJ] :
            if relationship[ases[minJ-1]][ases[minJ]] !='sibling-to-sibling' and relationship[ases[minJ]][ases[minJ+1]] !='sibling-to-sibling' :
                notpeering[ases[minJ]][ases[minJ+1]] =1
            else:
                notpeering[ases[minJ-1]][ases[minJ]] =1
    l = str(file.readline()).strip();

        
file.close()


file = open('/home/asemwal/raw_data/2018/proc/links_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    ases = l.split("|")
    if notpeering[ases[0]][ases[1]] != 1 and degree[ases[0]]/degree[ases[1]] < 60 and degree[ases[1]]/degree[ases[0]] > 1/60:
        relationship[ases[0]][ases[1]] = 'peer-to-peer'
        relationship[ases[1]][ases[0]] = 'peer-to-peer'
        
    l = str(file.readline()).strip();   

file.close()
print(relationship)



out = open('/home/asemwal/raw_data/2018/proc/relationships','w')
file = open('/home/asemwal/raw_data/2018/proc/links_1530662400_1530748799','r')
l = str(file.readline()).strip();
while l!='':
    ases = l.split("|")
    out.write(str(ases[0])+"|"+str(ases[1])+"|"+ relationship[ases[0]][ases[1]] +'\n')
        
    l = str(file.readline()).strip();   
file.close()
out.flush()
out.close()

"""
file = open('/home/asemwal/raw_data/2018/proc/peerpathvisibility_1530742400_1530748799','r')
purpose='verification'
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
print(time.time())
#file = open(location+year+'proc/'+f, 'r')
l = (file.readline()).strip()
path ={}
while(l !=''):
    x = l.split("|")
    ases = []
    if x[1] != '' and l.find("{") < 0:
        newases = x[1].split(" ")
        ases.append(newases[0])
        links = []
        for i in range(1, len(newases)):
            if ases[-1] != newases[i]:
                ases.append(newases[i])
        for i in range(1, len(ases)):
            links.append(relationship[ases[i-1]][ases[i]])
            #links.append(g.get_edge_data(ases[i-1],ases[i])['relationship'])
        path.update({" ".join(ases): " ".join(links)})    
    l = (file.readline()).strip()
line =''
file = open('/home/asemwal/raw_data/2018/proc/path_with_relationship','w')
for i in path.keys():
    line = i +'\n' +path[i]+'\n'
    file.write(line)
file.flush()
file.close()

line =''
file = open('/home/asemwal/raw_data/2018/proc/path_with_relationship1','w')
for i in path.keys():
    links = path[i].split(" ")
    hill = False;
    
    for j in range(0,len(links)):
        if hill == False:
            if links[j] in ('sibling-to-sibling','customer-to-provider'):
                pass
            elif links[j] in ('peer-to-peer','provider-to-customer'):
                hill = True
            else:
                line = i +'\n' +path[i]+'\n'
                file.write(line)
                break;
        elif hill == True:
            if links[j] in ('provider-to-customer','sibling-to-sibling', 'peer-to-peer'):
                pass
            else:
                line = i +'\n' +path[i]+'\n'
                file.write(line)
                break;
file.flush()
file.close()

"""