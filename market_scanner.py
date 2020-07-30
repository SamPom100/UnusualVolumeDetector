import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import NasdaqController


class mainObj:
    def getData(self, ticker):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=5)
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
        sys.stdout = sys.__stdout__
        return data[["Volume"]]

    def find_anomalies(self, data, cutoff):
        anomalies = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        indexs = data[data['Volume'] > upper_limit].index.tolist()
        outliers = data[data['Volume'] > upper_limit].Volume.tolist()
        index_clean = [str(x)[:-9] for x in indexs]
        d = {'Dates': index_clean, 'Volume': outliers}
        return d

    def find_anomalies_two(self, data, cutoff):
        indexs = []
        outliers = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        for i in range(len(data)):
            temp = data['Volume'].iloc[i]
            if temp > upper_limit:
                indexs.append(str(data['Date'].iloc[i])[:-9])
                outliers.append(temp)
        d = {'Dates': indexs, 'Volume': outliers}
        return d

    def customPrint(self, d, tick):
        if d['Dates']:
            print("\n*******  " + tick.upper() + "  *******")
            print("Ticker is: "+tick.upper())
            for i in range(len(d['Dates'])):
                str1 = str(d['Dates'][i])
                str2 = str(d['Volume'][i])
                print(str1 + " - " + str2)
            print("*********************")

    def main_func(self, cutoff):
        StocksController = NasdaqController(True)
        list_of_tickers = StocksController.getList()
        # list_of_tickers = ['aapl', 'amzn', 'nvda', 'ostk', 'msft',
        #                  'fb', 'shop', 'baba', 'tmus', 'f', 'sq', 'docu', 'nflx']
        print("-- updates complete --")
        start_time = time.time()
        for x in list_of_tickers:
            test = (self.find_anomalies_two(self.getData(x), cutoff))
            self.customPrint(test, x)
        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))


# input desired anomaly standard deviation cuttoff
mainObj().main_func(12)
