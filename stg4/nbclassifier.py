# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 00:31:05 2018

@author: asemwal
"""

import numpy as np
import pandas as pd
file_path='/home/asemwal/raw_data/bgpdata/cmd/data2.tmp'
file_path = '/home/asemwal/raw_data/2018/proc/traindata.txt_4'
file_path='/home/asemwal/thesis/bgp-python/data/simulator/myrun/testdata_process_1'
y = pd.read_csv(file_path,  usecols=[40])
df = pd.read_csv(file_path ,  usecols=[4,5,6,7,12,13,14,15,16,17,18,18,24,25,26,27,28,29,30,31,36,37,38,39])
#df = pd.read_csv(file_path,header=None, usecols=[1,2,3])
from sklearn.naive_bayes import GaussianNB
classifier = GaussianNB()

x=df.to_csv().split("\n")
X = [] 
for i in range(1, len(x)-1):
    X.append(list(x[i].split(",")[1:]))   
np_X = np.array(X).astype(np.float)
np_y = np.array(list(y['40'])).astype(np.float)
d=70
for d in range(5,902,50):
    classifier.fit(np_X[0:d],np_y[0:d])
    print("{}|{}".format(d,classifier.score(np_X[d:],np_y[d:])))


"""
print(classifier.score(np_X[d:d+100],np_y[d:d+100]))
print(classifier.predict_proba([np_X[d+68]]))
print(classifier.predict_proba([np_X[d+69]]))
print(classifier.predict_proba([np_X[d+70]]))
print(classifier.predict_proba([np_X[d+71]]))
print(classifier.predict_proba([np_X[d+100]]))
print(classifier.predict_proba([np_X[d+198]]))

print(classifier.predict([np_X[d+68]]))
print(classifier.predict([np_X[d+69]]))
print(classifier.predict([np_X[d+70]]))
print(classifier.predict([np_X[d+71]]))
print(classifier.predict([np_X[d+100]]))
print(classifier.predict([np_X[d+198]]))
"""