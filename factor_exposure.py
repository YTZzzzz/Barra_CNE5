import pandas as pd
import numpy as np
from utility import *
from WindPy import *
from style_factor import StyleFactor


path = r'D:\citics\Barra\data\\' 
data = pd.read_csv(path + 'dataall.csv')

####pre NA processing 优先股缺失并非来源于数据缺失，所以用0填补。
data.wgsd_pfd_stk.fillna(0, inplace = True)

###返回style factor exposure
style_factors = factors(data)
style_factors.to_csv(path + 'StyleFactors.csv', index = False)

####删除任意因子暴露存在NA的行，删除当日停牌的股票
style_factors.dropna(inplace = True, axis = 0)
style_factors.drop(style_factors[style_factors.volume == 0].index.tolist(), inplace = True)
style_factors.drop(['volume'],axis = 1,inplace = True)
style_factors.index = np.arange(len(style_factors))

###用以下两种方法都可以获取industry factor exposure
"""
w.start()
beginDate = '2012-12-25'
endDate = '2018-07-01'
stockSector = w.wset("sectorconstituent","date="+endDate+";sector=全部A股")
dates,codes,names = stockSector.Data
joincodes = ','.join(codes)
ind = w.wss(joincodes,'industry_gicscode','industryType=1')
industrycode= ind.Data[0]
inddata = pd.DataFrame({'industry_gicscode':industrycode}, index = ind.Codes)
"""

IND = pd.read_csv(path + 'industry.csv')
IND = IND[~IND.iloc[:,3].isnull()]
industrycode = [str(int(x)) for x in IND.iloc[:,3]]
inddata = pd.DataFrame({'industry_gicscode':industrycode}, index = IND.iloc[:,0])
industry_data = industry(inddata)


####对style factors truncate， winsorize， normalize后将数据合并。
trade_data = data.loc[:,['datetime', 'code']]
trade_data['return'] = data.loc[:,'pct_chg']
trade_data['weight'] = data.loc[:,'mkt_cap_ard'] 
datetime = sorted(style_factors.datetime.unique())
dfs = pd.DataFrame()
for each in datetime:
    time = style_factors[style_factors.datetime == each]
    pre_data = preparing(time)
    style_data = styles(pre_data)
    factor_data = pd.merge(style_data, industry_data.iloc[:,1:], left_on = 'code', right_index = True,how = 'left')
    df = pd.merge(factor_data, trade_data, left_on = ['datetime','code'],right_on =['datetime','code'], how = 'inner')
    df.dropna(inplace = True)
    df.weight = df.loc[:,'weight'] / sum(df.loc[:,'weight'])
    dfs =  dfs.append(df)
    print(each)

dfs.index = np.arange(len(dfs))
dfs.to_csv(path+'FactorExposure.csv', index = False) 

