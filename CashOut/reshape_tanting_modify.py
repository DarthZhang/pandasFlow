# -*- coding: utf-8 -*-


#==============================================================================
# ��ͬ���׿������ݰ�����ʱ����ǰ�����ϲ����õ�ʱ���������������
#���룺
#    ���׿���ɢ�����ݣ���ʽ������ ���� ��ǩ
#���������ʱ�� 
#    ����1 ����2...����n ���һ�ʽ��ױ�ǩ...
#==============================================================================
import pandas as pd
from pandas import DataFrame
import numpy as np
df = pd.read_csv("idx_new_08_sort_test.csv")
df=df.sort_values(by=['pri_acct_no_conv','tfr_dt_tm']) #��pri_acct_no_conv�е��������� 
#df.index=range(0,df.shape[0]) 

#df=df.head()
data=np.array(df.iloc[:,1:], dtype=np.int64)
#��ȡ���еĿ��� ��������


df['pri_acct_no_conv'].index=range(0,card_c.shape[0]) #�����Ŀ����޸�����
card_c_d = df['pri_acct_no_conv'].drop_duplicates()#ɾ���ظ����׿���

print card_c_d

#�����ϲ� ÿ�ſ��ŵĵ�һ������
c_index=card_c_d.index
c_index_list = list(c_index)


for cn in c_index_list:
    temp=[]
    count=np.sum(df['pri_acct_no_conv']==card_c_d[cn]) #����ĳ�ſ�������  card_c_d[cn]��ĳ������
    for j in range(cn,cn+count):
        temp=np.hstack((temp,data[j][0:-1])) #ͬһ���ŵ������ϲ�,��ǩ���ϲ�
        temp_s=temp
        temp_s=np.hstack((temp_s,data[j][-1]))  #��������ı�ǩ
        temp_s=temp_s.reshape(1,len(temp_s))
        data_temp = DataFrame(temp_s)
        data_temp.to_csv('data_5_rows.csv',index=False,header=False,mode='a')
        
        
        
#a = np.array((1,2,3))  
#b = np.array((2,3,4))  
#c = np.hstack((a,b))
#print c
# 
#print DataFrame(c) 

