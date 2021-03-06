# -*-coding:utf-8-*-


import numpy as np
from numpy import arange
from matplotlib import pyplot
from pandas import read_csv
from pandas import  set_option
#from pandas.plotting import scatter_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.metrics import recall_score, precision_score

# 导入随机森林算法库
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import confusion_matrix
from sklearn.utils import shuffle
from sklearn.ensemble import GradientBoostingClassifier
import datetime
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn.metrics import precision_recall_fscore_support
from dateutil import parser
from sklearn.metrics import confusion_matrix
import seaborn as sns
sns.set_style('whitegrid')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import time

fraudname = r'fraud.csv'
normalname = r'normal.csv'

df_fraud = read_csv(fraudname,  sep=',', dtype=str)

df_normal = read_csv(normalname,  sep=',',  dtype=str)


df_fraud["label"] = 1
df_normal["label"] = 0

df_All = pd.concat([df_fraud,df_normal], axis = 0)
df_All = df_All.fillna(-1)

df_All = shuffle(df_All)

#"resp_cd","app_ins_inf" 这两个列 有 全数字的字符串，有带字母的字符串。格式很乱。所以推荐read_csv(fraudname,  sep=',', dtype=str)  直接指定全部为str。 后面对连续变量单独指定 df_All["trans_at"] = df_All["trans_at"].astype(np.double)
sus_cols = ["trans_at", "settle_at"]
df_All["trans_at"] = df_All["trans_at"].astype(np.double)
df_All["settle_at"] = df_All["settle_at"].astype(np.double)

dis_cols = ["resp_cd","app_ins_inf","acq_ins_id_cd","mchnt_tp","card_attr","acct_class","app_ins_id_cd","fwd_ins_id_cd","trans_curr_cd","trans_tp","proc_st","ins_pay_mode","up_discount","app_discount","ctrl_rule1","mer_version","app_version","order_type","app_ntf_st","acq_ntf_st","proc_sys","mchnt_back_url","app_back_url","mer_cert_id","mchnt_nm","acq_ins_inf","country_cd","area_cd"]
df_dummies = pd.get_dummies(df_All[dis_cols])

########################################################################
def cnt_89(x):
    return  str(x).count("8") + str(x).count("9")

def cnt_89_ratio(x):
    return  float(str(x).count("8") + str(x).count("9"))/float(len(str(x))-2)

def getWeekday(x):
    result = -1
    try:
        result = parser.parse(x).weekday()
    except ValueError:
        result = -1
    return result

df_All["weekday"] = df_All["trans_tm"].map(lambda x: getWeekday(x))

df_All["hour"] = df_All["trans_tm"].map(lambda x: x[8:10] )

df_All["is_night"] = df_All["hour"].map(lambda x: 1 if (int(x)>=0 and int(x)<=6) else 0 )

df_All["cnt_89"] = df_All["trans_at"].map(lambda x: cnt_89(x))
df_All["cnt_89_ratio"] = df_All["trans_at"].map(lambda x: cnt_89_ratio(x))
gened_cols = ["weekday", "hour", "is_night", "cnt_89", "cnt_89_ratio"]
##################################################################

############################特征交叉##############################
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import PolynomialFeatures
#先把所有类别型变量变成数值性，然后调用PolynomialFeatures  计算变量相乘的扩展 获得 交叉特征   但其实相乘的数值有时候并不一定有意义，不过可以尝试。所以正确的做法是，先用原语义做简单字符串拼接，然后再做onehot编码。
#interaction_only=True 例如[a,b]的多项式交互式输出[1,a,b,ab]。不存在自己与自己交互的情况如;a^2或者a*b^2之类的。
poly = PolynomialFeatures(degree=2, interaction_only=True)

le = LabelEncoder()
df_le= np.array(le.fit_transform(df_All[dis_cols[0]]))

for i in dis_cols[1:]:
    le_i = LabelEncoder()
    df_le_tmp=  np.array(le_i.fit_transform(df_All[i]))
    df_le  = np.vstack((df_le,df_le_tmp))

df_le = df_le.T
print df_le.shape
df_poly = pd.DataFrame(poly.fit_transform(df_le))

# ###################################################################


df_X = pd.concat([df_All[sus_cols],df_dummies,df_All[gened_cols]], axis=1)
df_X = pd.concat([df_X.reset_index(),df_poly], axis=1)

print df_X.shape

used_cols = df_X.columns


sc =StandardScaler()
df_X =sc.fit_transform(df_X)#对数据进行标准化

df_y = df_All["label"]


X_train, X_test, y_train, y_test = train_test_split(df_X, df_y, test_size=0.2)

#n_estimators树的数量一般大一点。 max_features 对于分类的话一般特征束的sqrt，auto自动
clf = RandomForestClassifier(n_estimators=100, max_depth=None, min_samples_split=2, max_features="auto",max_leaf_nodes=None, bootstrap=True)

clf = clf.fit(X_train, y_train)


FE_ip_tuples = zip(used_cols, clf.feature_importances_)
pd.DataFrame(FE_ip_tuples).to_csv("FE_ip.csv", index=True)



pred = clf.predict(X_test)

cm1=confusion_matrix(y_test, pred)
print  cm1

result = precision_recall_fscore_support(y_test,pred)
#print result
precision_0 = result[0][0]
recall_0 = result[1][0]
f1_0 = result[2][0]
precision_1 = result[0][1]
recall_1 = result[1][1]
f1_1 = result[2][1]
print "precision_1: ", precision_1,"  recall_1: ", recall_1, "  f1_1: ", f1_1

print classification_report(y_test, pred)

