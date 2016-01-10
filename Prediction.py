'''
The MIT License (MIT)

Copyright (c) 2016 kagklis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from math import sqrt
import numpy as np
from copy import deepcopy
from pandas import Series, DatetimeIndex
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot
from statsmodels.tsa.arima_model import _arma_predict_out_of_sample

def limit_range(values, nm, nM):
    M = max(values)
    m = min(values)
    oldRange = M-m
    newRange = nM-nm
    for i in range(len(values)):
        values[i] = (((values[i] - m)*newRange)/oldRange) + nm

    return(values)

def mean(values):
    return (sum(values)*1.0)/len(values)


def stanDev(values):
    m = mean(values)
    total_sum = 0
    for i in range(len(values)):
        total_sum += (values[i]-m)**2

    under_root = (total_sum*1.0)/len(values)
    return (m,sqrt(under_root))


def linreg(X, Y):
    """
    return a,b in solution to y = ax + b such that root mean square distance between trend line and original points is minimized
    """
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det


def predict(data, Ds, AL, steps):
    
    key = data.keys()
    key = key[0]
    V = len(data[key])
   
    # Create N-step prediction using ARMA method on the initial timeseries
    res = sm.tsa.ARMA(data[key][0:(V-1-steps)], (3, 0)).fit()
    params = res.params
    residuals = res.resid
    p = res.k_ar
    q = res.k_ma
    k_exog = res.k_exog
    k_trend = res.k_trend
    temp = _arma_predict_out_of_sample(params, steps, residuals, p, q, k_trend, k_exog, endog=data[key], exog=None, start=V-steps)
    
    pArma = [data[key][V-steps-1]]
    pArma.extend(temp)
    arma_t = Series(pArma, index=DatetimeIndex([data[key].index[V-steps-1+i] for i in range(steps+1)],freq="D"))
    
    print("ARMA: \n",arma_t)
    pred = deepcopy(data)
    offset = 1
    # Create N-step prediction using recursive ARMA method on the initial timeseries
    for ss in range(steps, 0, -offset):
        res = sm.tsa.ARMA(pred[key][0:(V-1-ss)], (3, 0)).fit()
        params = res.params
        residuals = res.resid
        p = res.k_ar
        q = res.k_ma
        k_exog = res.k_exog
        k_trend = res.k_trend
        pred[key][V-ss] = _arma_predict_out_of_sample(params, offset, residuals, p, q, k_trend, k_exog, endog=data[key], exog=None, start=V-ss)[0]
        
    
    rArma = [data[key][V-steps-1]]
    rArma.extend(pred[key][V-steps:(V+1)])
    arma_t_r = Series(rArma, index=DatetimeIndex([data[key].index[V-steps-1+i] for i in range(steps+1)],freq="D"))
    
    print("rARMA: \n",arma_t_r)


    
    
    # Create N-step prediction using Summarization Features
    ext_Ds = np.pad(Ds, steps, mode='symmetric')
    ext_Ds = [ext_Ds[len(ext_Ds)-steps+i] for i in range(steps)]
    #print("Ds:",ext_Ds)
    m, s = stanDev(data[key])
    
    a,b = linreg(range(len(AL)), AL)
    r = [a*index + b for index in range(len(AL)+steps)]
    
    temp2 = [(ext_Ds[i]+r[len(AL)-1+i])/10 for i in range(steps)]
    
    fcst = [data[key][V-steps-1]]
    fcst.extend(temp2)
    summarized_t = Series(fcst, index=DatetimeIndex([data[key].index[V-steps-1+i] for i in range(steps+1)],freq="D"))
    print("Summarized: \n",summarized_t)
    
    return(arma_t, arma_t_r, summarized_t)
