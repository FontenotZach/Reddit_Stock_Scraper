from threading import Lock
from os import path

from Util import *

import csv
import pathlib
import Ticker

debug = False

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
    file_mutex = 0

    def __init__(self):
        self.file_mutex = Lock()

    def write_data(self, tickers, set, sub_name):
        if debug:
            print(f'Storage manager writing data for Subreddit {sub_name}')
            print(f'Data: {sub_name} {set} | {tickers}')

        self.file_mutex.acquire()
        # Write each ticker score to appropriate SymbolDirectory
        for ticker in tickers:
            file_name = f'Data/{set}/{ticker[0]}_data_{set}.csv'
            file_path = pathlib.Path(file_name)
        
            if debug:
                print(f'Storage manager checking and updating {file_name}')
            updated_values = []
            current_length = 0
            index = int(get_index())

            if file_path.exists():
                #TODO: Comment
                if debug:
                    print(f'Storage manager reading existing file {file_name}')
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

            if debug:
                print(f'Storage manager writing file {file_name}')
            file = open(file_name, 'w')
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(map(lambda x: [x], updated_values))

            file.close()

            write_to_csv(tickers, set, sub_name)

        self.file_mutex.release()
