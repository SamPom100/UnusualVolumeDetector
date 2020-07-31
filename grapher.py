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
    
    # Allow the user to specify the stock ticker at the start of running the script
    def __init__(self, ticker):
        self.ticker = ticker
    
    def getData(self):
        # Changed the ticker provided to the data variable to be the ticker that the user specifies at time of class instantiation
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        data = yf.download(self.ticker, pastDate, currentDate)
        return data[["Volume"]]

    def printData(self):
        data = self.getData()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            cleanData_print = data.copy()
            cleanData_print.reset_index(level=0, inplace=True)
            print(cleanData_print.to_string(index=False))

    def barGraph(self):
        data = self.getData()
        data.reset_index(level=0, inplace=True)
        tempList = []
        for x in data['Date']:
            tempList.append(x.date())
        data['goodDate'] = tempList
        data = data.drop('Date', 1)
        data.set_index('goodDate', inplace=True)
        ################
        fig, ax = plt.subplots(figsize=(15, 7))
        data.plot(kind='bar', ax=ax)
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        # Added ticker symbol to bar graph
        ax.set_title(self.ticker)
        mplcursors.cursor(hover=True)
        ################
        plt.show()

    def lineGraph(self):
        data = self.getData()
        data.reset_index(level=0, inplace=True)
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(data['Date'], data['Volume'])
        ax.get_yaxis().set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        # Added the ticker symbol to the graph
        ax.set_title(self.ticker)
        mplcursors.cursor(hover=True)
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        plt.show()

    def find_anomalies(self, random_data):
        anomalies = []
        random_data_std = np.std(random_data)
        random_data_mean = np.mean(random_data)
        # Set upper and lower limit to 3 standard deviation
        anomaly_cut_off = random_data_std * 4
        lower_limit = random_data_mean - anomaly_cut_off
        upper_limit = random_data_mean + anomaly_cut_off
        # Generate outliers
        for outlier in random_data:
            if outlier > upper_limit or outlier < lower_limit:
                anomalies.append(outlier)
        return anomalies

# User will enter a number from 1-7 based on what they want to do
def choose_commands():
    print("What commands would you like to do for stock ticker you chose?")
    select = input("Please enter the number ' 1, 2, 3, 4, 5, 6, 7'\n"
                + "1. Print the Bar Graph\n"
                + "2. Print the Line Graph\n"
                + "3. Print Summary\n"
                + "4. Print Bar Graph and Summary\n"
                + "5. Print Line graph and Summary\n"
                + "6. Print Bar Graph and Line Graph\n"
                + "7. Print all three\n"
                )
    return select

# Output what the user wants
def determine_outputs(select):
    if select == "1":
        main.barGraph()
    elif select == "2":
        main.lineGraph()
    elif select == "3":
        main.printData()
    elif select == "4":
        main.barGraph()
        main.printData()
    elif select == "5":
        main.lineGraph()
        main.printData()
    elif select == "6":
        main.barGraph()
        main.lineGraph()
    elif select == "7":
        main.barGraph()
        main.lineGraph()
        main.printData()
    else:
        print("Not a valid command")

# setup

# Allow the user to specify what stock ticker they want to look at when the script is ran
stock_ticker = input("Please enter FINRA stock ticker Symbol(i.e. Tesla > TSLA, Apple > AAPL)\n")

main = mainObj(stock_ticker)

option = choose_commands()
determine_outputs(option)
