import pandas as pd
import numpy as np


###暂时放在这，等着会把工具函数放在一个模块里
def halflife(half_life = 63, length = 252):
    t = np.arange(length)
    w = 2 **(t/half_life) / sum(2 ** (t/half_life))
    return(w)

class StyleFactor(object):
    
    def __init__(self, data):
        self.data = data
        self.date = list(data.datetime)
        self.length = len(data)
    
    def RSTR(self, T = 504, L = 21, half_life = 126):
        rstr = np.tile(np.nan, self.length)
        for t in np.arange(T + L, self.length+1):
            rt = self.data.pct_chg[(t-T-L):(t-L)]
            rft = self.data.rf[(t-T-L):(t-L)]
            rstr[t-1] = sum((np.log(1+rt)-np.log(1+rft)) * halflife(half_life, length = T))
        return rstr
    
    def DASTD(self, half_life = 42,T = 252):
        w = halflife(half_life, length = T)
        dastd = np.tile(np.nan, self.length)
        for t in np.arange(T, self.length):
            re = self.data.pct_chg[t- T:t]
            r_avg = sum(w * re)
            dastd[t] = sum(w * (re - r_avg)**2)
        return dastd
    
    def CMRA(self, period = 12):
        cmra = np.tile(np.nan, self.length)
        for k in np.arange(period*21, self.length):
            r = []
            for i in range(period):
                r_month = np.prod(self.data.pct_chg[k-(i+1)*21:k-i*21]+1)-1
                rf_month = np.prod(self.data.rf[k-(i+1)*21:k-i*21]+1)-1
                r.append(np.log(1+r_month) - np.log(1+rf_month))
            Z = np.cumsum(r)
            cmra[k] = np.log(1+max(Z)) - np.log(1+min(Z))
        return cmra
    
    def NLSIZE(self):
        nlsize = self.data.mkt_cap_ard ** 3
        return nlsize
    
    def BTOP(self):
        btop = 1 / self.data.pb
        return btop
    
    def STOM(self, t = 21):
        stom = np.tile(np.nan, self.length)
        for k in np.arange(t, self.length):
            stom[k] = np.log(sum(self.data.volume[k-t:k]/self.data.share_totala[k-t:k]))
        return stom
    
    def STOQ(self, stom, t=21, T=3):
        stoq = np.tile(np.nan, self.length)
        for k in np.arange(T*t, self.length):
            idx = k - np.arange(T) *t
            stoq[k] = np.log(sum(np.exp(stom.iloc[idx]))/T)
        return stoq
    
    def STOA(self, stom, t=21, T =12):
        stoa = np.tile(np.nan, self.length)
        for k in np.arange(T*t, self.length):
            idx = k - np.arange(T) *t
            stoa[k] = np.log(sum(np.exp(stom.iloc[idx]))/T)
        return stoa
    
    def EPFWD(self):
        epfwd = 1 / self.data.pe_est_ftm
        return epfwd
    
    def CETOP(self):
        cetop = self.data.ocfps_ttm / self.data.close
        return cetop
    
    def ETOP(self):
        etop = 1/self.data.pe_ttm
        return etop
    
    def EGRO(self,period):
        year = [x[:4] for x in self.data.datetime]
        time = [int(x) for x in year]
        eps = self.data.eps_basic
        n = len(year)
        egro = np.tile(np.nan, n)
        for i in np.arange(period, n):
            x = time[i-period:i]
            y = eps[i-period:i]
            x_avg = np.mean(x)
            y_avg = np.mean(y)
            beta = sum((x - x_avg) * (y - y_avg))/sum((x - x_avg) **2)
            egro[i] = beta/x_avg
        return egro
    
    def MLEV(self):
        ME = self.data.close.shift(1) * self.data.share_totala.shift(1)
        PE = self.data.wgsd_pfd_stk 
        LD = self.data.wgsd_debt_lt
        mlev = (ME+PE+LD)/ME
        return mlev
        
    def DTOA(self):
        TD= self.data.wgsd_liabs
        TA= self.data.wgsd_assets
        dtoa = TD/TA
        return dtoa
    
    def BLEV(self):
        PE = self.data.wgsd_pfd_stk 
        LD = self.data.wgsd_debt_lt
        BE = self.data.wgsd_com_eq_par
        blev = (BE+PE+LD) / BE
        return blev
    