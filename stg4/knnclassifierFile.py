# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 00:31:05 2018

@author: asemwal
"""

k = 3
file_path='/home/asemwal/raw_data/bgpdata/cmd/data2.tmp'
y = pd.read_csv(file_path, header=None, usecols=[8])
df = pd.read_csv(file_path, header=None, usecols=[0,1,2,3,4,5,6,7])
from sklearn.neighbors import KNeighborsClassifier
neigh = KNeighborsClassifier(n_neighbors=k)

x=df.to_csv().split("\n")
X = [] 
for i in range(1, len(x)-1):
    X.append(list(x[i].split(",")[1:]))   

y = list(y[8])
d=55
neigh.fit(X[0:d],y[0:d])
print(neigh.score(X[d:],y[d:]))
print(neigh.predict_proba([[0,0,0,3,0,0,2,3]]))
print(neigh.predict_proba([[31,0,1,28,0,1,21,6]]))
print(neigh.predict_proba([[0,1,44,7,3,8,356,6]]))
print(neigh.predict_proba([[0,0,0,2,0,1,5,20]]))
print(neigh.predict_proba([[5,5,56,7,14,7,20,25]]))
print(neigh.predict_proba([[0,0,0,2,218,70,2621,2]]))
print(neigh.predict_proba([[0,0,0,4,218,70,2621,2]]))

print(neigh.predict([[0,0,0,3,0,0,2,3]]))
print(neigh.predict([[31,0,1,28,0,1,21,6]]))
print(neigh.predict([[0,1,44,7,3,8,356,6]]))
print(neigh.predict([[0,0,0,2,0,1,5,20]]))
print(neigh.predict([[5,5,56,7,14,7,20,25]]))
print(neigh.predict([[0,0,0,2,218,70,2621,2]]))
print(neigh.predict([[0,0,0,4,218,70,2621,2]]))
