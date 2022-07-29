 
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import numpy as np
import math

def log_reg():
    spotify_features = ['energy', 'liveness', 'tempo', 'speechiness',
                                            'acousticness', 'instrumentalness', 'danceability',
                                            'loudness', 'valence']
    data = pd.read_csv('/Users/akshay/Desktop/Django/Backend/api/ML/final_dataset.csv').drop(['Unnamed: 0'],axis=1)
    data = data[data.mood.isin(['Aggressive','Energetic']) == False]
    trainx, testx, trainy, testy = train_test_split(data[spotify_features], data['mood'], test_size = 0.33, random_state = 42, stratify=data['mood'])


    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(trainx[spotify_features])
    test_scaled = scaler.fit_transform(testx[spotify_features])

    logreg = LogisticRegression(max_iter=2000)
    logreg.fit(train_scaled, trainy)
    print (accuracy_score(logreg.predict(train_scaled), trainy))

    scores = cross_val_score(logreg, train_scaled, trainy, cv=5)
    print (scores.mean())

    params = {"C" : np.logspace(-6, 3, 10)}
    clf = GridSearchCV(logreg, params)
    clf.fit(train_scaled, trainy)
    print (clf.best_estimator_.C)
    print (clf.best_score_)
   
    logreg = LogisticRegression(max_iter=2000, C=0.1)
    logreg.fit(train_scaled, trainy)
    preds = clf.predict(test_scaled)
    print (accuracy_score(preds, testy))

    fi = pd.DataFrame(clf.best_estimator_.coef_, columns=spotify_features)
    pow(math.e, fi)
    fo = fi.set_axis(logreg.classes_, axis=0)
    fo
    fo.idxmax(axis=1)



log_reg()