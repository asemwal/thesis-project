# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 15:48:13 2018

@author: asemwal
"""

from os import listdir
from os.path import isfile, join
mypath ='/home/asemwal/raw_data/experiments/graphs'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.find("graph") > -1]