# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 21:18:18 2023

@author: veerg
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 23:32:37 2023

@author: veerg
"""

'''this program trains a deep neural network on the final dataset.
To choose the architecture of the model, a 80/20 training-test-split was applied,
but in this version of the code, the model is trained on the 2012/13 - 2021/22 seasons
and tested only on the 2022/23 season just as a fun illustration of how the model 
performs on last seasons data'''

import sys
sys.path.append(r'C:/Users/veerg/OneDrive/Documents/Premier League Predictor')
from constants import *
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.regularizers import l2

#importing the final data
raw_data = pd.read_excel(final_data) 
unprocessed_data = raw_data.drop(raw_data.columns[0], axis = 1)

'''this part of the code regularizes transfer values on the basis of season.
Otherwise, top teams from 2012/13 have similar transfer values as bottom teams from recent years
due to inflation. Transfer value is used as a metric for relative team quality, so each transfer value
is divided by the average transfer values of premier league teams from that season so that top teams from 
different seasons are treated the same with regards to this particular metric'''

avg_transfer_vals = {}

seasons = list(unprocessed_data['season'].unique())

for season in seasons:
    relevant_df = unprocessed_data[unprocessed_data['season'] == season]
    home_mean = relevant_df['Home Transfer Value'].mean()
    away_mean = relevant_df['Away Transfer Value'].mean()
    mean = (home_mean + away_mean)/2
    
    avg_transfer_vals[season] = mean

regularized_home_tvals = []
regularized_away_tvals = []

for i in range(unprocessed_data.shape[0]):
    regularized_home_tvals.append(unprocessed_data.loc[i]['Home Transfer Value']/avg_transfer_vals[unprocessed_data.loc[i]['season']])
    regularized_away_tvals.append(unprocessed_data.loc[i]['Away Transfer Value']/avg_transfer_vals[unprocessed_data.loc[i]['season']])

unprocessed_data['Home Transfer Value'] = regularized_home_tvals
unprocessed_data['Away Transfer Value'] = regularized_away_tvals


remove_nokeep_mask = unprocessed_data['keep row?'] == 1
processed_data = unprocessed_data[remove_nokeep_mask]


#adding class labels: 0 for home team win, 1 for a draw, and 2 for away team win
length = processed_data.shape[0]


WDL = [] #WDL means Win Draw Loss, and is a new column that contains the class labels

for i in range(length):
    if processed_data.iloc[i]['Home Team Score'] > processed_data.iloc[i]['Away Team Score']:
        WDL.append(0)
    elif processed_data.iloc[i]['Home Team Score'] == processed_data.iloc[i]['Away Team Score']:
        WDL.append(1)
    elif processed_data.iloc[i]['Home Team Score'] < processed_data.iloc[i]['Away Team Score']:
        WDL.append(2)

processed_data['WDL'] = WDL

'''splitting data into training and testing data. For the purposes of this demonstration,
the model is trained on 10 seasons of data and tested only on last seasons data. If one were testing
more formally, as was done to pick the best neural network architechture, it would be better to test on 2-3 seasons and 
train on the rest'''

testing_data_df = processed_data[processed_data['season'] == '22/23']
training_data_df = processed_data[processed_data['season'] != '22/23']

testing_data = testing_data_df.drop(['Home Team Score', 'Away Team Score', 'season', 'Home Team', 'Away Team'], axis = 1)
training_data = training_data_df.drop(['Home Team Score', 'Away Team Score', 'season', 'Home Team', 'Away Team'], axis = 1)

#change data into numpy arrays from pandas DFs
testing_data = testing_data.values
training_data = training_data.values

# Split the data into input features and outputs
X_test, X_train = testing_data[:, :-1], training_data[:, :-1]
y_test, y_train = testing_data[:, -1], training_data[:, -1]




#applying z-score normalization to all features
scaler = StandardScaler()
scaled_X_train = scaler.fit_transform(X_train)
scaled_X_test = scaler.transform(X_test)



#fitting and training model
tf.random.set_seed(55)
lambda_coeff = 0.01

NN_model = Sequential([
    Dense(units = 100, activation = "relu", kernel_regularizer=l2(lambda_coeff)),
    Dense(units = 75, activation = "relu", kernel_regularizer=l2(lambda_coeff)),
    Dense(units = 45, activation = "relu", kernel_regularizer=l2(lambda_coeff)),
    Dense(units = 30, activation = "relu", kernel_regularizer=l2(lambda_coeff)),
    Dense(units = 15, activation = "relu", kernel_regularizer=l2(lambda_coeff)),
    Dense(units = 3, activation = "softmax", kernel_regularizer=l2(lambda_coeff))
    
    ]
    )

NN_model.compile(optimizer='adam',
              loss=SparseCategoricalCrossentropy())

NN_model.fit(scaled_X_train, y_train, epochs=300)

y_pred = NN_model.predict(scaled_X_test)



y_pred_assigned = tf.argmax(y_pred, axis = 1) #this variable converts softmax probability arrays to class assignments
print('\n\n\n')
print("accuracy: " + str(accuracy_score(y_test, y_pred_assigned)))
cm = confusion_matrix(y_test, y_pred_assigned)
#print(cm)

#unprint the confusion matrix for a more detailed breakdown of results and model performance


score_col = []
prob_of_win = []
prob_of_draw = []
prob_of_loss = []
correct = []


#preparing the final output sheet: Last Season Predictions.xlsx
for i in range(testing_data.shape[0]):
    home_score = str(testing_data_df.iloc[i]['Home Team Score'])
    away_score = str(testing_data_df.iloc[i]['Away Team Score'])
    
    score = home_score + "-" + away_score
    score_col.append(score)
    
    prob_of_win.append(y_pred[i][0])
    prob_of_draw.append(y_pred[i][1])
    prob_of_loss.append(y_pred[i][2])
    
    if y_pred_assigned[i] == y_test[i]:
        correct.append(1)
    else:
        correct.append(0)
        
    

testing_data = testing_data_df[['Home Team', 'Away Team']]

testing_data['Score'] = score_col
testing_data['Probability of Home Win'] = prob_of_win
testing_data['Probability of Draw'] = prob_of_draw
testing_data['Probability of Away Win'] = prob_of_loss
testing_data['Correct Prediction (Yes or No)'] = correct
testing_data['Result'] = y_test

testing_data.to_excel(last_season_predictions)
