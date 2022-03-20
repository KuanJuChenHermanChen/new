#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tejapi
tejapi.ApiConfig.api_key = "5ESe2LtQJzuDCvVSudNdXi792Pi9xl"


# In[33]:


df = tejapi.get('TRAIL/TAPRCD',
                  coid="3035",
                  opts={'columns': ['coid', 'mdate', 'volume', 'open_d','high_d','low_d','close_d','tej_psr']},
                  paginate=True,
                  chinese_column_name=True,
                 )
df = df.set_index("年月日")

df


# In[34]:


plt.figure(facecolor='white',figsize=(24,8))
plt.plot(df['收盤價(元)'], label='收盤價(元)')
plt.title("(3035)",fontsize=25)
plt.xticks(rotation=45)
plt.xlabel('Data',fontsize=25)
plt.ylabel('Price',fontsize=25)
plt.grid()
plt.show()


# In[35]:


def voltrade(ma,p,q,s): 
    
    ma = ma.copy()
    
    ma["當日交易量"] = ma["成交量(千股)"].rolling(p).mean()
    
    ma["前五日總量"] = ma["成交量(千股)"].rolling(q).sum()
    
    ma["前第六到第十日總量"] = (ma["成交量(千股)"].rolling(s).sum() - ma["成交量(千股)"].rolling(q).sum())
           
    return ma

#設定參數
stock = voltrade(df, 1, 5, 10)

stock


# In[36]:


#設定篩選條件
def buysell(company,a,b):
    company = company.copy()
    buy=[]
    sell=[]
    hold=0
    for i in range(len(company)):
        
        #買點設定：前五日交易總量 >= 前第六到第十日交易總量的三倍
        if company["前五日總量"][i] >= company["前第六到第十日總量"][i]*a :
            sell.append(np.nan)
            if hold !=1:
                buy.append(company["收盤價(元)"][i])
                
                hold = 1
            else: 
                buy.append(np.nan)

        #賣點設定：前五日交易總量 >= 前第六到第十日交易總量的五倍
        elif company["前五日總量"][i] >= company["前第六到第十日總量"][i]*b :
            buy.append(np.nan)
            if hold !=0:
                sell.append(company["收盤價(元)"][i])
                hold = 0
            else:
                sell.append(np.nan)
        else:
            buy.append(np.nan)
            sell.append(np.nan)
            
    a=(buy,sell)
        
    company['Buy_Signal_Price']=a[0]
    company['Sell_Signal_Price']=a[1]
    company["買賣股數1"]=company['Buy_Signal_Price'].apply(lambda x : 1000 if x >0 else 0)
    company["買賣股數2"]=company['Sell_Signal_Price'].apply(lambda x : -1000 if x >0 else 0  )
    company["買賣股數"]=company["買賣股數1"]+ company["買賣股數2"]
    
    return company


# In[37]:


def plot(data):
    
    #視覺化
    plt.figure(figsize=(24,8))
    
    #設定買點為紅色正三角形符號
    plt.scatter(data.index,data['Buy_Signal_Price'],color='red', label='Buy',marker='^',alpha=1)
    
    #設定賣點為綠色倒三角符號
    plt.scatter(data.index,data['Sell_Signal_Price'],color='green', label='Sell',marker='v',alpha=1)
    
    
    plt.plot(data['收盤價(元)'], label='Close Price', alpha=0.35)
    plt.title('Close Price Buy & Sell Signals')
    
    #字斜45度角
    plt.xticks(rotation=45)
    plt.xlabel('Date')  
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    return  plt.show()


# In[38]:


vol = buysell(stock,3,5)

plot(vol)


# In[39]:


#與成交量做對比
def pvtwo(data):
  fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 8))
  ax1, ax2 = axes.flatten()
  ax1.scatter(data.index,data['Buy_Signal_Price'],color='red', label='Buy',marker='^',alpha=1)

  ax1.scatter(data.index,data['Sell_Signal_Price'],color='green', label='Sell',marker='v',alpha=1)
  ax1.plot(data['收盤價(元)'], label='Close Price', alpha=0.35)
  ax1.set_title('Close Price Buy & Sell Signals')
  ax1.set_ylabel('Price')
  ax1.grid(linestyle="--",alpha=0.8)

  red_pred = np.where(data["收盤價(元)"] >= data["開盤價(元)"],data["成交量(千股)"], 0)
  blue_pred = np.where(data["收盤價(元)"] <  data["開盤價(元)"], data["成交量(千股)"], 0)
  ax2.bar(data.index,red_pred, facecolor="red")
  ax2.bar(data.index,blue_pred,facecolor="green")
  plt.legend(loc='best')
  return plt.show()

pvtwo(vol)


# In[40]:


#買點價位
for i in vol['Buy_Signal_Price']:
    
    if i > 0:
        
        print(i)


# In[41]:


#賣點價位
for i in vol['Sell_Signal_Price']:
    
    if i > 0:
        
        print(i)

