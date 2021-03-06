# -*- coding: utf-8 -*-
"""
Function: Train a LSTM model for fraud detection
Input: train.csv
Output: lstm_model.h5 model file

@author: yuwei
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
import theano
from keras.utils import np_utils
from keras.models import load_model
from sklearn.utils.class_weight import compute_class_weight, compute_sample_weight
from sklearn.metrics import recall_score, precision_score
from keras import metrics
import keras.backend as K
from sklearn.utils import shuffle 
from sklearn.metrics import confusion_matrix
from keras import regularizers
from keras.layers.wrappers import Bidirectional

from keras.layers import Conv1D, MaxPooling1D 
from keras.models import Model


import os                          #python miscellaneous OS system tool
#os.chdir("C:/work/unionpay/") #changing our directory to which we have our data file
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="0"
#lets not be annoyed by any warnings unless they are errors
import warnings
warnings.filterwarnings('ignore')

labelName="label"
cardName = "pri_acct_no_conv" 
runEpoch=20

#modelName = "lstm_reshape_5.md"

BS = 128
#runLoop = 50

#Alldata = pd.read_csv('convert_5_card_GBDT.csv')
Alldata = pd.read_csv('convert_5_card.csv')
#Alldata = pd.read_csv('convert_5_card_more.csv')




Fraud = Alldata[Alldata.label == 1]
Normal = Alldata[Alldata.label == 0]
print "Ori Fraud shape:", Fraud.shape, "Ori Normal shape:", Normal.shape

card_c_F = Fraud['pri_acct_no_conv'].drop_duplicates()#涉欺诈交易卡号

#未出现在欺诈样本中的正样本数据
fine_N=Normal[(~Normal['pri_acct_no_conv'].isin(card_c_F))]
print "True Fraud shape:", Fraud.shape, "True Normal shape:", fine_N.shape

Alldata = pd.concat([Fraud,fine_N], axis = 0)


###############################
Alldata = shuffle(Alldata)
print "Total samples:", Alldata.shape[0]
train_all,test_all=train_test_split(Alldata, test_size=0.2)


#train_all = pd.read_csv('train-converted_4.csv')
#test_all = pd.read_csv('train-converted_4.csv')



y_train2 = train_all.label
y_test2 = test_all.label
nb_classes = 2
y_train = np_utils.to_categorical(y_train2, nb_classes)
y_test = np_utils.to_categorical(y_test2, nb_classes)

X_Train = train_all.drop(labelName, axis = 1, inplace=False).drop(cardName, axis = 1, inplace=False) 
X_Test = test_all.drop(labelName, axis = 1, inplace=False).drop(cardName, axis = 1, inplace=False)  



size_data = X_Train.shape[1];
print "size_data= ", size_data

timesteps = 5
data_dim = size_data/timesteps
print "data dimension=", data_dim


sc = StandardScaler()    #MinMaxScaler()    不好

#print X_train.loc[:1]

X_train = sc.fit_transform(X_Train)
X_test = sc.transform(X_Test)

 
# Defining our classifier builder object to do all layers in once using layer codes from previous part

from keras.constraints import maxnorm
 
def classifier_builder ():
 
    classifier = Sequential()
    classifier.add(Reshape((timesteps, data_dim), input_shape=(size_data,)))
    classifier.add(Masking(mask_value= -1, input_shape=(timesteps, data_dim)))
 
    
    classifier.add(LSTM(128, input_shape=(timesteps, data_dim), recurrent_dropout=0.3, activation='sigmoid',  recurrent_activation='hard_sigmoid',   unit_forget_bias=True, return_sequences=True))
    classifier.add(Dropout(0.7))
    classifier.add(LSTM(64,  recurrent_dropout=0.3, activation='sigmoid',  recurrent_activation='hard_sigmoid',   unit_forget_bias=True))
    classifier.add(Dropout(0.7))
     
    #classifier.add(Dense(32, activation='softmax'))
    #classifier.add(Dropout(0.7))
    
    classifier.add(Dense(2, activation='softmax'))
 
    
    
    
    classifier.compile(loss='categorical_crossentropy',
              optimizer= 'Adam',                           #RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.01),                  #'rmsprop', #'rmsprop','Adam'
              metrics=[metrics.mae,"accuracy"])

    return classifier

class_weights = compute_class_weight('balanced', np.unique(y_train2), y_train2)

#class_weights_2 = compute_class_weight('balanced', np.unique(y_train), y_train)
#class_weights= dict()
#for key in {0,1}:
#        class_weights[key] = class_weights_2[key]


#Now we should create classifier object using our internal classifier object in the function above
classifier = KerasClassifier(build_fn= classifier_builder,
                             batch_size = BS,
                             nb_epoch = runEpoch) 
 

#if(os.access(modelName, os.F_OK)):
#    classifier=load_model(modelName)

from keras import backend as bk
print "Before set", bk.learning_phase()


bk.set_learning_phase(1)   #训练阶段
print "After set ", bk.learning_phase()

#classifier.fit(X_train, y_train, batch_size=BS, epochs=runEpoch, class_weight=class_weights,  validation_data=(X_test, y_test), verbose=2)
  
classifier.fit(X_train, y_train, batch_size=BS, epochs=runEpoch,  validation_data=(X_test, y_test), verbose=2)


bk.set_learning_phase(0)  #测试阶段
print "After set ", bk.learning_phase()

y_predict=classifier.predict(X_test,batch_size=BS)

print y_predict.reshape(y_predict.shape[0],1)
print y_predict.shape


print y_test.T.shape
y_test_o = y_test.T[1].reshape(y_test.T[1].shape[0],1)
print y_test_o.shape
  
confusion_matrix=confusion_matrix(y_test_o,y_predict)
print  confusion_matrix


precision_p = float(confusion_matrix[1][1])/float((confusion_matrix[0][1] + confusion_matrix[1][1]))
recall_p = float(confusion_matrix[1][1])/float((confusion_matrix[1][0] + confusion_matrix[1][1]))
 
print ("Precision:", precision_p) 
print ("Recall:", recall_p) 

if(os.access("lstm_lxr.md", os.F_OK)):
    print(classifier.summary()) 
    classifier.save('lstm_lxr.md')
else:
    print(classifier.model.summary())
    classifier.model.save('lstm_lxr.md')
    
    
#('Precision:', 0.9660511363636364)
#('Recall:', 0.9601863617111394)
 