import pandas as pd
import numpy as np
from sklearn import linear_model
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
from utility import *
path = u'D:\citics\Barra\data\\'


dfs = pd.read_csv(path + 'FactorExposure.csv')
raw = pd.read_csv(path + 'dataall.csv')



####通过加权回归计算因子收益率
#####同时返回t值，VIF
def regress(test):
    X = test.iloc[:,2:-2]
    y = np.array(test.loc[:,'return'])
    w = np.array(test.loc[:,'weight'])
    wls_model = sm.WLS(y,X, weights= w)
    result = wls_model.fit()
    factor_return = result.params
    f = pd.DataFrame(dict(factor_return), index =test.datetime.unique(),columns = factor_return.index)
    resid = result.resid
    pred = pd.DataFrame({'residual':resid,'code':test.code,'weight':test.weight})
    t = result.tvalues
    vif = [variance_inflation_factor(np.array(X), i) for i in range(X.shape[1])]    
    vif = dict(zip(X.columns, vif))    
    return(f, pred,t, vif)

def cov_pair(ft, fk):
    T = len(ft) 
    half = T/2
    w = halflife(half_life = half, length = T)
    cov = sum(w*(ft - np.mean(ft)) * (fk - np.mean(fk)))
    return cov

def cov_mat(df,date,T = 90, delta = 0):
    try:
        loca = np.where(df.index.values == date)[0][0]
        mat = pd.DataFrame(index= df.columns, columns = df.columns)
        col = df.columns
        for fact1 in col:
            for fact2 in col:
                ft = np.array(df[fact1].iloc[(loca-T):loca])
                fk = np.array(df[fact2].iloc[(loca - T - delta):(loca - delta)])
                mat.loc[fact1,fact2] = cov_pair(ft, fk)
    except:
        print('Index out-of-bounds' )
    return mat



####因子风险和现实风险比较
def forecast_risk(df, T= 90):
    risk = pd.DataFrame(index = df.index, columns = df.columns)
    for i in np.arange(T,len(df)):
        for each in df.columns:
           risk[each].iloc[i] = cov_pair(df[each].iloc[(i-T):i], df[each].iloc[(i-T):i])
    return risk

def realized_risk(df, T = 126):
    risk = pd.DataFrame(index = df.index, columns = df.columns)
    for each in df.columns:
        risk[each] = df[each].rolling(window = T).var()
    return risk


############以下是specific risk的计算
#####计算St
def avg_risk(df):
    tradeday = df.datetime.unique()
    S =[]
    for each in tradeday:
        temp = df[df.datetime == each]
        abs_return = abs(temp['residual'])
        avg_return = sum(abs_return * temp.weight)
        S.append(avg_return)
    St = pd.Series(S, index = tradeday)
    return St

####计算Shat
def avg_risk_predict(S, T = 30, a = 6): ##T是 回归的回溯时长；a value of weight
    E = a*S.shift(1) + a * (1-a) *S.shift(2) + a*(1-a)**2 * S.shift(3)
    S_hat = pd.Series(index = S.index)
    for i in np.arange(3+T, len(E)):
        y = S[(i-T):i]
        x = E[(i-T):i]
        ols_model = sm.OLS(y, x)
        result = ols_model.fit()
        S_hat[i:(i+1)] =result.predict(S[i:(i+1)])
    return(S_hat)

def adjustment_data(predict_data,factor, raw, a = 0.6): 
    code = predict_data.code.unique()
    dfs = pd.DataFrame()
    for each in code:
        df = predict_data[predict_data.code == each].copy()
        raw_data = raw[raw.code == each].copy()
        r = abs(raw_data.pct_chg)
        raw_data['EWA'] =  a*r.shift(1) + a * (1-a) *r.shift(2) + a*(1-a)**2 * r.shift(3)
        raw_data['return_lag'] = raw_data.pct_chg.shift(1)
        df = pd.merge(df, raw_data[['datetime','code','pct_chg','risk_residvol252','EWA','return_lag']], on = ['datetime','code'], how = 'inner')
        dfs = dfs.append(df)
    predict_data = pd.merge(dfs, factor.iloc[:,:-2], on = ['datetime','code'],how = 'inner' )
    S_avg = avg_risk(predict_data)
    S_avg = pd.DataFrame(S_avg)
    S_avg.columns = ['S']
    predict_data = pd.merge(predict_data, S_avg, left_on = 'datetime', right_index = True)
    predict_data['V'] = (abs(predict_data.residual) - predict_data.S)/ predict_data.S
    predict_data.drop(['S','residual','pct_chg'], axis = 1, inplace =True)
    predict_data.rename(columns = {'risk_residvol252': 'sigma'}, inplace = True)
    predict_data = predict_data.sort_values(by = ['datetime','code'], axis =0, ascending = True)
    return predict_data
  
####计算Vhat 目前还确少峰度修正k
def adjustment(predict_data):
    predict_data.dropna(inplace = True)
    tradeday = predict_data.datetime.unique()
    V_hat = pd.DataFrame()
    for i in np.arange((len(tradeday)-1)):
        df = predict_data[predict_data.datetime == tradeday[i]].copy()
        dfnext = predict_data[predict_data.datetime == tradeday[i+1]].copy()
        V = df['V']
        Z = df.iloc[:,2:-3].copy()
        Znext = dfnext.iloc[:,2:-3].copy()
        ols_model = sm.OLS(V, Z)
        result = ols_model.fit()
        V_pred = result.predict(Znext)
        V_pred = pd.DataFrame({'datetime':tradeday[i+1], 'code':dfnext.code,'Vhat':V_pred}, columns =['datetime','code','Vhat'])
        V_hat = V_hat.append(V_pred)
        print(tradeday[i])
    V_hat.loc[V_hat.Vhat <-1,'Vhat'] = -1
    return V_hat


a = adjustment_data(predict_data, dfs, raw)
V = adjustment(a)
Shat = avg_risk_predict(avg_risk(predict_data))
Shat = pd.DataFrame(Shat,columns = ['Shat'])
specific_risk = pd.merge(V,Shat, left_on = 'datetime', right_index = True)
specific_risk.dropna(inplace = True)
specific_risk['sigma'] = specific_risk.Shat*(1 + specific_risk.Vhat)
specific_risk.index = np.arange(len(specific_risk))
#specific_risk['datetime'].value_counts()
specific_risk.to_csv(path + 'specific_risk.csv')
return_matrix.to_csv(path + 'FactorReturn.csv')
Frisk = forecast_risk(return_matrix)
Rrisk = realized_risk(return_matrix)   





