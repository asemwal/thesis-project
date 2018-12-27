# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 20:36:30 2018

@author: asemwal
"""

file = open('/home/asemwal/result','r')
l = str(file.readline()).strip()
found = False
end =True
count = 0;
while(str(l).strip() !=''):
    if l.find('asemwal')> -1 and found == False:
        found = True
    elif l.find('asemwal')> -1 and found == True:
        count+=1
    elif l.find('asemwal' ) < 0 :
        found = False
    
    l = str(file.readline()).strip()
    