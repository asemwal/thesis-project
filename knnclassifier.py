# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 23:11:50 2018

@author: asemwal
"""
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, precision_score, recall_score,
                             f1_score)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import train_test_split



def plot_calibration_curve(est, name, fig_index):
    """Plot calibration curve for est w/o and with calibration. """
    # Calibrated with isotonic calibration
    isotonic = CalibratedClassifierCV(est, cv=2, method='isotonic')

    # Calibrated with sigmoid calibration
    sigmoid = CalibratedClassifierCV(est, cv=2, method='sigmoid')

    # Logistic regression with no calibration as baseline
    lr = LogisticRegression(C=1., solver='lbfgs')

    fig = plt.figure(fig_index, figsize=(10, 10))
    ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((3, 1), (2, 0))

    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    for clf, name in [(lr, 'Logistic'),
                      (est, name),
                      (isotonic, name + ' + Isotonic'),
                      (sigmoid, name + ' + Sigmoid')]:
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        if hasattr(clf, "predict_proba"):
            prob_pos = clf.predict_proba(X_test)[:, 1]
        else:  # use decision function
            prob_pos = clf.decision_function(X_test)
            prob_pos = \
                (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())
    
        clf_score = brier_score_loss(y_test, prob_pos, pos_label=y.max())
        print("%s:" % name)
        print("\tBrier: %1.3f" % (clf_score))
        print("\tPrecision: %1.3f" % precision_score(y_test, y_pred))
        print("\tRecall: %1.3f" % recall_score(y_test, y_pred))
        print("\tF1: %1.3f\n" % f1_score(y_test, y_pred))

        fraction_of_positives, mean_predicted_value = \
            calibration_curve(y_test, prob_pos, n_bins=10)

        ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                 label="%s (%1.3f)" % (name, clf_score))

        ax2.hist(prob_pos, range=(0, 1), bins=10, label=name,
                 histtype="step", lw=2)

    ax1.set_ylabel("Fraction of positives")
    ax1.set_ylim([-0.05, 1.05])
    ax1.legend(loc="lower right")
    ax1.set_title('Calibration plots  (reliability curve)')

    ax2.set_xlabel("Mean predicted value")
    ax2.set_ylabel("Count")
    ax2.legend(loc="upper center", ncol=2)

    plt.tight_layout()
import numpy as np
import pandas as pd
file_path='/home/asemwal/raw_data/bgpdata/cmd/data2.tmp'
file_path = '/home/asemwal/raw_data/2018/proc/traindata.txt_4'
file_path='/home/asemwal/thesis/bgp-python/data/simulator/myrun/testdata_process_1'
file_path ='/home/asemwal/raw_data/evam_file_dummy'
#y = pd.read_csv(file_path,  usecols=[43])
#([1, 9, 1, 1, 1, 1, 1, 5, 1, 8, 1, 1, 1, 1, 4, 1, 7, 1, 1, 1, 2, 3, 6])
y = pd.read_csv(file_path, header=None, sep='|',  usecols=[31])
  #4,    6,7,8,9,10,      12,    14,15,16,17,  19,   21,22,23

df = pd.read_csv(file_path, header=None, sep='|',  usecols=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30])
#df = pd.read_csv(file_path,  usecols=[4,    6,7,8,9,10,      12,    14,15,16,17,  19,   21,22,23])
x=df.to_csv().split("\n")
X = [] 
for i in range(1, len(x)-1):
    X.append(list(x[i].split(",")[1:]))   
X = np.array(X).astype(np.float)
y = np.array(list(y[31])).astype(np.float)

from sklearn.neighbors import KNeighborsClassifier
k=7
classifier = KNeighborsClassifier( n_neighbors=k)
print("{}-Neighbour Classifier".format(k))
i=1
d=110000
X_train, X_test, y_train, y_test = X[0:d], X[d:], y[0:d], y[d:]
plot_calibration_curve(classifier, "knn classifier", i)
for d in range(50000000,902,50):
    X_train, X_test, y_train, y_test = X[0:d], X[d:], y[0:d], y[d:]
    print("{} train data size".format(d))
    #classifier.fit(np_X[0:d],np_y[0:d])
    #print("{}|{}".format(d,classifier.score(np_X[d:],np_y[d:])))
    plot_calibration_curve(KNeighborsClassifier(), "knn classifier", i)
    i+=1
    
  



# Plot calibration curve for Gaussian Naive Bayes
#plot_calibration_curve(KNeighborsClassifier(), "knn classifier", 1)

#plt.show()




"""
X = [[0,0,0,2,218,70,2621,2],
[0,0,0,1,218,70,2621,2],
[0,0,0,2,60,16,5801,3],
[0,0,0,1,0,0,0,1],
[0,0,3,7,0,0,0,1],
[3,0,0,3,3,8,356,6],
[0,0,0,2,0,0,0,2],
[29,36,80,32,40,0,0,21],
[0,0,0,1,218,70,2621,2],
[0,0,1,4,218,70,2621,2],
[0,0,14,6,218,70,2621,2],
[0,0,0,8,3,8,356,6],
[0,0,1,7,3,8,356,6],
[0,0,14,6,218,70,2621,2],
[0,0,3,7,0,0,0,1],
[0,0,0,1,0,0,5,2],
[1,0,1,17,30,2,18,29],
[0,0,0,3,218,70,2621,2],
[0,0,0,1,218,70,2621,2],
[0,0,0,2,218,70,2621,2],
[44,0,5,38,3,1,38,8],
[0,0,0,2,84,8,130,77],
[75,30,1130,14,0,0,3,11],
[4,0,53,4,155,13,82,72],
[0,0,0,3,15,11,9,22],
[0,0,0,2,218,70,2621,2],
[11,15,2384,5,26,0,0,8],
[5,5,56,7,0,0,0,1],
[20,0,45,13,218,70,2621,2],
[0,0,1,4,84,8,130,77],
[26,0,0,16,29,36,80,32],
[1,1,50,2,30,2,18,29],
[15,2,49,38,49,0,1,31],
[0,0,0,6,4,50,1704,3],
[0,0,0,1,218,70,2621,2],
[19,34,163,15,0,1,108,7],
[0,0,0,1,218,70,2621,2],
[0,0,2,20,3,8,356,6],
[0,0,0,1,3,8,356,6],
[1,1,15,10,0,0,1,4],
[0,0,0,4,3,8,356,6],
[50,1,4,34,3,8,356,6],
[0,0,0,12,0,0,0,1],
[0,0,2,14,0,1,10,4],
[0,0,0,9,3,8,356,6],
[0,0,2,14,749,46,286,23],
[0,0,0,3,3,8,356,6],
[0,0,0,2,0,0,0,1],
[0,0,0,2,0,1,5,20],
[29,4,4,34,408,11,13,21],
[0,0,2,7,0,0,1,4],
[0,0,0,2,14,26,2532,4],
[0,1,44,7,3,8,356,6],
[411,26,67,36,0,0,0,2],
[3,0,1,15,65,2,43,45],
[0,0,1,12,3,8,356,6],
[1,1,20,9,1,1,11,7],
[4,0,3,12,0,0,0,1],
[0,0,0,2,1,2,10,6]]
y = [1,
0,
0,
0,
1,
0,
1,
1,
0,
0,
0,
0,
1,
0,
0,
0,
1,
0,
1,
1,
0,
0,
0,
1,
0,
1,
0,
0,
0,
0,
1,
1,
1,
0,
0,
0,
1,
0,
0,
0,
1,
1,
0,
1,
0,
1,
0,
1,
0,
1,
1,
1,
1,
0,
0,
0,
1,
1,
0]
"""

"""
print(classifier.predict_proba([np_X[d+68]]))
print(classifier.predict_proba([np_X[d+68]]))
print(classifier.predict_proba([np_X[d+69]]))
print(classifier.predict_proba([np_X[d+70]]))
print(classifier.predict_proba([np_X[d+71]]))
print(classifier.predict_proba([np_X[d+100]]))
print(classifier.predict_proba([np_X[d+198]]))

print(classifier.predict([np_X[d+68]]))
print(classifier.predict([np_X[d+68]]))
print(classifier.predict([np_X[d+69]]))
print(classifier.predict([np_X[d+70]]))
print(classifier.predict([np_X[d+71]]))
print(classifier.predict([np_X[d+100]]))
print(classifier.predict([np_X[d+198]]))


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
"""