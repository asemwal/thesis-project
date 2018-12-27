# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:06:26 2018

@author: asemwal
"""

import pandas as pd

df = pd.read_csv('/home/asemwal/raw_data/2016/peerdistribution_1467590400_1467676799_dedup',sep='|', header=None)
collector = df.groupby([0])