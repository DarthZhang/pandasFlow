# -*- coding: utf-8 -*-
"""
Created on Fri Jul 07 08:30:44 2017

@author: lixurui
"""

import pandas as pd                #data analysing tool for python
import matplotlib.pyplot as plt    #data visualising tool for python
import numpy as np
np.random.seed(1234)

from IPython.display import display
from sklearn.preprocessing import StandardScaler,MinMaxScaler                   # for normalization of our data
from keras.wrappers.scikit_learn import KerasClassifier            #package allowing keras to work with python
from sklearn.model_selection import cross_val_score, GridSearchCV  #using Kfold and if needed, GridSearch object in analysis
from sklearn.utils import shuffle                                  # shuffling our own made dataset
from keras.models import Sequential                                # linear layer stacks model for keras
from sklearn.model_selection import train_test_split
from keras.layers import Dense, Dropout
from keras.layers.core import Dense, Dropout, Activation,Flatten, Reshape
from keras.layers import Embedding, Masking
from keras.layers import LSTM
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.datasets import mnist
from keras.layers import BatchNormalization
from sklearn.svm import SVC
 
from keras.utils import np_utils
from keras.models import load_model
from sklearn.utils.class_weight import compute_class_weight, compute_sample_weight
from sklearn.metrics import recall_score, precision_score
from keras import metrics
import keras.backend as K
 
from sklearn.metrics import confusion_matrix
from keras import regularizers
from sklearn.ensemble import RandomForestClassifier
 

labelName="label" 
runEpoch=20
AE_Epochs = 20


modelName = "lstm_reshape_5.md"

BS = 256
#runLoop = 50

Alldata = pd.read_csv('LSTM_converted_5.csv')
Alldata = shuffle(Alldata)

train_all,test_all=train_test_split(Alldata, test_size=0.2)


#train_all = pd.read_csv('train-converted_4.csv')
#test_all = pd.read_csv('train-converted_4.csv')



y_train = train_all.label
y_test = test_all.label

X_train = train_all.drop(labelName, axis = 1, inplace=False) 
X_test = test_all.drop(labelName, axis = 1, inplace=False) 

print X_train.columns

print len(X_train.columns)

size_data = X_train.shape[1];
print "size_data= ", size_data

timesteps = 5
data_dim = size_data/timesteps
print "data dimension=", data_dim


sc = MinMaxScaler()      #StandardScaler()

#print X_train.loc[:1]

X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

 
# Defining our classifier builder object to do all layers in once using layer codes from previous part


Size1 = 256
Size2 = 128
Size3 = 64

inputSize =size_data


Encoder1 = Sequential([Dense(Size1, input_dim=inputSize, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])
Encoder2 = Sequential([Dense(Size2, input_dim=Size1, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])
Encoder3 = Sequential([Dense(Size3, input_dim=Size2, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])


#解码器为：
Decoder1 = Sequential([Dense(Size2, input_dim=Size3, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])
Decoder2 = Sequential([Dense(Size1, input_dim=Size2, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])
Decoder3 = Sequential([Dense(inputSize, input_dim=Size1, activation='relu'  )])                # , activity_regularizer=regularizers.l1(10e-5))])

#autoencoder为：
Autoencoder = Sequential()
Autoencoder.add(Encoder1)
Autoencoder.add(Encoder2)
Autoencoder.add(Encoder3)

Autoencoder.add(Decoder1)
Autoencoder.add(Decoder2)
Autoencoder.add(Decoder3)
 
#Autoencoder.compile(optimizer='rmsprop', loss='mse', metrics=[metrics.mae,"accuracy"])
Autoencoder.compile(optimizer='rmsprop', loss='mse')
#Autoencoder.compile(optimizer='adam', loss='mse')
#进行训练：
Autoencoder.fit(X_train, X_train, nb_epoch=AE_Epochs, shuffle=True, validation_data=(X_test, X_test))



encoder1_train = Encoder1.predict(X_train)
encoder2_train = Encoder2.predict(encoder1_train)
X_train = Encoder3.predict(encoder2_train)
 
encoder1_test = Encoder1.predict(X_test)
encoder2_test = Encoder2.predict(encoder1_test)
X_test = Encoder3.predict(encoder2_test)
 

   



def classifier_builder ():
 
    classifier = Sequential()
    classifier.add(Reshape((timesteps, data_dim), input_shape=(size_data,)))
    classifier.add(Masking(mask_value= -1, input_shape=(timesteps, data_dim)))
    #classifier.add(LSTM(128))#               , input_shape=(timesteps, data_dim)))
    #classifier.add(LSTM(256, input_shape=(timesteps, data_dim),     activation='sigmoid',  recurrent_activation='hard_sigmoid',   unit_forget_bias=True, return_sequences=True))
    #classifier.add(Dropout(0.6))
    classifier.add(LSTM(128, input_shape=(timesteps, data_dim),     activation='sigmoid',  recurrent_activation='hard_sigmoid',   unit_forget_bias=True, return_sequences=True))
    classifier.add(Dropout(0.6))
    classifier.add(LSTM(64, input_shape=(timesteps, data_dim),     activation='sigmoid',  recurrent_activation='hard_sigmoid',   unit_forget_bias=True))   # activation='sigmoid', recurrent_activation='hard_sigmoid', unit_forget_bias=True, kernel_regularizer=regularizers.l2(0.01), recurrent_regularizer=regularizers.l2(0.01), bias_regularizer=regularizers.l1(0.01), activity_regularizer=regularizers.l1(0.01)))
    classifier.add(Dropout(0.6))
    classifier.add(Dense(1, activation='sigmoid'))  #'tanh'  'sigmoid'
 
    
    
    
    classifier.compile(loss='binary_crossentropy',
              optimizer= 'Adam',                           #RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.01),                  #'rmsprop', #'rmsprop','Adam'
              metrics=[metrics.mae,"accuracy"])

    return classifier

class_weights = compute_class_weight('balanced', np.unique(y_train), y_train)
print "class weights = ", class_weights

#Now we should create classifier object using our internal classifier object in the function above
classifier = KerasClassifier(build_fn= classifier_builder,
                             batch_size = BS,
                             nb_epoch = runEpoch) 
 

#if(os.access(modelName, os.F_OK)):
#    classifier=load_model(modelName)

classifier.fit(X_train, y_train, batch_size=BS, epochs=runEpoch, class_weight=class_weights, validation_data=(X_test, y_test), verbose=2)
  
y_predict=classifier.predict(X_test,batch_size=BS)
y_predict =  [j[0] for j in y_predict]
y_predict = np.where(np.array(y_predict)<0.5,0,1)
 
precision = precision_score(y_test, y_predict, average='macro') 
recall = recall_score(y_test,y_predict, average='macro') 
print ("Precision:", precision) 
print ("Recall:", recall) 

confusion_matrix=confusion_matrix(y_test,y_predict)
print  confusion_matrix

#if(os.access(modelName, os.F_OK)):
#    print(classifier.summary()) 
#    classifier.save(modelName)
#else:
#    print(classifier.model.summary())
#    classifier.model.save(modelName)

