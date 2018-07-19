from WindPy import *
import datetime
import pandas as pd
import numpy as np

market_cols1 = ['mkt_cap_ard','risk_beta120','pb','pe_est_ftm','ocfps_ttm', #财务数据
                'pe_ttm','west_netprofit_CAGR','west_netprofit_YOY',
                'risk_exstdev252','risk_residvol252','share_totala',
                'wgsd_pfd_stk','wgsd_debt_lt','wgsd_liabs',
                'wgsd_assets','wgsd_com_eq_par']
market_cols2 = ['pct_chg', 'volume','close'] #交易数据
beginDate = '2012-12-25'
endDate = '2018-07-01'
path = r'D:\citics\Barra\data' # 结果储存路径

#today = datetime.date.today().strftime('%Y-%m-%d')
#endDate = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
w.start()
def GetMarketInfo(code,cols1,cols2):
    global beginDate
    ipoDate = w.wss(code,'ipo_date').Data[0][0].strftime('%Y-%m-%d')
    if ipoDate > beginDate:
        begin = ipoDate
    else:
        begin = beginDate
    dailyQuota1 = w.wsd(code,','.join(cols1),begin,endDate,"industryType=1;ruleType=9;currencyType=;rptType=1;Fill=Previous")
    df1 = pd.DataFrame(dict(zip(cols1,dailyQuota1.Data)),index=dailyQuota1.Times)
    dailyQuota2 = w.wsd(code,','.join(cols2),begin,endDate,"")
    df2 = pd.DataFrame(dict(zip(cols2,dailyQuota2.Data)),index=dailyQuota2.Times)
    df = pd.merge(df1,df2, left_index = True, right_index = True)
    [riskfree] = w.wsd("TB1Y.WI", "close", begin, endDate, "Fill=Previous").Data
    rf =(np.array(riskfree)/100 + 1)**(1/252)-1
    df['rf'] = rf
    return df
def Align(code,df):
    df.reset_index(inplace=True)
    df.rename(columns={'index':'datetime'},inplace=True)
    df['code'] = code;
    df.set_index(['datetime','code'],inplace=True)
    try:
        df['pct_chg'] /= 100
    except:
        print('无pct_chg字段')
    return df
def Concat(codes,cols1,cols2):
    dfs = pd.DataFrame()  
    for code in codes:
        print('开始下载%s数据'%code)
        try:
            df_temp = GetMarketInfo(code,cols1,cols2)
            df_temp = Align(code,df_temp)
            dfs = dfs.append(df_temp)
            dfs.to_pickle(path+r'\test.pkl')
        except:
            print('quota exceeded.')
            break 
    return dfs
# 通过wset取截止日全部A股代码，ESTU
stockSector = w.wset("sectorconstituent","date="+endDate+";sector=全部A股")
dates,codes,names = stockSector.Data
#股票数据
#code = codes[:500]
#code = ['000001.SZ','000002.SZ']
dfs = Concat(codes,market_cols1,market_cols2)
dfs.to_csv(path + r'\stock.csv')
w.stop()
