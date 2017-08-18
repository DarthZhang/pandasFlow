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
 
from sklearn.model_selection import cross_val_score, GridSearchCV  #using Kfold and if needed, GridSearch object in analysis
from sklearn.utils import shuffle                                  # shuffling our own made dataset
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.utils.class_weight import compute_class_weight, compute_sample_weight
from sklearn.metrics import recall_score, precision_score
 
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score as auc 

import tensorflow as tf
 
labelName="label" 
runEpoch=200000
 
out_dim = 2
BS = 256
#runLoop = 50

Alldata = pd.read_csv('LSTM_converted_5.csv')
Alldata = shuffle(Alldata)

train_all,test_all=train_test_split(Alldata, test_size=0.2)


#train_all = pd.read_csv('train-converted_4.csv')
#test_all = pd.read_csv('train-converted_4.csv')



y_train = train_all.label
y_test = test_all.label


#ex_dict = {0:[0,1],1:[1,0]}
 
#y_train = y_train.map(lambda x: ex_dict[x]) 
#y_test = y_test.map(lambda x: ex_dict[x])

y_train = np.array([1-y_train, y_train]).T
y_test = np.array([ 1 - y_test, y_test]).T

#print y_train.shape, y_test.shape

X_train = train_all.drop(labelName, axis = 1, inplace=False) 
X_test = test_all.drop(labelName, axis = 1, inplace=False) 

print X_train.columns

print len(X_train.columns)

size_data = X_train.shape[1];
print "size_data= ", size_data

timesteps = 5
data_dim = size_data/timesteps
print "data dimension=", data_dim


sc = StandardScaler()    #MinMaxScaler()    不好

#print X_train.loc[:1]

X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

num_train = X_train.shape[0]
 

index_in_epoch = 0
contents = X_train
labels = y_train
#https://stackoverflow.com/questions/41454511/tensorflow-how-is-dataset-train-next-batch-defined
def get_next_batch(batch_size, index_in_epoch, contents, labels):
    start = index_in_epoch
    index_in_epoch = index_in_epoch + batch_size
    contents = X_train
    labels = y_train
    if index_in_epoch > num_train:
      # Shuffle the data
      perm = np.arange(num_train)
      perm = np.random.shuffle(perm)
      contents = X_train[perm]
      labels = y_train[perm]
      # Start next epoch
      start = 0
      index_in_epoch = batch_size
      
    end = index_in_epoch
    return contents[start:end], labels[start:end]

 
_X = tf.placeholder(tf.float32, shape=[None, timesteps, data_dim], name='input')
_y = tf.placeholder(tf.float32, [None, out_dim], name='label')
dropout = tf.placeholder(tf.float32, name='dropout')
batch_size = tf.placeholder(tf.int32, name='batch_size')  # 注意类型必须为 tf.int32
 
num_units = 200
num_layers = 3

 


cells = []
for _ in range(num_layers):
  cell = tf.contrib.rnn.LSTMCell(num_units)  # Or GRUCell(num_units)
  cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=1.0 - dropout)
  cells.append(cell)
mlstm_cell = tf.contrib.rnn.MultiRNNCell(cells)

init_state = mlstm_cell.zero_state(batch_size, dtype=tf.float32)


# **步骤6：方法一，调用 dynamic_rnn() 来让我们构建好的网络运行起来
# ** 当 time_major==False 时， outputs.shape = [batch_size, timestep_size, hidden_size] 
# ** 所以，可以取 h_state = outputs[:, -1, :] 作为最后输出
# ** state.shape = [layer_num, 2, batch_size, hidden_size], 
# ** 或者，可以取 h_state = state[-1][1] 作为最后输出
# ** 最后输出维度是 [batch_size, hidden_size]
 
X_reshape = tf.reshape(_X, [-1, timesteps, data_dim])

output, state = tf.nn.dynamic_rnn(mlstm_cell, X_reshape, dtype=tf.float32, initial_state=init_state)
h_state = state[-1][1]

