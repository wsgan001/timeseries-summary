from glob import glob
from os import chdir, getcwd
from datetime import date as datetime_date

def simple_scan(directory):

    stocks = []
    num_of_days = 0

    cur_dir = getcwd()
    chdir(directory)
    
    # Reading data from files - Keeping dates and close value
    for fname in glob("*.txt"):
        file_iter = open(fname, 'rU')
        for line in file_iter:
            
            temp = line.strip().rstrip(' ').split(',')
            if temp[1] not in stocks:
                stocks.append(temp[1])
        
        file_iter.close()
        num_of_days += 1
    return(stocks, len(stocks), num_of_days)


def read_p_timeseries(directory, name, days='All'):

    stock_dic = {}
    num_of_days = 0
    
    cur_dir = getcwd()
    chdir(directory)
    
    # Reading data from files - Keeping dates and close value
    for fname in glob("*.txt"):
        if days== 'All' or num_of_days <= days-1:
            file_iter = open(fname, 'rU')
            for line in file_iter:
                temp = line.strip().rstrip(' ').split(',')
                if temp[1] == name:
                    date = datetime_date(int(temp[0][0:4]), int(temp[0][4:6]), int(temp[0][6:8]))
                
                    if temp[1] not in stock_dic:
                        stock_dic[temp[1]] = [{"Date":date, "Close":float(temp[5])}]
                    else:
                        stock_dic[temp[1]].append({"Date":date, "Close":float(temp[5])})
            file_iter.close()
            num_of_days += 1
            
    chdir(cur_dir)
    return(stock_dic)


def read_c_timeseries(directory, stocks='All', days='All'):

    stock_dic = {}
    num_of_days = 0
    all_dates = []
    
    cur_dir = getcwd()
    chdir(directory)
    
    # Reading data from files - Keeping dates and close value
    for fname in glob("*.txt"):
        num_of_stocks = 0
        if days== 'All' or num_of_days < days:
            file_iter = open(fname, 'rU')
            for line in file_iter:
                if stocks=='All' or num_of_stocks < stocks:
                    temp = line.strip().rstrip(' ').split(',')
                    date = datetime_date(int(temp[0][0:4]), int(temp[0][4:6]), int(temp[0][6:8]))
                    
                    if temp[1] not in stock_dic:
                        stock_dic[temp[1]] = [{"Date":date, "Close":float(temp[5])}]
                    else:
                        stock_dic[temp[1]].append({"Date":date, "Close":float(temp[5])})
                else:
                    break
                num_of_stocks += 1
            all_dates.append(date) 
            file_iter.close()
            num_of_days += 1
    chdir(cur_dir)
    return(stock_dic, all_dates)
