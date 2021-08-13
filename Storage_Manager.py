from threading import Lock

import Ticker

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

        self.file_mutex.acquire()
        # Write each ticker score to appropriate SymbolDirectory
        for ticker in tickers:
            file_name = f'Data/{set}/{ticker.symbol}_data_{set}.csv'
            file_path = pathlib.Path(file_name)
            if file_path.exists():
                file = open(file_name, 'r')
            else:
                file = open(file_name, 'x')
                file.close()
                file = open(file_name, 'r')

            #TODO: Comment
            reader = csv.reader(file)
            values = list(reader)
            updated_values = []

            for value in values:
                updated_values.append(value[0])

            file.close()
            index = int(get_index())

            current_length = len(values)

            while len(updated_values) <= index:
                updated_values.append(0)

            updated_values[index] = float(updated_values[index]) + ticker.score
            #new_values = values[current_length:]

            file = open(file_name, 'w')
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(map(lambda x: [x], updated_values))

            file.close()

            write_to_csv(tickers, set, sub_name)

        self.file_mutex.release()
