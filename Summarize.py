from __future__ import division, print_function
from math import log, sqrt, floor
from pywt import wavedec
import numpy as np
from pandas import Series, DatetimeIndex

def limit_range(values, nm, nM):
    M = max(values)
    m = min(values)
    oldRange = M-m
    newRange = nM-nm
    for i in range(len(values)):
        values[i] = (((values[i] - m)*newRange)/oldRange) + nm

    return(values)


##def linreg(X, Y):
##    """
##    return a,b in solution to y = ax + b such that root mean square distance between trend line and original points is minimized
##    """
##    N = len(X)
##    Sx = Sy = Sxx = Syy = Sxy = 0.0
##    for x, y in zip(X, Y):
##        Sx = Sx + x
##        Sy = Sy + y
##        Sxx = Sxx + x*x
##        Syy = Syy + y*y
##        Sxy = Sxy + x*y
##    det = Sxx * N - Sx * Sx
##    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

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

def summarize(data):
    
    #############      Summarization       #############
    key = data.keys()
    key = key[0]
    values = [x["Close"] for x in data.values()[0]]
    V = len(values)

    # number of levels for DWT
    L = int(floor(log(V,2)))

    m,s = stanDev(values)
    values = [float((v-m)/s) for v in values]


    # dictionary with the summarization attributes
    stocks = {}
    stocks[key] = {}
    stocks[key]["extremas"] = []
    stocks[key]["extremas-x"] = []

    if L <= 20 and L > 1:
        w = 'db'+str(L)
        lof = 2*L - 1
    else:
        w = 'db2'
        lof = 2*2 - 1
    
    # During the same scan we produce the DWT coefficients
    coeffs = wavedec(values, w, level=L)    
    A = coeffs[0]
    D = coeffs[1:]

    # All D_i unfolded
    tempD = [i for array in D for i in array]
    
    # For Spectrum Power -> Cycle/Seasonality
    max_spec_p = []
    max_sum_l = []
    spec_ind = []

    # For extramas
    extr_ind = []

    # Scan each D_i
    for i in D:

        # Turning Points
        stocks[key]["extremas"].append(min(i))
        extr_ind.append(np.array(i).tolist().index(min(i)))
        
        stocks[key]["extremas"].append(max(i))
        extr_ind.append(np.array(i).tolist().index(max(i)))
        
        # Power Spectrum 
        spec_p = np.array(np.abs(np.fft.fft(i))**2).tolist()
        max_sum_l.append(sum(spec_p))
        max_val_c = max(spec_p)
        max_spec_p.append(max_val_c)
        spec_ind.append(spec_p.index(max_val_c))

    for p in range(len(extr_ind)):
        stocks[key]["extremas-x"].append(tempD.index(D[int(floor(p/2))][extr_ind[p]]))

    ps = max(max_spec_p)
    #stocks[key]["AL"] = A
    
    # Regression of A_L -> trend
    x = np.array(limit_range([i for i in range(len(A))],0,V))
    y = np.array(A)
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A,y)[0]
    stocks[key]["trend"] = {"x":range(V), "r":limit_range([m*i + c for i in range(V)],0,1)}
    

    # Turning points     
    stocks[key]["extremas"] = limit_range(stocks[key]["extremas"],0,1)
    stocks[key]["extremas-x"] = limit_range(stocks[key]["extremas-x"],0,V)
   
    # Cycle & Seasonality
    stocks[key]["start_cycle"] = tempD.index(D[max_spec_p.index(ps)][spec_ind[max_spec_p.index(ps)]])
    stocks[key]["cycle"] = spec_ind[max_spec_p.index(ps)]

    mps = max(max_sum_l)
    index = max_sum_l.index(mps)
    #stocks[key]["Ds"] = limit_range(np.array(D[max_spec_p.index(ps)]).tolist(),0,1)
    #stocks[key]["Ds-x"] = limit_range([tempD.index(z) for z in D[max_spec_p.index(ps)]],0,V)

    stocks[key]["Ds"] = limit_range(np.array(D[index]).tolist(),0,1)
    stocks[key]["Ds-x"] = limit_range([tempD.index(z) for z in D[index]],0,V)

    values = [x["Close"] for x in data.values()[0]]

    # NCSS
    vol = []
    for i in range(1,V):
        vol.append(100*(log(values[i])-log(values[i-1])))

    m = mean(vol)

    # Volatility
    vol = [((z-m)**2) for z in vol]
    stocks[key]["volatility"] = vol

    coeffs = wavedec(vol, w, level=L)
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
    stocks[key]["ncss"] = ncss_ind[max_ncss.index(max(max_ncss))]

    timeserie = convert2timeseries(data)

    return(timeserie, stocks)
