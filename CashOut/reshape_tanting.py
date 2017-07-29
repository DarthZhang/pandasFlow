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
df = pd.read_csv("idx_new_08.csv")
df=df.sort_values(by=['pri_acct_no_conv','tfr_dt_tm']) #��pri_acct_no_conv�е��������� 
#df.index=range(0,df.shape[0]) 

#df=df.head()
data=np.array(df.iloc[:,1:], dtype=np.int64)
#��ȡ���еĿ��� ��������
card_c=df['pri_acct_no_conv']
card_c.index=range(0,card_c.shape[0]) #�����Ŀ����޸�����
card_c_d = card_c.drop_duplicates()#ɾ���ظ����׿���

#�����ϲ� ͬһ���ŵ�����
c_index=card_c_d.index

for i, cn in enumerate(c_index):
    temp=[]
    count=np.sum(card_c==card_c_d[cn]) #����ĳ�ſ�������
    for j in range(cn,cn+count):
        temp=np.hstack((temp,data[j][0:-1])) #ͬһ���ŵ������ϲ�,��ǩ���ϲ�
        temp_s=temp
        temp_s=np.hstack((temp_s,data[j][-1]))
        temp_s=temp_s.reshape(1,len(temp_s))
        data_temp = DataFrame(temp_s)
        data_temp.to_csv('data_5_rows.csv',index=False,header=False,mode='a')