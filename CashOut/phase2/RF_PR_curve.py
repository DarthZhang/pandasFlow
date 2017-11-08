# -*- coding: utf-8 -*-
import pandas as pd 
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier 
from sklearn.utils import shuffle  
from sklearn.cross_validation import train_test_split
from sklearn.metrics import precision_recall_curve, roc_curve, auc  
import numpy as np

 
label='label' # label的值就是二元分类的输出
cardcol= 'pri_acct_no_conv'
time = "tfr_dt_tm"
 
reader = pd.read_csv("FE_trainNormal.csv", low_memory=False, iterator=True)
     
loop = True
chunkSize = 100000 
chunks = []
i = 0
while loop:
    try:
        chunk = reader.get_chunk(chunkSize)
        chunks.append(chunk)
        if (i%5)==0:
            print i
        i = i+1
   
    except StopIteration:
        loop = False
        print "Iteration is stopped."
df_normal_train = pd.concat(chunks, ignore_index=True)

df_normal_train = df_normal_train.sample(n=800000) 


df_fraud_all = pd.read_csv("FE_Fraud.csv", low_memory=False)
df_fraud_all = df_fraud_all.sample(n=8000) 
#df = pd.read_csv("idx_weika_07.csv") 

df = pd.concat([df_normal_train,df_fraud_all], axis = 0)


label='label' # 
cardcol= 'pri_acct_no_conv'

Fraud = df[df.label == 1.0]
Normal = df[df.label == 0.0]
print "Ori Fraud shape:", Fraud.shape, "Ori Normal shape:", Normal .shape

card_c_F = Fraud['pri_acct_no_conv'].drop_duplicates()#涉欺诈交易卡号

#未出现在欺诈样本中的正样本数据
fine_N=Normal[(~Normal['pri_acct_no_conv'].isin(card_c_F))]
print "True Fraud shape:", Fraud.shape, "True Normal shape:", fine_N.shape

df_All=pd.concat([Fraud,fine_N], axis = 0)


################################################################################


df_All=shuffle(df_All)

 
x_columns = [x for x in df_All.columns if x not in [label,cardcol,time, "term_id", "mchnt_cd"]]
 
#x_columns = x_columns[-67:-1] 
 
train_all,test_all=train_test_split(df_All, test_size=0.2)
 

y_train = train_all.label
y_test = test_all.label

X_train = train_all[x_columns] 
X_test =  test_all[x_columns] 
 

#n_estimators树的数量一般大一点。 max_features 对于分类的话一般特征束的sqrt，auto自动
clf = RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=10, max_features="auto",max_leaf_nodes=None, bootstrap=True)

clf = clf.fit(X_train, y_train)
  
print clf.score(X_test, y_test)

pred = clf.predict(X_test) 

confusion_matrix=confusion_matrix(y_test,pred)
print  confusion_matrix


precision_p = float(confusion_matrix[1][1])/float((confusion_matrix[0][1] + confusion_matrix[1][1]))
recall_p = float(confusion_matrix[1][1])/float((confusion_matrix[1][0] + confusion_matrix[1][1]))
 
print ("Precision:", precision_p) 
print ("Recall:", recall_p) 

F1_Score = 2*precision_p*recall_p/(precision_p+recall_p)

print F1_Score
 




pred_pair = clf.predict_proba(X_test)  
pred_proba = [x[1] for x in pred_pair]
 

precision, recall, thresholds = precision_recall_curve(y_test,pred_proba)  
 
import matplotlib.pyplot as plt
 

plt.step(recall, precision, color='b', alpha=0.2,
         where='post')
plt.fill_between(recall, precision, step='post', alpha=0.2,
                 color='b')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.savefig("examples.jpg")

np.savetxt("precision.txt",precision)
np.savetxt("recall.txt",recall)