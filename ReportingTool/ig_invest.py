import pandas as pd
from os import path
from matplotlib import pyplot as plt
sBasePath = 'C:\\Users\\franc\\Documents\\ig_invest'
sFileName_Value = 'IWM Historical Data.csv'
sFileName_Growth = 'IWO Historical Data.csv'
sFileName_Value = path.join(sBasePath,sFileName_Value)
sFileName_Growth = path.join(sBasePath,sFileName_Growth)

df_Value = pd.read_csv((sFileName_Value),sep=",")
df_Growth = pd.read_csv((sFileName_Growth),sep = ",")
df_Value = df_Value[['Date','Price']]
df_Value.columns = ['Date','Price']
df_Growth = df_Growth.dropna()
df_Value = df_Value.dropna()


df_Growth['Date'] = pd.to_datetime(df_Growth['Date'] , format='%b %d, %Y')
df_Growth = df_Growth[['Date','Price']]
df_Growth = df_Growth.set_index(df_Growth['Date'])
df_Value = df_Value[['Date','Price']]
df_Value['Date'] = pd.to_datetime(df_Value['Date'] , format='%b %d, %Y')
df_Value = df_Value.set_index(df_Value['Date'])
newindex = df_Value.index.union(df_Growth.index)
df_Value = df_Value.reindex(newindex,method = 'pad')
df_Growth = df_Growth.reindex(newindex,method = 'pad')
df_Value = df_Value[(df_Value.index > '2015-07-07')]
df_Growth = df_Growth[(df_Growth.index > '2015-07-07')]
df_Value=  1.2*df_Value['Price']
df_Growth=  df_Growth['Price']

df_Value = df_Value-df_Value.iloc[-1]
df_Growth = df_Growth-df_Growth.iloc[-1]

plt.plot(df_Value)
plt.plot(df_Growth)
df_Value= df_Value.diff()
df_Growth = df_Growth.diff()
df_Growth = df_Growth.dropna()
df_Value = df_Value.dropna()
cfd_res = df_Growth - df_Value
std_values = df_Value.std()
std_growth =df_Growth.std()
'''
df_Tre = 1.5*df_Tre[['Price']]
df_Tre = df_Tre-df_Tre.iloc[0]
df_HYG = df_HYG[['Price']]
df_HYG = df_HYG-df_HYG.iloc[0]
'''



#plt.plot(df_HYG)
plt.show()
pass

