import pandas as pd
import numpy as np
import scipy.optimize as sc_opt



def halflife(half_life = 63, length = 252):
    t = np.arange(length)
    w = 2 **(t/half_life) / sum(2 ** (t/half_life))
    return(w)
  

def winsorize(a, limit = 3):
    mean = np.mean(a)
    std = np.std(a)
    a_new = a.copy()
    a_new[a < mean - std * limit] = mean - std*limit
    a_new[a > mean + std * limit] = mean + std*limit
    return a

def normalize(a):
    mean = np.mean(a)
    std = np.std(a)
    a_new = (a - mean)/std
    return a_new

def orthogonalize(target_variable, reference_variable, regression_weight):
    orthogonalized_target_variable = target_variable - (target_variable * reference_variable).sum()/(reference_variable**2).sum() * reference_variable
    return orthogonalized_target_variable


def non_linear_size(size_exposure, market_cap_on_current_day):

    cubed_size = np.power(size_exposure, 3)
    
    cubed = normalize(winsorize(cubed_size))
    
    size = normalize(winsorize(size_exposure))
    
#    orthogonalized_size = orthogonalize(target_variable = cubed_size, reference_variable = size_exposure,
#                                              regression_weight = np.sqrt(market_cap_on_current_day)/(np.sqrt(market_cap_on_current_day).sum()))

    orthogonalized_size = orthogonalize(target_variable = cubed, reference_variable = size,
                                              regression_weight = np.sqrt(market_cap_on_current_day)/(np.sqrt(market_cap_on_current_day).sum()))

    return orthogonalized_size


def truncate(data, column, limit = 5):
    data = data[np.isfinite(data.iloc[:,column])]
    mean = np.mean(data.iloc[:,column])
    std = np.std(data.iloc[:,column])
    idx = (data.iloc[:,column] > (mean - std * limit)) & (data.iloc[:,column] < (mean + std * limit))
    data_new = data[idx]
    return data_new




def preparing(data, truncate_limit = 5, winsorize_limit = 3):
    ncols = data.shape[1]
    for i in np.arange(2, ncols):
        data = truncate(data, i)
        data.iloc[:,i] = winsorize(data.iloc[:,i], winsorize_limit)
        data.iloc[:,i] = normalize(data.iloc[:,i])
    return data




def industry(data):
    industry = data.iloc[:,0].unique()
    for each in industry:
        data[each] = 0
        data.loc[data.iloc[:,0]== each, each] = 1
    return data

def styles(data):
    result = data.iloc[:,:2]
    result['Beta'] = data.BETA
    result['Momentum'] = data.RSTR
    result['Size'] = data.LNCAP
    result['RV'] = 0.74*data.DASTD + 0.16*data.CMRA + 0.1*data.HSIGMA
    result['NLS'] = data.NLSIZE
    result['BTP'] = data.BTOP
    result['Liquidity'] = 0.35*data.STOM + 0.35*data.STOQ + 0.3*data.STOA
    result['EY'] = 0.68*data.EPFWD + 0.21* data.CETOP + 0.11*data.ETOP
    result['Growth'] = 0.18*data.EGRLF + 0.11*data.EGRSF
    result['Leverage'] = 0.38*data.MLEV + 0.35* data.DTOA + 0.27 * data.BLEV
    return result

def dealna(data):
    data.dropna(inplace = True)
    tradeday = data.datetime.unique()
    nday = len(tradeday)
    data_count = data.code.value_counts()
    complete = data_count[data_count == nday].index.values 
    ind = data.code.isin(complete)
    data = data[ind] 
    data.index = np.arange(len(data))
    return data