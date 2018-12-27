# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:50:15 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:04:36 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
"""
geoip={}
geofile='/home/asemwal/Downloads/geolite/GeoIPCountryWhois.csv'
for i in range(0,256):
    geoip.update({i:{}})
    for j in range(0,256):
        geoip[i].update({j:{}})
        for k in range(0,256):
            geoip[i][j].update({k:".".join([str(i), str(j), str(k),'*'])})
file = open(geofile, 'r')
l = str(file.readline()).strip().replace('"','')
while(str(l).strip() !=''):
    for i in range(int(l.split(',')[0].split('.')[0]),1+int(l.split(',')[1].split('.')[0])):
        for j in range(int(l.split(',')[0].split('.')[1]),1+int(l.split(',')[1].split('.')[1])):
            for k in range(int(l.split(',')[0].split('.')[2]),1+int(l.split(',')[1].split('.')[2])):
                geoip[i][j][k]= l.replace('"','').split(",")[4]
            
    l = str(file.readline()).strip().replace('"','')


file.close()
"""
if len(sys.argv) >  1:
    f=sys.argv[1]
else:
    f = '/home/asemwal/raw_data/2018/old_proc/spalgopaths_1_2'
purpose='spalgolinks'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    ases=l.split(" ")
    peer=ases[0]
    for i in range(1, len(ases)):
        try:
            if ases[i-1] != ases[i] :
                stats[peer+"|"+ases[i-1]+"|" +ases[i] ] += 1
        except KeyError as e:
            stats.update({peer+"|"+ases[i-1]+"|" +ases[i]  : 1})
    l = str(file.readline()).strip()
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            #line += str(k) + "|"+ str(stats[k])+"\n"
            line += str(x[0].strip())+"\n"
    except KeyError as e:
        break;
print line
out = open(location+year+'old_proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')


out.write(line)
out.flush()
out.close()