#h_state = output[:, -1, :]  # 或者 h_state = state[-1][1]


# 开始训练和测试
W = tf.Variable(tf.truncated_normal([num_units, out_dim], stddev=0.1), dtype=tf.float32)
bias = tf.Variable(tf.constant(0.1,shape=[out_dim]), dtype=tf.float32)
y_pre = tf.nn.softmax(tf.matmul(h_state, W) + bias,  name='predict')


# 损失和评估函数
lr = 1e-3
batch_mse = tf.reduce_mean(tf.pow(y_pre - _y, 2), 1)

cross_entropy = -tf.reduce_mean(_y * tf.log(y_pre))
train_op = tf.train.AdamOptimizer(lr).minimize(cross_entropy)
 

# TRAIN StARTS
save_model = 'model_lstm_tf_za'
saver = tf.train.Saver()

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(runEpoch):
        batch = get_next_batch(BS, index_in_epoch, contents, labels)
 
        _X_reshape = batch[0].reshape(-1, timesteps, data_dim)
        _y_reshape = batch[1]#.values.reshape(-1,1) 
        #print _X_reshape.shape
        #print _y_reshape.shape
         
        _, cost, y_prediction = sess.run([train_op, cross_entropy, y_pre], feed_dict={_X:_X_reshape, _y: _y_reshape, dropout: 0.6, batch_size: BS})
          
        if (i+1)%BS == 0:
            step = (i+1)/BS
            train_batch_mse = sess.run(batch_mse, feed_dict={_X:_X_reshape, _y: _y_reshape, dropout: 0.6, batch_size: BS})
            print "step:",step, " cost=", "{:.9f}".format(cost),  "Train auc=",  auc(batch[1], y_prediction)
         
        
    # 计算测试数据的准确率
#    _X_test_reshape = X_test.reshape(-1, timesteps, data_dim)
#    _y_test_reshape = y_test#.values#.reshape(-1,out_dim)
#    print "test accuracy %g"% sess.run(accuracy, feed_dict={_X: _X_test_reshape, _y: _y_test_reshape, dropout: 0, batch_size: _y_test_reshape.shape[0]})
    
    print("Optimization Finished!")
    save_path = saver.save(sess, save_model)
    print("Model saved in file: %s" % save_path)


_X_test_reshape = X_test.reshape(-1, timesteps, data_dim)
_y_test_reshape = y_test#.values#.reshape(-1,out_dim)

# Initializing the variables
init = tf.global_variables_initializer()

with tf.Session() as sess:
    #方法1
    #saver.restore(sess, tf.train.latest_checkpoint('.'))
    
    #方法2
    ##注意，不仅仅要给出模型名字model_lstm_tf_za，还一定要给出所在的路径，如果是当前目录下，就用./model_lstm_tf_za，否则会报错Unsuccessful TensorSliceReader constructor
    saver = tf.train.import_meta_graph("./model_lstm_tf_za.meta")
    saver.restore(sess, "./model_lstm_tf_za")
    
    y_predict = sess.run(y_pre, feed_dict={_X: _X_test_reshape, dropout: 0, batch_size: _y_test_reshape.shape[0]})
    print y_predict.shape
    print y_test.shape
 
    
#y_predict = np.array( [x[0] for x in y_predict]).reshape(-1,1)
#y_predict = np.where(np.array(y_predict)<0.5,0,1)
#y_test = np.array([x[0] for x in y_test]).reshape(-1,1)

 

y_predict = np.argmax(y_predict, axis=1).reshape(-1,1)
y_test = np.argmax(y_test, axis=1).reshape(-1,1)




confusion_matrix=confusion_matrix(y_test,y_predict)
print  confusion_matrix


precision_p = float(confusion_matrix[1][1])/float((confusion_matrix[0][1] + confusion_matrix[1][1]))
recall_p = float(confusion_matrix[1][1])/float((confusion_matrix[1][0] + confusion_matrix[1][1]))
 
print ("Precision:", precision_p) 
print ("Recall:", recall_p) 
