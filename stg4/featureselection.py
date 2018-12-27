# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 20:37:17 2018

@author: asemwal
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_selection import f_regression, mutual_info_regression
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import RFECV
from sklearn.datasets import make_classification
from sklearn.svm import SVC
from sklearn.datasets import load_digits
from sklearn.feature_selection import RFE
import matplotlib.pyplot as plt

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
X = np.array(X).astype(np.float)
y = np.array(list(y['40'])).astype(np.float)


svc = SVC(kernel="linear", C=1)
rfe = RFE(estimator=svc, n_features_to_select=15, step=1)
rfe.fit(X, y)
ranking = rfe.ranking_.reshape(X[40].shape)

# Plot pixel ranking
plt.matshow(ranking, cmap=plt.cm.Blues)
plt.colorbar()
plt.title("Ranking of pixels with RFE")
plt.show()

"""
# Create the RFE object and compute a cross-validated score.
svc = SVC(kernel="linear")
# The "accuracy" scoring is proportional to the number of correct
# classifications
rfecv = RFECV(estimator=svc, step=1, cv=StratifiedKFold(2),
              scoring='accuracy')
rfecv.fit(X, y)

print("Optimal number of features : %d" % rfecv.n_features_)

# Plot number of features VS. cross-validation scores
plt.figure()
plt.xlabel("Number of features selected")
plt.ylabel("Cross validation score (nb of correct classifications)")
plt.plot(range(1, len(rfecv.grid_scores_) + 1), rfecv.grid_scores_)
plt.show()

 

f_test, _ = f_regression(X, y)
f_test /= np.max(f_test)

mi = mutual_info_regression(X, y)
mi /= np.max(mi)

plt.figure(figsize=(15, 5))
for i in range(3):
    plt.subplot(1, 3, i + 1)
    plt.scatter(X[:, i], y, edgecolor='black', s=20)
    plt.xlabel("$x_{}$".format(i + 1), fontsize=14)
    if i == 0:
        plt.ylabel("$y$", fontsize=14)
    plt.title("F-test={:.2f}, MI={:.2f}".format(f_test[i], mi[i]),
              fontsize=16)
plt.show()
"""