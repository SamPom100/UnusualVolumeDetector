import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import NasdaqController
from tqdm import tqdm

from joblib import Parallel, delayed, parallel_backend
import multiprocessing

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


class mainObj:

    def __init__(self):
        pass

    def getData(self, ticker):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=5)
        sys.stdout = open(os.devnull, "w")

        #data = yf.download(ticker, pastDate, currentDate)
        data = yf.download(tickers = ticker,period='6mo')
        #comment above line out instead if you want the original window

        sys.stdout = sys.__stdout__
        return data[["Volume"]]


    def find_anomalies(self, data, cutoff, currentDate):
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        is_outlier = data['Volume'] > upper_limit
        is_in_three_days = ((currentDate - data['Date']) <= datetime.timedelta(days=3))
        return data[is_outlier & is_in_three_days]

    def customPrint(self, d, tick):
        print("\n\n\n*******  " + tick.upper() + "  *******")
        print("Ticker is: "+tick.upper())
        print(d)
        print("*********************\n\n\n")


    def parallel_wrapper(self,x, cutoff, currentDate, positive_scans):
        d = (self.find_anomalies(self.getData(x), cutoff, currentDate))
        if d.empty:
            return

        self.customPrint(d, x)
        stonk = dict()
        stonk['Ticker'] = x
        stonk['TargetDate'] = d['Date'].iloc[0]
        stonk['TargetVolume'] = d['Volume'].iloc[0]
        positive_scans.append(stonk)

    def main_func(self, cutoff):
        StocksController = NasdaqController(True)
        list_of_tickers = StocksController.getList()
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = time.time()

        manager = multiprocessing.Manager()
        positive_scans = manager.list()

        with parallel_backend('loky', n_jobs=multiprocessing.cpu_count()):
            Parallel()(delayed(self.parallel_wrapper)(x, cutoff, currentDate, positive_scans) for x in tqdm(list_of_tickers, miniters=1) )

        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))

        return positive_scans

if __name__ == '__main__':
    sys.excepthook = show_exception_and_exit
    mainObj().main_func(10)
# input desired anomaly standard deviation cuttoff
# run time around 50 minutes for every single ticker.