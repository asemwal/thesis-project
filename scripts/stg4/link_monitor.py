# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:04:36 2018

@author: asemwal
"""
import time
import sys
import utils
stats = {}
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


f=sys.argv[1]
purpose='links'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(str(l).strip() !=''):
    peerip=l.split('|')[0]
    if peerip.find(':') == -1:
        peer=geoip[int(peerip.split('.')[0])][int(peerip.split('.')[1])][int(peerip.split('.')[2])]
    ases= l.split("|")[1].split(" ")
    for i in range(1, len(ases)):
        try:
            if ases[i-1] != ases[i] and peerip.find(":") == -1:
                stats[peer+"_"+ases[i-1]+"|"+peer+"_"+ases[i] ] += 1
        except KeyError as e:
            stats.update({peer+"_"+ases[i-1]+"|"+peer+"_"+ases[i]  : 1})
    l = str(file.readline()).strip()
line=""
line=""
print(time.time())
while(True):
    try:
        x = stats.popitem()
        if x[0].strip() != '':
            #line += str(k) + "|"+ str(stats[k])+"\n"
            line += str(x[0].strip())+"|"+ str(x[1])+"\n"
    except KeyError as e:
        break;
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')


out.write(line)
out.flush()
out.close()