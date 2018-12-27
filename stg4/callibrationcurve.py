# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 09:30:28 2018

@author: asemwal
"""

print(__doc__)

# Author: Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#         Jan Hendrik Metzen <jhm@informatik.uni-bremen.de>
# License: BSD Style.
from sklearn.neighbors import KNeighborsClassifier

import numpy as np
import pandas as pd
file_path='/home/asemwal/raw_data/bgpdata/cmd/data2.tmp'
file_path = '/home/asemwal/raw_data/2018/proc/traindata.txt_4'
file_path='/home/asemwal/thesis/bgp-python/data/simulator/myrun/testdata_process_1'
y = pd.read_csv(file_path,  usecols=[40])
df = pd.read_csv(file_path,  usecols=[4,5,6,7,12,13,14,15,16,17,18,18,24,25,26,27,28,29,30,31,36,37,38,39])
x=df.to_csv().split("\n")
X = [] 
for i in range(1, len(x)-1):
    X.append(list(x[i].split(",")[1:]))   
np_X = np.array(X).astype(np.float)
np_y = np.array(list(y['40'])).astype(np.float)
d=50

import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (brier_score_loss, precision_score, recall_score,
                             f1_score)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import train_test_split


# Create dataset of classification task with many redundant and few
# informative features

X, y = datasets.make_classification(n_samples=100000, n_features=20,
                                    n_informative=2, n_redundant=10,
                                    random_state=42)
X ,y= np_X,np_y
#X_train, X_test, y_train, y_test = train_test_split(np_X, np_y, test_size=0.1, random_state=42)
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.99, random_state=42)
X_train, X_test, y_train, y_test = np_X[0:d], np_X[d:], np_y[0:d], np_y[d:]


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

# Plot calibration curve for Gaussian Naive Bayes
#plot_calibration_curve(GaussianNB(), "Naive Bayes", 1)
plot_calibration_curve(KNeighborsClassifier(n_neighbors=7), 'KNN Classifier', 3 )
# Plot calibration curve for Linear SVC
#plot_calibration_curve(LinearSVC(), "SVC", 2)

plt.show()