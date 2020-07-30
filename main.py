import matplotlib.pyplot as plt
import yfinance as yf
from datetime import *
import dateutil.relativedelta
import datetime
import pandas as pd
import mplcursors
import matplotlib
import matplotlib.dates as mdates
from dateutil import parser
import numpy as np


class mainObj:
    def getData(self):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=2)
        data = yf.download('TSLA', pastDate, currentDate)
        return data[["Volume"]]

    def printData(self, data):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            cleanData_print = data.copy()
            cleanData_print.reset_index(level=0, inplace=True)
            print(cleanData_print.to_string(index=False))

    def barGraph(self, data):
        data.reset_index(level=0, inplace=True)
        tempList = []
        for x in data['Date']:
            tempList.append(x.date())
        data['goodDate'] = tempList
        data = data.drop('Date', 1)
        data.set_index('goodDate', inplace=True)
        fig, ax = plt.subplots(figsize=(15, 7))
        data.plot(kind='bar', ax=ax)
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        mplcursors.cursor(hover=True)
        plt.show()

    def lineGraph(self, data):
        data.reset_index(level=0, inplace=True)
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(data['Date'], data['Volume'])
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        mplcursors.cursor(hover=True)
        plt.show()

    def find_anomalies(self, random_data):
        anomalies = []
        random_data_std = np.std(random_data)
        random_data_mean = np.mean(random_data)
        # Set upper and lower limit to 3 standard deviation
        anomaly_cut_off = random_data_std * 3

        lower_limit = random_data_mean - anomaly_cut_off
        upper_limit = random_data_mean + anomaly_cut_off
        # Generate outliers
        for outlier in random_data:
            if outlier > upper_limit or outlier < lower_limit:
                anomalies.append(outlier)
        return anomalies


# setup
main = mainObj()

# commands
data = main.getData()
# main.printData(data)
print(main.find_anomalies(data['Volume']))
main.barGraph(data)
