import multiprocessing as mp
import os
from Process_Wrapper import Process_Wrapper

from Util import *

# /////////////////////////////////////////////////////////////////
#   Method: storage_manager
#   Purpose: Manages file output
#   Inputs:
#           'tickers' - list of scraped tickers
#           'set' - the set the comments belong to
#               > TODO: convert to enum
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
class StorageManager(Process_Wrapper):
    WAIT_TIME = 20
    PROCESS_TYPE_NAME = 'SMAN'

    def __init__(self, data_queue):
        self.file_mutex = mp.Lock()
        self.queue = data_queue


    def process_queue(self):
        self.PROCESS_ID = os.getpid()

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
        self.now = datetime.datetime.now().isoformat(timespec='hours')
        
        # PART 1
        # THESE ARE PER-TICKER ['timestamp', 'score']
        headers = ['score']
        # Write each ticker score to appropriate SymbolDirectory
        for ticker in tickers:
            file_name = f'Data/{set}/{sub_name}/{ticker[0]}_data_{set}.csv'

            df = self.read_csv(file_name, headers)
            #self.p(f'Read in: {df}')

            if self.now in df.index:
                # If the timestamp already exists in the file, modify the value
                tmp = pd.Series([df.at[self.now, headers[0]] + ticker[1]], name=headers[0], index=[self.now])
                df.update(tmp)
            else:
                df = df.append(pd.DataFrame([ticker[1]], index=[self.now], columns=headers))

            # Write CSV with new timestamp and ticker score
            #self.p(f'Writing out: {df}')
            df.to_csv(file_name, index=True, index_label='timestamp')
        
        # PART 2
        # Write the data to the subreddit file
        file_name = f'Data/Reddit-Stock-Scraper_{sub_name}_{set}.csv'
        headers = ['symbol', 'score']

        df = self.read_csv(file_name, headers)
        #self.p(f'Read in: {df}')
        
        for ticker in tickers:
            if self.now in df.index and ticker[0] in df.at[self.now, headers[0]]:
                #self.p(f'Index {self.now} - Symbol {ticker[0]} found, updating.')
                tmp = pd.Series([df.at[self.now, headers[0]] + ticker[1]], name=headers[1], index=[self.now])
                df.update(tmp)
            else:
                df = df.append(pd.DataFrame([[ticker[0], ticker[1]]], index=[self.now], columns=headers))
        
        #self.p(f'Writing out: {df}')
        df.to_csv(file_name, index=True, index_label='timestamp')
        
        self.file_mutex.release()


    def read_csv(self, file_name, headers) -> pd.DataFrame:
        if os.path.exists(file_name):
            self.p(f'Storage manager checking and updating {file_name}')
            return pd.read_csv(file_name, index_col='timestamp')
        else:
            self.p(f'Storage manager creating {file_name}')
            return pd.DataFrame(index=[self.now], columns=headers).dropna()
            tmp = {}
            for x in headers:
                if x == 'symbol':
                    tmp[x] = ''
                else:
                    tmp[x] = 0

            return pd.DataFrame(tmp, index=[self.now], columns=headers)
            
        