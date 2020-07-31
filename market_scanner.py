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


class mainObj:
    def getData(self, ticker):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=5)
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
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

    def days_between(self, d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def main_func(self, cutoff):
        StocksController = NasdaqController(True)
        list_of_tickers = StocksController.getList()
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        start_time = time.time()
        for x in tqdm(list_of_tickers, miniters=1):
            d = (self.find_anomalies(self.getData(x), cutoff, currentDate))
            if d.empty:
                continue
            self.customPrint(d, x)

        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))


# input desired anomaly standard deviation cuttoff
# run time around 50 minutes for every single ticker.
mainObj().main_func(10)
