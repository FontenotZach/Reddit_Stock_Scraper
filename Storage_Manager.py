import multiprocessing as mp
import os
import dataclasses

from pandas.io.parsers import read_csv

from Util import *

import csv
import pathlib

# /////////////////////////////////////////////////////////////////
#   Method: storage_manager
#   Purpose: Manages file output
#   Inputs:
#           'tickers' - list of scraped tickers
#           'set' - the set the comments belong to
#               > TODO: convert to enum
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
class StorageManager:
    WAIT_TIME = 60

    DEBUG = True

    def __init__(self, data_queue):
        self.file_mutex = mp.Lock()
        self.queue = data_queue

    def p(self, s):
        if self.DEBUG:
            print(f'SMAN {self.process_id}\t| {s}')

    def process_queue(self):
        self.process_id = os.getpid()

        while True:
            self.p(f'Processing data queue: {self.queue.qsize()}')
            while not self.queue.empty():
                (tickers, set, sub_name) = self.queue.get()
                self.write_data(tickers, set, sub_name)
            self.p(f'Done. Sleeping for {self.WAIT_TIME} seconds.')

            time.sleep(self.WAIT_TIME)


    def write_data(self, tickers, set, sub_name):
        self.p(f'Writing data for sub {sub_name}/{set}')

        self.file_mutex.acquire()
        now = datetime.datetime.now().isoformat('|', timespec='seconds')
        
        # PART 1
        # THESE ARE PER-TICKER ['timestamp', 'score']
        headers = ['date', 'score']
        # Write each ticker score to appropriate SymbolDirectory
        for ticker in tickers:
            file_name = f'Data/{set}/{sub_name}/{ticker[0]}_data_{set}.csv'

            df = self.read_csv(file_name, headers)
            df = df.append(pd.DataFrame([[now, ticker[1]]], columns=headers))

            # Write CSV with new timestamp and ticker score
            df.to_csv(file_name, index=False)
        
        # PART 2
        # Write the data to the subreddit file
        file_name = f'Data/Reddit-Stock-Scraper_{sub_name}_{set}.csv'
        headers = ['date', 'symbol', 'dataset', 'score']

        df = self.read_csv(file_name, headers)
        
        for ticker in tickers:
            df = df.append(pd.DataFrame([[now, ticker[0], set, ticker[1]]], columns=headers))
            
        df.to_csv(file_name, index=False)
        
        self.file_mutex.release()


    def read_csv(self, file_name, headers) -> pd.DataFrame:
        if os.path.exists(file_name):
            self.p(f'Storage manager checking and updating {file_name}')
            return pd.read_csv(file_name)
        else:
            self.p(f'Storage manager creating {file_name}')
            return pd.DataFrame(columns=headers)
        