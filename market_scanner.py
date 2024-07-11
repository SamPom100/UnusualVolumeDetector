import os
import time
import yfinance as yf
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import NasdaqController
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import multiprocessing
import pandas as pd
import quandl
from dateutil.parser import parse
from yfinance.exceptions import YFInvalidPeriodError
import random

###########################
# THIS IS THE MAIN SCRIPT #
###########################

# Change variables to your liking then run the script
MONTH_CUTTOFF = 6  # 6
DAY_CUTTOFF = 4  # 3
STD_CUTTOFF = 9  # 9
MIN_STOCK_VOLUME = 10000


class mainObj:

    def __init__(self):
        pass

    def getDataQuandl(self, ticker, pastDate, currentDate):
        ticker = "WIKI/"+ticker
        mydata = quandl.get(ticker, start_date=pastDate,
                            end_date=currentDate, rows=50)
        mydata = mydata["Volume"]
        return mydata

    def getData(self, ticker):
        try:
            global MONTH_CUTOFF

            sys.stdout = open(os.devnull, "w")
            # maybe swap yahoo finance to quandl due to rate limits
            try:
                data = yf.Ticker(ticker).history(period=str(MONTH_CUTTOFF) + "mo", raise_errors=True)
            except (YFInvalidPeriodError) as e:
                try:
                    data = yf.Ticker(ticker).history(period=e.valid_ranges[-1])
                except:
                    return pd.DataFrame(columns=["Volume"])
            sys.stdout = sys.__stdout__

            # avoid yahoo finance rate limits
            time.sleep(random.uniform(0.2, 1.5))
            return data[["Volume"]]
        except:
            return pd.DataFrame(columns=["Volume"])

    def find_anomalies(self, data):
        global STD_CUTTOFF
        global MIN_STOCK_VOLUME
        indexs = []
        outliers = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * STD_CUTTOFF
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        for i in range(len(data)):
            temp = data['Volume'].iloc[i]
            if temp > upper_limit and temp > MIN_STOCK_VOLUME:
                indexs.append(str(data['Date'].iloc[i])[:-15])
                outliers.append(temp)
        d = {'Dates': indexs, 'Volume': outliers}
        return d

    def customPrint(self, d, tick):
        print("\n\n\n*******  " + tick.upper() + "  *******")
        print("Ticker is: "+tick.upper())
        for i in range(len(d['Dates'])):
            str1 = str(d['Dates'][i])
            str2 = str(d['Volume'][i])
            print(str1 + " - " + str2)
        print("*********************\n\n\n")

    def days_between(self, d1, d2):
        return abs((parse(d2) - parse(d1)).days)

    def parallel_wrapper(self, x, currentDate, positive_scans):
        global DAY_CUTTOFF
        d = (self.find_anomalies(self.getData(x)))
        if d['Dates']:
            for i in range(len(d['Dates'])):
                if self.days_between(str(currentDate), str(d['Dates'][i])) <= DAY_CUTTOFF:
                    self.customPrint(d, x)
                    stock = dict()
                    stock['Ticker'] = x
                    stock['TargetDate'] = d['Dates'][0]
                    stock['TargetVolume'] = str(
                        '{:,.2f}'.format(d['Volume'][0]))[:-3]
                    positive_scans.append(stock)

    def main_func(self):
        StocksController = NasdaqController(False) #tmp disable while ftp is down
        list_of_tickers = StocksController.getList()
        currentDate = datetime.date.today().strftime("%m-%d-%Y")
        start_time = time.time()

        # positive_scans = []
        # for x in tqdm(list_of_tickers):
        #     self.parallel_wrapper(x, currentDate, positive_scans)

        manager = multiprocessing.Manager()
        positive_scans = manager.list()

        cpu_count = multiprocessing.cpu_count()
        try:
            with parallel_backend('loky', n_jobs=cpu_count):
                Parallel()(delayed(self.parallel_wrapper)(x, currentDate, positive_scans)
                           for x in tqdm(list_of_tickers))
        except Exception as e:
            print(e)

        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))

        return positive_scans


if __name__ == '__main__':
    mainObj().main_func()
