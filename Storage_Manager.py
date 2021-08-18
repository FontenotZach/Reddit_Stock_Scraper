import os
import multiprocessing as mp
import psycopg2 as psql
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
                (tickers, set_name, sub_name) = self.queue.get()
                self.write_data(tickers=tickers, table=f'{sub_name}_{set_name}')
            self.p(f'Done. Sleeping for {self.WAIT_TIME} seconds.')

            time.sleep(self.WAIT_TIME)


    def write_data(self, tickers, table):
        self.p(f'Writing data for sub {table}')

        self.file_mutex.acquire()
        current_hour_stamp = datetime.datetime.now().isoformat(timespec='hours')

        # Open the database and try to write ticker values
        conn = None
        try:
            conn = psql.connect(**get_sql_config())
            cur = conn.cursor()

            queries = []
            
            # Generate all necessary queries to insert or update data
            for ticker in tickers:
                query = f'SELECT score FROM {table} WHERE hour_stamp=\'{current_hour_stamp}\' AND ticker_symbol=\'{ticker[0]}\''
                cur.execute(query)
                res = cur.fetchone()
                
                # If there is already a value for this ticker and timestamp, then update it
                if res is None:
                    queries.append(f'INSERT INTO {table} (hour_stamp, ticker_symbol, score) VALUES (\'{current_hour_stamp}\', \'{ticker[0]}\', {ticker[1]})')
                else:
                    queries.append(f'UPDATE {table} SET score={res[0] + ticker[1]} WHERE hour_stamp=\'{current_hour_stamp}\' AND ticker_symbol=\'{ticker[0]}\'')
            
            # Then execute and commit them all
            for q in queries:
                self.p(q)
                cur.execute(q)
            conn.commit()

        except Exception as e:
            self.p(f'SQL Exception {e}')
        finally:
            if conn is not None:
               conn.close()
        
        self.file_mutex.release()
