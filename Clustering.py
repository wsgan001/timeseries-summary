from mlpy import dtw_std
from math import log, floor, ceil
import numpy as np
import scipy
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
from matplotlib.pyplot import show


def cluster(data, sum_t, num):
    ##############        Clustering Initial Timeseries         ################
    plots = []
    D = len(data)
    # Calculate distance matrix using DTW
    dist_mat = np.empty(shape=(D,D))
    ii = 0
    labels1=[]
    for i in data.keys():
        jj = 0
        for j in data.keys():
            if ii==jj:
                dist_mat[ii][jj] = 0
            else:
                dist_mat[ii][jj] = dtw_std([z for z in data[i]], [z for z in data[j]], dist_only=True)
            jj += 1
        ii += 1
        labels1.append(i)

    # Use average linkage + DTW to remove outliers

    avg = linkage(squareform(dist_mat), method='average', metric='euclidean')
    clusters = fcluster(avg, floor(log(num)/log(2)),'maxclust')
    #print(clusters)
    freq = {}
    for i in clusters:
        if i not in freq:
            freq[i] = 1
        else:
            freq[i] += 1

    # Stocks which appear in almost empty clusters are considered outliers
    thresh = max(freq.values())
    mfe = [k for k,v in freq.items() if v > floor(num/10)]

    f = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    
    plt.subplot(211)
    plt.title("With Outliers")
    if num > 50:
        dendrogram(avg, leaf_font_size=10)
    else:
        dendrogram(avg, labels=labels1,leaf_font_size=11)
    locs, ll=plt.xticks()
    plt.setp(ll, rotation=90)
    
    
    
    # Remove outliers and their labels
    outliers = []
    for i in range((len(clusters)-1),-1,-1):
        if clusters[i] not in mfe:
            print("Outlier stock: "+str(labels1[i]))
            outliers.append(labels1[i])
            dist_mat = np.delete(dist_mat, i, 0)
            dist_mat = np.delete(dist_mat, i, 1)
            del labels1[i]

    print("Total Outliers: "+ str(len(outliers)))

    # Finally do the clustering !!!
    ward = linkage(dist_mat, method='ward', metric='euclidean')
    clusters1= fcluster(ward, 3,'maxclust')
    #print(clusters1)
    #print(labels1)
    plt.subplot(212)
    plt.title("After removing outliers")
    if num > 50:
        dendrogram(ward, no_labels=True, leaf_font_size=10)
    else:
        dendrogram(ward, labels=labels1,leaf_font_size=11)
    plt.subplots_adjust(hspace=.5)
    locs, ll=plt.xticks()
    plt.setp(ll, rotation=90)
    plots.append(f)

    ###########        Plot Initials & Summaries           ############
    
    f2 = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    plt.subplot(211)
    colormap = plt.cm.gist_ncar
    f2.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num)])
    for k in data.keys():
        data[k].plot()

    plt.subplot(212)
    f2.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, num)])
    for k in sum_t.keys():
        (sum_t[k]/10).plot()
    plt.xlim(0, len(sum_t[max(sum_t, key=len)])-1)
    plt.subplots_adjust(hspace=.32)
    plots.append(f2)


    #############       Clustering Summarized Timeseries        ############

    S = len(sum_t)
    dist_mat = np.empty(shape=(S,S))
    ii = 0
    labels2=[]
    # Calculate distance matrix using DTW
    for i in sum_t.keys():
        jj = 0
        for j in sum_t.keys():
            if ii==jj:
                dist_mat[ii][jj] = 0
            else:
                dist_mat[ii][jj] = dtw_std([z for z in sum_t[i]], [z for z in sum_t[j]], dist_only=True)
            jj += 1
        ii += 1
        labels2.append(i)

    # Use average linkage + DTW to remove outliers

    avg = linkage(squareform(dist_mat), method='average', metric='euclidean')
    clusters= fcluster(avg, floor(log(num,2)),'maxclust')
    #print(clusters)
    freq = {}
    for i in clusters:
        if i not in freq:
            freq[i] = 1
        else:
            freq[i] += 1
            
    # Stocks which appear in almost empty clusters are considered outliers
    thresh = max(freq.values())
    mfe = [k for k,v in freq.items() if v > floor(num/10)]
    f3 = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    plt.subplot(211)
    plt.title("With Outliers")
    if num > 50:
        dendrogram(avg, no_labels=True, leaf_font_size=10)
    else:
        dendrogram(avg, labels=labels2,leaf_font_size=11)
    locs, ll=plt.xticks()
    plt.setp(ll, rotation=90)
    
    outliers = []
    # Remove outliers
    for i in range((len(clusters)-1),-1,-1):
        if clusters[i] not in mfe:
            print("Outlier stock: "+str(labels2[i]))
            outliers.append(labels2[i])
            dist_mat = np.delete(dist_mat, i, 0)
            dist_mat = np.delete(dist_mat, i, 1)
            del labels2[i]

    print("Total Outliers: "+ str(len(outliers)))

    # Finally do the clustering !!!
    ward = linkage(dist_mat, method='ward', metric='euclidean')
    clusters2= fcluster(ward, 3,'maxclust')
    #print(clusters2)
    #print(labels2)
    plt.subplot(212)
    plt.title("After removing outliers")
    if num > 50:
        dendrogram(ward, leaf_font_size=10)
    else:
        dendrogram(ward, labels=labels2,leaf_font_size=11)
    plt.subplots_adjust(hspace=.5)
    locs, ll=plt.xticks()
    plt.setp(ll, rotation=90)

    plots.append(f3)
    colormap = plt.cm.gist_ncar
    f4 = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    plt.subplot(311)
    plt.title("Clusters with Initial Timeseries")
    for i in range(1,4):
        plt.subplot(int(310+i))
        
        f4.gca().set_color_cycle([colormap(ii) for ii in np.linspace(0, 0.9, num)])

        for j in range(len(clusters1)):
            if clusters1[j] == i:
                data[labels1[j]].plot(label=labels1[j])
                #plt.xlim(0, len(sum_t[max(sum_t, key=len)])-1)
                
        plt.legend(loc=4,prop={'size':10})
    plt.subplots_adjust(hspace=.55)
    plots.append(f4)
                
    f5 = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    plt.subplot(311)
    plt.title("Clusters based on Summarization Timeseries")
    for i in range(1,4):
        plt.subplot(int(310+i))
        f4.gca().set_color_cycle([colormap(ii) for ii in np.linspace(0, 0.9, num)])

        for j in range(len(clusters2)):
            if clusters2[j] == i:
                data[labels2[j]].plot(label=labels2[j])
                #plt.xlim(0, len(sum_t[max(sum_t, key=len)])-1)
                
        plt.legend(loc=4,prop={'size':10})
    plt.subplots_adjust(hspace=.55)
    plots.append(f5)

    f6 = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
    plt.subplot(311)
    plt.title("Clusters with Summarization Timeseries")
    for i in range(1,4):
        plt.subplot(int(310+i))
        colormap = plt.cm.gist_ncar
        f4.gca().set_color_cycle([colormap(ii) for ii in np.linspace(0, 0.9, num)])

        for j in range(len(clusters2)):
            if clusters2[j] == i:
                (sum_t[labels2[j]]/10).plot(label=labels2[j])
                #plt.xlim(0, len(sum_t[max(sum_t, key=len)])-1)
                
        plt.legend(loc=4,prop={'size':10})
    plt.subplots_adjust(hspace=.55)
    plots.append(f6)
    
    return(plots)
    
    
##    show()
