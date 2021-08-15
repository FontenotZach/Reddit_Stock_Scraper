import multiprocessing as mp
import os
import queue

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
    process_id = 0
    file_mutex = 0
    queue = 0

    WAIT_TIME = 60

    debug = True

    def __init__(self, data_queue):
        self.file_mutex = mp.Lock()
        self.queue = data_queue

    def p(self, s):
        if self.debug:
            print(f'SMAN {self.process_id}\t| {s}')

    def process_queue(self):
        self.process_id = os.getpid()

        while True:
            self.p(f'Processing data queue: {self.queue.qsize()}')
            while not self.queue.empty():
                (tickers, set, sub_name) = self.queue.get()
                self.write_data(tickers, set, sub_name)

            time.sleep(self.WAIT_TIME)


    def write_data(self, tickers, set, sub_name):
        self.p(f'Storage manager writing data for sub{sub_name}/{set}')

        self.file_mutex.acquire()
        # Write each ticker score to appropriate SymbolDirectory
        for ticker in tickers:
            file_name = f'Data/{set}/{ticker[0]}_data_{set}.csv'
            file_path = pathlib.Path(file_name)
        
            self.p(f'Storage manager checking and updating {file_name}')
            updated_values = []
            current_length = 0
            index = int(get_index())

            if file_path.exists():
                #TODO: Comment
                self.p('Storage manager reading existing file {file_name}')
                file = open(file_name, 'r')

                reader = csv.reader(file)
                values = list(reader)
                current_length = len(values)

                for row in values:
                    updated_values.append(row[0])
                file.close()

            while len(updated_values) <= index:
                updated_values.append(0)

            updated_values[index] = float(updated_values[index]) + ticker[1]

            self.p(f'Storage manager writing file {file_name}')
            file = open(file_name, 'w')
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(map(lambda x: [x], updated_values))

            file.close()

            write_to_csv(tickers, set, sub_name)
        self.file_mutex.release()
