import logging
import os
import sys
import time
import yfinance as yf
from datetime import date
from stocklist import NasdaqController
from tqdm import tqdm
import pandas as pd
from dateutil.parser import parse
from yfinance.exceptions import YFInvalidPeriodError, YFRateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter
import random
from dotenv import load_dotenv

load_dotenv()

def env_int(name, default):
    return int(os.getenv(name, default))

def env_float(name, default):
    return float(os.getenv(name, default))

logging.basicConfig(
    stream=sys.stderr,
    level=logging.WARNING,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

MONTH_CUTOFF = env_int("MONTH_CUTOFF", 6)
DAY_CUTOFF = env_int("DAY_CUTOFF", 4)
ROLLING_WINDOW = env_int("ROLLING_WINDOW", 20)
VOLUME_MULTIPLIER = env_float("VOLUME_MULTIPLIER", 3)
MIN_STOCK_VOLUME = env_int("MIN_STOCK_VOLUME", 10000)
MIN_PRICE = env_int("MIN_PRICE", 20)
MIN_MEDIAN_DOLLAR_VOLUME = env_int("MIN_MEDIAN_DOLLAR_VOLUME", 5000000)
REQUEST_DELAY_SECONDS = env_int("REQUEST_DELAY_SECONDS", 2)
BATCH_SIZE = env_int("BATCH_SIZE", 100)

class mainObj:
    @retry(
        retry=retry_if_exception_type(YFRateLimitError),
        wait=wait_exponential_jitter(initial=30, max=120),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def fetch_history(self, ticker):
        return yf.Ticker(ticker).history(
            period=str(MONTH_CUTOFF) + "mo", raise_errors=True
        )

    def getData(self, ticker):
        time.sleep(random.uniform(REQUEST_DELAY_SECONDS, REQUEST_DELAY_SECONDS + 1))
        try:
            data = self.fetch_history(ticker)
        except YFInvalidPeriodError as error:
            try:
                data = yf.Ticker(ticker).history(period=error.valid_ranges[-1])
            except Exception as fallback_error:
                logger.warning("Ticker %s failed during fallback request: %s", ticker, fallback_error)
                return pd.DataFrame(columns=["Volume"])
        except Exception as error:
            logger.warning("Ticker %s failed after retry policy: %s", ticker, error)
            return pd.DataFrame(columns=["Volume"])

        if data.empty:
            logger.warning("Ticker %s returned an empty response", ticker)
            return pd.DataFrame(columns=["Volume"])

        if "Close" not in data or "Volume" not in data:
            logger.warning("Ticker %s returned missing columns: %s", ticker, list(data.columns))
            return pd.DataFrame(columns=["Volume"])

        if data["Close"].iloc[-1] < MIN_PRICE:
            return pd.DataFrame(columns=["Volume"])

        return data[["Close", "Volume"]]


    def find_anomalies(self, data):
        if data.empty:
            return {'Dates': [], 'Volume': []}

        volumes = data['Volume']
        baseline = volumes.rolling(ROLLING_WINDOW).median().shift(1)
        anomalies = data.loc[
            baseline.notna()
            & (volumes >= baseline * VOLUME_MULTIPLIER)
            & (volumes >= MIN_STOCK_VOLUME)
        ]
        return {
            'Dates': [str(index).split(' ')[0] for index in anomalies.index],
            'Volume': anomalies['Volume'].tolist(),
        }

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

    def scan_ticker(self, ticker, current_date, positive_scans):
        self.scan_data(ticker, self.getData(ticker), current_date, positive_scans)

    def scan_data(self, ticker, data, current_date, positive_scans):
        if data.empty or "Close" not in data or "Volume" not in data:
            logger.warning("Ticker %s returned empty or incomplete batch data", ticker)
            return
        data = data.dropna(subset=["Close", "Volume"])
        if data.empty:
            logger.warning("Ticker %s returned no usable rows in batch data", ticker)
            return
        if data["Close"].iloc[-1] < MIN_PRICE:
            return
        median_dollar_volume = (data["Close"] * data["Volume"]).tail(ROLLING_WINDOW).median()
        if median_dollar_volume < MIN_MEDIAN_DOLLAR_VOLUME:
            logger.info("Ticker %s skipped for low median dollar volume: %.0f", ticker, median_dollar_volume)
            return
        anomalies = self.find_anomalies(data)
        for anomaly_date, volume in zip(anomalies['Dates'], anomalies['Volume']):
            if self.days_between(str(current_date), anomaly_date) <= DAY_CUTOFF:
                result = {'Dates': [anomaly_date], 'Volume': [volume]}
                self.customPrint(result, ticker)
                chart = self.build_chart(data, anomaly_date)
                result = {
                    'Ticker': ticker,
                    'TargetDate': anomaly_date,
                    'TargetVolume': f'{volume:,.0f}',
                    'Chart': chart,
                }
                if not any(
                    item['Ticker'] == ticker and item['TargetDate'] == anomaly_date
                    for item in positive_scans
                ):
                    positive_scans.append(result)

    def build_chart(self, data, anomaly_date):
        dates = [str(index).split(' ')[0] for index in data.index]
        try:
            anomaly_index = dates.index(anomaly_date)
        except ValueError:
            return []

        start = max(0, anomaly_index - ROLLING_WINDOW)
        values = data['Volume'].iloc[start:anomaly_index + 1].tolist()
        maximum = max(values) or 1
        return [
            {
                'Date': dates[index],
                'Volume': f'{value:,.0f}',
                'Height': max(4, round(value / maximum * 100)),
                'IsAnomaly': index == anomaly_index,
            }
            for index, value in zip(range(start, anomaly_index + 1), values)
        ]

    def main_func(self):
        StocksController = NasdaqController()
        list_of_tickers = StocksController.getList()
        current_date = date.today().strftime("%m-%d-%Y")
        start_time = time.time()
        positive_scans = []

        progress = tqdm(total=len(list_of_tickers))
        for start in range(0, len(list_of_tickers), BATCH_SIZE):
            tickers = list_of_tickers[start:start + BATCH_SIZE]
            if start:
                time.sleep(REQUEST_DELAY_SECONDS)
            try:
                batch = yf.download(
                    tickers,
                    period=str(MONTH_CUTOFF) + "mo",
                    group_by="ticker",
                    auto_adjust=False,
                    threads=False,
                    progress=False,
                    timeout=15,
                )
            except Exception as error:
                logger.warning("Batch starting at %s failed: %s", start, error)
                progress.update(len(tickers))
                continue

            for ticker in tickers:
                try:
                    data = batch[ticker][["Close", "Volume"]]
                except (KeyError, TypeError):
                    logger.warning("Ticker %s was missing from batch response", ticker)
                    progress.update(1)
                    continue
                self.scan_data(ticker, data, current_date, positive_scans)
                progress.update(1)
        progress.close()

        print("\n\n\n\n--- this took %s seconds to run ---" %
              (time.time() - start_time))

        return positive_scans

if __name__ == '__main__':
    mainObj().main_func()
