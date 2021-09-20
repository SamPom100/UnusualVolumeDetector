import yfinance as yf
from datetime import date
import dateutil.relativedelta
import datetime
import pandas as pd
from pandas_datareader import data as pdr
import quandl


def getData(ticker):
    currentDate = datetime.date.today() + datetime.timedelta(days=1)
    pastDate = currentDate - \
    dateutil.relativedelta.relativedelta(months=3)
    data = yf.download(ticker, pastDate, currentDate)
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(data[["Volume"]])


getData("MSFT")

#when on probation, 18 calls results in a lock

def getQuan():
    start = currentDate = datetime.date.today() + datetime.timedelta(days=1)
    end = pastDate = currentDate - \
        dateutil.relativedelta.relativedelta(months=1)
    
    mydata = quandl.get("WIKI/AAPL", start_date=pastDate, end_date=currentDate, rows=50)
    mydata = mydata["Volume"]
    print(mydata)