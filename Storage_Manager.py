import os
import datetime
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
    COOLDOWN_TIME = 90
    PROCESS_TYPE_NAME = 'SMAN'

    def __init__(self, data_queue):
        self.write_mutex = mp.Lock()
        self.queue = data_queue

    # /////////////////////////////////////////////////////////////////
    #   Method: storage_manager
    #   Purpose: Periodically looks at and processes the queue of ticker data to be written to disk.
    # /////////////////////////////////////////////////////////////////
    def storage_manager(self):
        self.PROCESS_ID = os.getpid()
        self.thread_print('Started storage manager')

        while True:
            self.debug_print(f'Processing data queue with {self.queue.qsize()} items.')
            if not self.queue.empty():
                pq = mp.Process(target=self.process_queue)
                pq.start()
                pq.join()

            self.debug_print(f'Done. Sleeping for {self.COOLDOWN_TIME} seconds.')
            time.sleep(self.COOLDOWN_TIME)

    # /////////////////////////////////////////////////////////////////
    #   Method: process_queue
    #   Purpose: Writes everything from the queue to disk.
    # /////////////////////////////////////////////////////////////////
    def process_queue(self):
        while not self.queue.empty():
            (tickers, set_name, sub_name) = self.queue.get()
            self.write_data(tickers=tickers, table=f'{sub_name}_{set_name}')
        
        


    # /////////////////////////////////////////////////////////////////
    #   Method: write_data
    #   Purpose: Writes the ticker data to a SQL database.
    #   Parameters:
    #       tickers - The ticker tuple to write TODO: Change this to ticker object
    #       table   - The name of the SQL database table to write the ticker to
    # /////////////////////////////////////////////////////////////////
    def write_data(self, tickers, table):
        self.debug_print(f'Writing data for {table}')

        # We acquire this mutex to ensure data can't be read and written while
        # the database may be changing due to another write_data process.
        self.write_mutex.acquire()

        # This software averages a ticker's performance per-hour on Reddit
        current_hour = datetime.datetime.now().isoformat(sep='-', timespec='hours')

        # Open the database and try to write ticker values
        conn = None
        try:
            conn = psql.connect(**get_sql_config())
            cur = conn.cursor()

            queries = []
            
            # Generate all necessary queries to insert or update data
            for ticker in tickers:
                identifier = f'{current_hour}_{ticker.symbol}'
                query = f'SELECT score FROM {table} WHERE time_ticker_identifier=\'{identifier}\''
                cur.execute(query)
                res = cur.fetchone()
                
                # If there is already a value for this ticker and timestamp, then update it
                if res is None:
                    queries.append(f'INSERT INTO {table} (time_ticker_identifier, score) VALUES (\'{identifier}\', {ticker.score})')
                else:
                    queries.append(f'UPDATE {table} SET score={res[0] + ticker.score} WHERE time_ticker_identifier=\'{identifier}\'')
            
            # Then execute and commit them all
            self.debug_print(f'Executing {len(queries)} queries.')
            for q in queries:
                cur.execute(q)
            conn.commit()

        except Exception as e:
            self.debug_print(f'SQL Exception {e}')
        finally:
            if conn is not None:
               conn.close()
        
        # Finally release the write mutex when everything completes
        self.write_mutex.release()
        return
