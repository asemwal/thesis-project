# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 18:48:39 2019

@author: asemwal
"""

def processfile():
    file= open('/home/asemwal/Documents/chall4.tex','r')
    write = open('/home/asemwal/Documents/chall5.tex','w')
    l= str(file.readline()).strip()
    count = 0
    while l != '' or count <= 30:
        if l == '':
            count+=1
        else:
            key = "\\subsubsection{"
            x=l.find(key)
            if x>-1:
                x+= len(key)
                #print x
                r=l.capitalize()
                #print r[x].upper()
                s=r[x].upper()
                t=key+s+r[x+1:]
                print t
                write.write(t+'\n')
            else:
                write.write(l+'\n')
            count = 0
        l= str(file.readline()).strip()
    write.close()
    file.close()            
processfile()