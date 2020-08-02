from stocklist import NasdaqController
import market_scanner

from joblib import Parallel, delayed, parallel_backend
import multiprocessing
from tqdm import tqdm

import numpy as np
import pandas as pd

class stockFilter:

    def __init__(self,manager,master_list):
        self.scanner = market_scanner.mainObj(_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=10)
        self.tickers = NasdaqController(True).getList()
        self.frame = pd.DataFrame(columns=['Ticker','AvgVol'])

        with parallel_backend('loky', n_jobs=multiprocessing.cpu_count()):
            Parallel()(delayed(self.parallel_getData_wrapper)(x, master_list)
                for x in tqdm(self.tickers, miniters=1))

        self.frame = pd.DataFrame.from_records(master_list)

        low = 0.0
        high = 0.95

        self.filtered_tickers = self.frame[self.frame.AvgVol.between(*self.frame.AvgVol.quantile([low, high]).tolist())].Ticker
        self.filtered_tickers.to_csv('filtered_tickers.csv',index=False)

        print("filtered tickers by avg volume (0-95th percentile)")

    def parallel_getData_wrapper(self,x,master_list):
        d = self.scanner.getData(x)
        if d.empty:
            return
        else:
            data_mean = np.mean(d)
            new_row = {'Ticker':x, 'AvgVol':data_mean.values[0]}
            master_list.append(new_row)

if __name__ == "__main__":
    manager = multiprocessing.Manager()
    master_list = manager.list()
    tmp = stockFilter(manager,master_list)