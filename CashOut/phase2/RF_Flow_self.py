# -*- coding: utf-8 -*-
import pandas as pd 
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier 
from sklearn.utils import shuffle  
from sklearn.cross_validation import train_test_split

 
label='label' # label的值就是二元分类的输出
cardcol= 'pri_acct_no_conv'
time = "tfr_dt_tm"



df = pd.read_csv("FE_db_1012.csv", low_memory=False)
 

label='label' # 
cardcol= 'pri_acct_no_conv'

Fraud = df[df.label == 1.0]
Normal = df[df.label == 0.0]
#print "Ori Fraud shape:", Fraud.shape, "Ori Normal shape:", Normal .shape

card_c_F = Fraud['pri_acct_no_conv'].drop_duplicates()#涉欺诈交易卡号

#未出现在欺诈样本中的正样本数据
fine_N=Normal[(~Normal['pri_acct_no_conv'].isin(card_c_F))]
print "True Fraud shape:", Fraud.shape, "True Normal shape:", fine_N.shape
 

train_Fraud,test_Fraud = train_test_split(Fraud, test_size=0.1)
print "train_Fraud shape:", train_Fraud.shape, "test_Fraud shape:", test_Fraud.shape

train_Normal,test_Normal = train_test_split(fine_N, test_size=0.9)
print "train_Normal shape:", train_Normal.shape, "ttest_Normal shape:", test_Normal.shape

#train_all = pd.concat([train_Fraud, train_Normal.sample(frac=0.1, replace=False)], axis = 0)
#test_all = pd.concat([test_Fraud.sample(frac=0.1, replace=False), test_Normal], axis = 0)
#x_columns = [x for x in train_Fraud.columns if x not in [label,cardcol,time, "term_id", "mchnt_cd"]]
# 
#  
#y_train = train_all.label
#y_test = test_all.label
#
#X_train = train_all[x_columns] 
#X_test =  test_all[x_columns] 
# 
#
##n_estimators树的数量一般大一点。 max_features 对于分类的话一般特征束的sqrt，auto自动
#clf = RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=10, max_features="auto",max_leaf_nodes=None, bootstrap=True)
#
#clf = clf.fit(X_train, y_train)
#  
#print clf.score(X_test, y_test)
#
#pred = clf.predict(X_test) 
#
#confusion_matrix=confusion_matrix(y_test,pred)
#print  confusion_matrix
#
#
#precision_p = float(confusion_matrix[1][1])/float((confusion_matrix[0][1] + confusion_matrix[1][1]))
#recall_p = float(confusion_matrix[1][1])/float((confusion_matrix[1][0] + confusion_matrix[1][1]))
# 
#print ("Precision:", precision_p) 
#print ("Recall:", recall_p) 
#
#F1_Score = 2*precision_p*recall_p/(precision_p+recall_p)
#
#print F1_Score
# 
