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


from __future__ import division, print_function
from math import sqrt, log, floor
from pywt import wavedec
import numpy as np
import pyparsing
from pandas import Series, DatetimeIndex

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


def convert2timeseries(data):
    stocks = {}
    for k, v in data.items():
        stocks[k] = Series([d["Close"] for d in v], index=DatetimeIndex([d["Date"] for d in v],freq="D"))
    return(stocks)

def summarize(data, steps):

    #############      Summarization       #############
    key = data.keys()
    key = key[0]
    values = [x["Close"] for x in data.values()[0]]
    values = values[0:(len(values)-steps)]
    V = len(values)
    # number of levels for DWT
    L = int(floor( float(log(V)/log(2)) ))

##    m,s = stanDev(values)
##    values = [float((v-m)/s) for v in values]

    # dictionary with the summarization attributes
    stocks = {}
    stocks[key] = {}

    if L <= 20 and L > 1:
        w = 'db'+str(L)
    else:
        w = 'db2'
    
    # During the same scan we produce the DWT coefficients
    coeffs = wavedec(values,w, level=L)    
    A = coeffs[0]
    D = coeffs[1:]
    
    # All D_i unfolded
    tempD = [i for array in D for i in array]
    
    # For Spectrum Power -> Cycle/Seasonality
    max_sum_l = []
    max_spec_p = []
    spec_ind = []

    # Scan each D_i
    for i in D:
        # Power Spectrum 
        spec_p = np.array(np.abs(np.fft.fft(i))**2).tolist()
        max_sum_l.append(sum(spec_p))
        
        max_val_c = max(spec_p)
        max_spec_p.append(max_val_c)
        spec_ind.append(spec_p.index(max_val_c))

    mps = max(max_sum_l)
    index = max_sum_l.index(mps)
    #stocks[key]["maxDs"] = np.array(D[index]).tolist()
    #print(index, " @ ", stocks[key]["maxDs"])
    
    x = np.array(limit_range([i for i in range(len(A))],0,V))
    y = np.array(A)
    
##    A = np.vstack([x, np.ones(len(x))]).T
##    m, c = np.linalg.lstsq(A,y)[0]
    
    p = np.polyfit(x, y, 1)
    #print("A:",[p[0]*i + p[1] for i in x] )

    ps = max(max_spec_p)
    stocks[key]["AL"] = A
    #print(A)
    
    # Seasonality
   
    stocks[key]["Ds"] = np.array(D[index]).tolist()
    stocks[key]["Ds-x"] = [tempD.index(z) for z in D[index]]
    #print("index: ", max_spec_p.index(ps),"Ds = ",stocks[key]["Ds"])
    timeserie = convert2timeseries(data)

    return(timeserie, stocks)
