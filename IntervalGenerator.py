# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 14:08:08 2018

@author: asemwal
"""


from datetime import datetime
from calendar import timegm
from time import gmtime, strftime
import time


def unix_time(dttm=None):
    if dttm is None:
       dttm = datetime.utcnow()

    return timegm(dttm.utctimetuple())


if __name__ == '__main__':
    year = range(2014,2019)  
    month = 7
    day = 4
    location='/home/asemwal/raw_data/'
    filename='raw'
    for i in year:
        timeA = int(unix_time(datetime(i, month, day, 00, 00, 00  )) )
        timeB = int(unix_time(datetime(i, month, day, 23, 59, 59  )) )
        print("{} -> {}".format(timeA,timeB))
        start= timeA
        end=0
        while(start < timeB-10000):
            end=start+9999;
            print("bgpreader -m  -w {},{} >> {}/{}_{}_{} &".format(start,end,location+str(i),filename,start,end))
            start=end+1
        print("bgpreader -m -w {},{} >> {}/{}_{}_{} &".format(start,timeB,location+str(i),filename,start,timeB))
        
        
