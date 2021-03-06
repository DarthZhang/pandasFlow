# -*- coding: utf-8 -*-
"""
Created on Fri Jul 07 08:30:44 2017

@author: lixurui
"""

from keras.layers import Input, Dense, Activation
from keras.models import Model
import numpy as np
from keras import regularizers

import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.metrics import recall_score, precision_score
 
#导入随机森林算法库
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn.grid_search import GridSearchCV
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import confusion_matrix
from sklearn.utils import shuffle 
from sklearn.preprocessing import StandardScaler   
 
from keras.models import Sequential

df_All = pd.read_csv("idx_new_08_del.csv", sep=',') 
df_All = shuffle(df_All) 
print df_All.shape[1]
 
#df_All.columns = ["pri_acct_no_conv","tfr_dt_tm","day_week","hour","trans_at","total_disc_at","settle_tp","settle_cycle","block_id","trans_fwd_st","trans_rcv_st","sms_dms_conv_in","cross_dist_in","tfr_in_in","trans_md","source_region_cd","dest_region_cd","cups_card_in","cups_sig_card_in","card_class","card_attr","acq_ins_tp","fwd_ins_tp","rcv_ins_tp","iss_ins_tp","acpt_ins_tp","resp_cd1","resp_cd2","resp_cd3","resp_cd4","cu_trans_st","sti_takeout_in","trans_id","trans_tp","trans_chnl","card_media","trans_id_conv","trans_curr_cd","conn_md","msg_tp","msg_tp_conv","trans_proc_cd","trans_proc_cd_conv","mchnt_tp","pos_entry_md_cd","pos_cond_cd","pos_cond_cd_conv","term_tp","rsn_cd","addn_pos_inf","iss_ds_settle_in","acq_ds_settle_in","upd_in","pri_cycle_no","disc_in","fwd_settle_conv_rt","rcv_settle_conv_rt","fwd_settle_curr_cd","rcv_settle_curr_cd","acq_ins_id_cd_BK","acq_ins_id_cd_RG","fwd_ins_id_cd_BK","fwd_ins_id_cd_RG","rcv_ins_id_cd_BK","rcv_ins_id_cd_RG","iss_ins_id_cd_BK","iss_ins_id_cd_RG","acpt_ins_id_cd_BK","acpt_ins_id_cd_RG","settle_fwd_ins_id_cd_BK","settle_fwd_ins_id_cd_RG","settle_rcv_ins_id_cd_BK","settle_rcv_ins_id_cd_RG","label"]#df_All = df_All.loc[:3000]
 
df_dummies =  df_All[["settle_tp","settle_cycle","block_id","trans_fwd_st","sms_dms_conv_in","cross_dist_in","tfr_in_in","trans_md","source_region_cd","dest_region_cd","cups_card_in","cups_sig_card_in","card_class","card_attr","acq_ins_tp","fwd_ins_tp","rcv_ins_tp","iss_ins_tp","acpt_ins_tp","resp_cd1","resp_cd3","cu_trans_st","sti_takeout_in","trans_id","trans_tp","trans_chnl","card_media","trans_curr_cd","conn_md","msg_tp","msg_tp_conv","trans_proc_cd","trans_proc_cd_conv","mchnt_tp","pos_entry_md_cd","pos_cond_cd","pos_cond_cd_conv","term_tp","rsn_cd","addn_pos_inf","iss_ds_settle_in","acq_ds_settle_in","upd_in","pri_cycle_no","disc_in","fwd_settle_conv_rt","fwd_settle_curr_cd","rcv_settle_curr_cd","acq_ins_id_cd_BK","acq_ins_id_cd_RG","fwd_ins_id_cd_BK","fwd_ins_id_cd_RG","rcv_ins_id_cd_BK","rcv_ins_id_cd_RG","iss_ins_id_cd_BK","iss_ins_id_cd_RG","acpt_ins_id_cd_BK","acpt_ins_id_cd_RG","settle_fwd_ins_id_cd_BK","settle_fwd_ins_id_cd_RG","settle_rcv_ins_id_cd_BK","settle_rcv_ins_id_cd_RG"]]

#print df_dummies.loc[:30]

#df_All = pd.concat([df_All[["pri_acct_no_conv_filled","day_week_filled","hour_filled","tfr_dt_tm_filled","trans_at_filled","total_disc_at_filled"]],df_dummies, df_All["label_filled"]], axis=1)



df_X = pd.concat([df_All[["tfr_dt_tm","day_week","hour","trans_at","total_disc_at"]],df_dummies], axis=1)#.as_matrix()
#df_X = df_All[["hour","trans_at","total_disc_at"]]
print df_X.shape

df_y = df_All["label"]#.as_matrix()

X_train, X_test, y_train, y_test = train_test_split(df_X, df_y, test_size=0.2)
 

sc = StandardScaler()

#print X_train.loc[:1]

X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)


Size1 = 512
Size2 = 256
Size3 = 128

inputSize =67
Epochs = 10

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

from keras import metrics
#Autoencoder.compile(optimizer='rmsprop', loss='mse', metrics=[metrics.mae,"accuracy"])
Autoencoder.compile(optimizer='rmsprop', loss='mse')
#Autoencoder.compile(optimizer='adam', loss='mse')
#进行训练：
Autoencoder.fit(X_train, X_train, nb_epoch=Epochs, shuffle=True, validation_data=(X_test, X_test))
 
  


#n_estimators树的数量一般大一点。 max_features 对于分类的话一般特征束的sqrt，auto自动
clf = RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=2, max_features="auto",max_leaf_nodes=None, bootstrap=True)

clf = clf.fit(X_train, y_train)
  
print clf.score(X_test, y_test)

pred = clf.predict(X_test) 

confusion_matrix=confusion_matrix(y_test,pred)
print  confusion_matrix


precision_p = float(confusion_matrix[1][1])/float((confusion_matrix[0][1] + confusion_matrix[1][1]))
recall_p = float(confusion_matrix[1][1])/float((confusion_matrix[1][0] + confusion_matrix[1][1]))
 
print ("Precision:", precision_p) 
print ("Recall:", recall_p) 

