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
from copy import deepcopy
from math import log, floor, sqrt
from pywt import wavedec
import numpy as np
import pyparsing
import matplotlib.pyplot as plt
import pandas as pd
from pandas import Series, DatetimeIndex

def limit_range(values, nm, nM):
    M = max(values)
    m = min(values)
    oldRange = M-m
    newRange = nM-nm
    for i in range(len(values)):
        values[i] = (((values[i] - m)*newRange)/oldRange) + nm

    return(values)

def rel_limit_range(values, om, oM, nm, nM):
    oldRange = oM-om
    newRange = nM-nm
    for i in range(len(values)):
        values[i] = (((values[i] - om)*newRange)/oldRange) + nm

    return(values)


def mean(values):
    return (sum(values)*1.0)/len(values)

def stanDev(values):
    m = mean(values)
    total_sum = 0
    for i in range(len(values)):
        total_sum += (values[i]-m)**2

    under_root = (total_sum*1.0)/len(values)
    return (m, sqrt(under_root))

def convert2timeseries(data):
    stocks = {}
    for k, v in data.items():
        stocks[k] = Series([d["Close"] for d in v], index=DatetimeIndex([d["Date"] for d in v],freq="D"))
    return(stocks)

def convert2timeseries_nd(data):
    stocks = {}
    for k, v in data.items():
        stocks[k] = Series(v["Close"], index=v["Index"])
    return(stocks)
    

def summarize(data, all_dates, length):

    #############      Summarization       #############
    
    V = length

    # number of levels for DWT
    L = int(floor( float(log(V,2))))


    # dictionary with the summarization attributes
    stocks = {}
    
    #############       Preprocessing & Summarization       #############
    toRemove = []
    # Remove stocks that have 10 or more missing values (10 <= days)
    # Fill in missing values -> (n_(i-1) + n_(i+1))/2
    for k, v in data.items():
        if len(v) <= (V-10):
            toRemove.append(k)
            print("Removing ",k," stock due to # of missing values!")
        else:
            for d in all_dates:
                flag = False
                index = -1
                for i in range(len(v)):
                    if d == v[i]["Date"]:
                        flag = True
                        break
                    elif d < v[i]["Date"]:
                        index = i
                        break
                if not(flag) and index != -1:
                    print(k,": Missing Value Detected @ ",index," position!")
                    data[k].append({"Date":d, "Close":float((float(v[i]["Close"] + v[i-1]["Close"])/2))})
                    
            data[k].sort(key=lambda x:x["Date"])
    for k in toRemove:
        del data[k]
    backup = deepcopy(data)

    m,s = stanDev([k["Close"] for v in data.values() for k in v])
    
    if L <= 5 and L > 1:
        w = 'coif'+str(L)
        lof = 2*L - 1
    else:
        w = 'coif2'
        lof = 2*2 - 1


    summarized_t = {}
    # Normalize, extract features and collect useful data for creating
    # timeseries as summary
    for k, v in data.items():

        # Normalize using Z-Score
        for i in range(len(v)):
            data[k][i]["Close"] = float((data[k][i]["Close"] - m)/s)
            
        # During the same scan we produce the DWT coefficients
        coeffs = wavedec([x["Close"] for x in data[k]], w, level=L)    
        A = coeffs[0]
        D = coeffs[1:]

        # All D_i unfolded
        tempD = [i for array in D for i in array]
        
        # For Spectrum Power -> Cycle/Seasonality
        max_spec_p = []
        max_sum_l = []
        spec_ind = []

        # For extremas
        extr_ind = []

        # Scan each D_i
        for i in D:
            if k not in stocks:
                stocks[k] = {}
                stocks[k]["extremas"] = []
                stocks[k]["extremas-x"] = []
            
            # Turning Points
            stocks[k]["extremas"].append(min(i))
            extr_ind.append(np.array(i).tolist().index(min(i)))
            
            stocks[k]["extremas"].append(max(i))
            extr_ind.append(np.array(i).tolist().index(max(i)))

            # Power Spectrum 
            spec_p = np.array(np.abs(np.fft.fft(i))**2).tolist()
            max_val_c = max(spec_p)
            max_sum_l.append(sum(spec_p))
            max_spec_p.append(max_val_c)
            spec_ind.append(spec_p.index(max_val_c))

        ps = max(max_spec_p)

        # Cycle & Seasonality
        stocks[k]["cycle"] = tempD.index(D[max_spec_p.index(ps)][spec_ind[max_spec_p.index(ps)]])

        mps = max(max_sum_l)
        index = max_sum_l.index(mps)
        #stocks[k]["Ds"] = limit_range(np.array(D[index]).tolist(),0,1)
        stocks[k]["Ds"] = np.array(D[index]).tolist()
        stocks[k]["Ds-x"] = [tempD.index(z) for z in D[index]]

        stocks[k]["AL"] = A
        # Regression of A_L -> trend
        x = np.array(limit_range([i for i in range(len(A))],0,V))
        y = np.array(A)
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A,y)[0]

        stocks[k]["trend"] = {"x":stocks[k]["Ds-x"], "r":[m*i + c for i in stocks[k]["Ds-x"]]}
        
        # Turning points
        for p in range(len(extr_ind)):
            stocks[k]["extremas-x"].append(tempD.index(D[int(floor(p/2))][extr_ind[p]]))
        stocks[k]["extremas"] = stocks[k]["extremas"]

        # For producing summarized timeseries
        e = []
        close_vals = [stocks[k]["Ds"][i] + stocks[k]["trend"]["r"][i] for i in range(len(stocks[k]["Ds"]))]
        summarized_t[k] = {"Index":range(len(stocks[k]["Ds"])), "Close": close_vals}

    # Making timeseries by using trend and power  spectrum
    m,s = stanDev([k for v in summarized_t.values() for k in v["Close"]])
    for k, v in summarized_t.items():
        for i in range(len(v)):
            summarized_t[k]["Close"][i] = float((summarized_t[k]["Close"][i] - m)/s)
    
    summarized_t = convert2timeseries_nd(summarized_t)

    # We no longer need normalized timeseries
    ret = convert2timeseries(data)
    data = deepcopy(backup)
    del backup

    for k, v in data.items():

        vol = []
        for i in range(1,len(v)):
            vol.append(100*(log(v[i]["Close"])-log(v[i-1]["Close"])))

        m = mean(vol)

        # Volatility
        vol = [((z-m)**2) for z in vol]

        coeffs = wavedec(vol,w, level=L)
        A = coeffs[0]
        D = coeffs[1:]

        # All D_i unfolded
        tempD = [i for array in D for i in array]
        
        # NCSS: for change variance
        ncss_ind = []
        max_ncss = []

        # Scan each D_i
        for i in D:
            pk = []
            nn = []
            par = sum([tempD[s]**2 for s in range(lof, V-1)])
            for j in range(L, V-1):
                pp =(sum([tempD[z]**2 for z in range(lof, j)])*1.0)/par
                pk.append(max( [ ((j+1)/(V-1))-pp, pp - (j/(V-1)) ]))
                nn.append(j)

            # NCSS Index Info
            max_pk = max(pk)
            max_ncss.append(max_pk)
            ncss_ind.append(nn[pk.index(max_pk)])
        stocks[k]["ncss"] = ncss_ind[max_ncss.index(max(max_ncss))]

    return(ret, summarized_t)

