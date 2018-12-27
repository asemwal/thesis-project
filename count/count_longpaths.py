# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:22:29 2018

@author: asemwal
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 01:35:45 2018

@author: asemwal
"""
import time
stats = {}
#file = open('/home/asemwal/thesis/bgp/archive_1530729999_1530739999', 'r')
#stats collected
print(time.time())
#file = open('/home/asemwal/thesis/bgpreader/archive_1530709999_1530729998', 'r')
file = open('/home/asemwal/thesis/bgpreader/proc/longpaths', 'r')
c=0;
l = file.readline()
while(str(l).strip() !=''):
    x = str(l).strip().split("|");
    try:
        stats[ x[0] ] += len(x[1].split(" "))-1
    except KeyError as e:
        stats.update({x[0]: len(x[1].split(" "))-1})
    l = file.readline()
line=""
print(time.time())
for k in stats.keys():
    line += str(k) + "|"+ str(stats[k])+"\n"
out = open('/home/asemwal/thesis/bgpreader/proc/longpaths_count', 'w')
out.write(line)
out.flush()
out.close()

#print(stats)


"""
    x = str(l).split("|");
    try:
        stats[x[0]]+=x[1]
    except IndexError as e:
        print(l)
        pass
    except KeyError as e:
        try:
            stats.update({x[0]:x[1]})
            stats[x[0]]+=x[1]
        except KeyError as e:
            print(l)
            print(e)
            pass
        except IndexError:
            pass
        pass
"""
