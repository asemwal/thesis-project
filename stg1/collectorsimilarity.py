# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
import sys
import utils
f=sys.argv[1]
#f='/home/asemwal/raw_data/2014/archive_1430747100_only'
stats = {}
purpose='collectorsimilarity'
print(time.time())
file = open(f, 'r')
location="/".join(file.name.split("/")[0:4])+'/'
year=str(file.name.split("/")[4])+'/'
l = str(file.readline()).strip()
while(l != ''):
    x = str(l).split("|");
    #if x[1] in ('R','A'):
    #    x[9]=" ".join(x[9].split(" ")[1:])
    k= utils.getKey(x , [2,4,7,9])
    try:
        if( x[1] in ( 'A','R','W')):
#            stats[x[4]+"|"+x[2]+"|"+x[5]][x[1]]+=1
            stats[k][x[1]]+=1
    except IndexError as e:
        print(l)
    except KeyError as e:
        try:
#            stats.update({x[4]+"|"+x[2]+"|"+x[5]:{'W':0,'A':0,'R':0,'S':0}})
#            stats[x[4]+"|"+x[2]+"|"+x[5]][x[1]]+=1
            
            stats.update({k:{'W':0,'A':0,'R':0}})
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
    line += str(k) + "|"+ str(stats[k]['R'])+"|"+ str(stats[k]['A'])+"|"+str(stats[k]['W']) +"\n"
out = open(location+year+'proc/'+purpose+'_'+utils.getTimeStamp(f), 'w')
out.write(line)
out.flush()
out.close()

    
