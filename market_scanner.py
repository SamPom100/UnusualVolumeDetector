import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import pandas as pd
import sys

from stocklist import NasdaqController

from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import multiprocessing


###########################
# THIS IS THE MAIN SCRIPT #
###########################

class mainObj:

    def __init__(self,_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=10): #default params 
        self.MONTH_CUTTOFF = _month_cuttoff
        self.DAY_CUTTOFF = _day_cuttoff
        self.STD_CUTTOFF = _std_cuttoff

    def getData(self, ticker):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - \
            dateutil.relativedelta.relativedelta(months=self.MONTH_CUTTOFF)

        # Fixes an off-by-one bug(yfinance not getting data for currentDate)
        currentDate += dateutil.relativedelta.relativedelta(days=1)

        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
        sys.stdout = sys.__stdout__
        return data[["Volume"]]

    def find_anomalies(self, data, currentDate):
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * self.STD_CUTTOFF
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        is_outlier = data['Volume'] > upper_limit
        is_in_three_days = ((currentDate - data['Date']) <= datetime.timedelta(days=self.DAY_CUTTOFF))
        return data[is_outlier & is_in_three_days]

    def customPrint(self, d, tick):
        print("\n\n\n*******  " + tick.upper() + "  *******")
        print("Ticker is: "+tick.upper())
        print(d)
        print("*********************\n\n\n")

    def parallel_wrapper(self,x, currentDate, positive_scans):
        d = (self.find_anomalies(self.getData(x), currentDate))
        if d.empty:
            return

        self.customPrint(d, x)
        stonk = dict()
        stonk['Ticker'] = x
        stonk['TargetDate'] = d['Date'].iloc[0]
        stonk['TargetVolume'] = d['Volume'].iloc[0]
        positive_scans.append(stonk)
        return

    def main_func(self,doFilter=False):
        manager = multiprocessing.Manager()
        positive_scans = manager.list()

        StocksController = NasdaqController(True)
        list_of_tickers = StocksController.getList()
        if doFilter:
            filtered_tickers = pd.read_csv('filtered_tickers.csv', names=['Ticker'], index_col=None, header=None).Ticker.astype('string')
            list_of_tickers = list(filtered_tickers.values)

        print(f'num tickers: {len(list_of_tickers)}')

        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = time.time()

        with parallel_backend('loky', n_jobs=multiprocessing.cpu_count()):
            Parallel()(delayed(self.parallel_wrapper)(x, currentDate, positive_scans)
                       for x in tqdm(list_of_tickers, miniters=1))

        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))

        return positive_scans


if __name__ == '__main__':
    results = mainObj(_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=10).main_func(doFilter=True) #customize these params to your liking
    for outlier in results:
        print(outlier)
    print(f'num outliers: {len(results)}')