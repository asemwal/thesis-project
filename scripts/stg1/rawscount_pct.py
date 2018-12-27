# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
f=sys.argv[1]
stats = {}
purpose='rawscount_pct'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(l != ''):
    x = str(l).split("|");
    k= utils.getKey(x , [4,2,5,6])
    try:
        if( x[1] in ('S','A','W','R')):
#            stats[x[4]+"|"+x[2]+"|"+x[5]][x[1]]+=1
            stats[k][x[1]]+=1
    except IndexError as e:
        print(l)
    except KeyError as e:
        try:
#            stats.update({x[4]+"|"+x[2]+"|"+x[5]:{'W':0,'A':0,'R':0,'S':0}})
#            stats[x[4]+"|"+x[2]+"|"+x[5]][x[1]]+=1
            
            stats.update({k:{'W':0,'A':0,'R':0,'S':0}})
            stats[k][x[1]]+=1
        except KeyError as e:
            print(l)
            print(e)
        except IndexError:
            pass
        pass
    l = str(file.readline()).strip()
line=""
print(time.time())
for k in stats.keys():
    line += str(k) + "|"+ str(stats[k]['R'])+"|"+ str(stats[k]['A'])+"|"+str(stats[k]['W'])+"|" +str(stats[k]['S'])+"\n"
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()

    
