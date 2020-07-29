import matplotlib.pyplot as plt
import yfinance as yf
from datetime import *
import dateutil.relativedelta
import datetime
import pandas as pd
import mplcursors
import matplotlib
import matplotlib.dates as mdates


class mainObj:
    def getData(self):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        data = yf.download('AMD', pastDate, currentDate)
        return data[["Volume"]]

    def printData(self, data):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            cleanData_print = data.copy()
            cleanData_print.reset_index(level=0, inplace=True)
            print(cleanData_print.to_string(index=False))

    def barGraph(self, data):
        fig, ax = plt.subplots(figsize=(15, 7))
        data.plot(kind='bar', ax=ax)
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        mplcursors.cursor(hover=True)
        plt.show()

    def lineGraph(self, data):
        data.reset_index(level=0, inplace=True)
        fig, ax = plt.subplots()
        ax.plot(data['Date'], data['Volume'])
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        mplcursors.cursor(hover=True)
        plt.show()


# setup
main = mainObj()

# commands
data = main.getData()
main.printData(data)
main.barGraph(data)
