import datetime
import random
import time
import os
import multiprocessing as mp

from Util import *
from Storage_Manager import *
from Comment_Info import *

class Queue_Reader:
    # 60 Second wait period to let the queue fill up
    COOLDOWN_TIME = 50

    DEBUG = True

    # /////////////////////////////////////////////////////////////////
    #   Method:     __init__
    #   Purpose:    Initializes class variables
    #   Inputs:
    #       'comment_queue' - A queue holding comments to process
    #       'sub_name'      - Name of the Subreddit being scraped
    #       'storage_queue' - A queue holding data to be written to disk
    # /////////////////////////////////////////////////////////////////
    def __init__(self, comment_queue, sub_name, storage_queue):
        # Initialize class variables
        self.sub_name = sub_name
        self.comment_queue = comment_queue
        self.storage_queue = storage_queue
    
    def p(self, s):
        if self.DEBUG:
            print(f'COM {self.process_id}\t| {s}')

    # /////////////////////////////////////////////////////////////////
    #   Method:     reader_wrapper
    #   Purpose:    Manages stream_scraper_reader
    # /////////////////////////////////////////////////////////////////
    def reader_wrapper(self):
        self.process_id = os.getpid()
        print(f'COM {self.process_id}\t| Comment Queue reader started on {self.sub_name}')
        
        # Run the reader script on a set schedule
        while True:
            #start_time = datetime.datetime.now()
            reader = mp.Process(target=self.comment_queue_reader)
            reader.start()
            reader.join()

            # Want to sleep for between 50 and 70 seconds
            t = self.COOLDOWN_TIME + (random.random() * 20.0)
            self.p(f'Sleeping for {t:.2f} seconds')
            time.sleep(t)
        
            #time_diff = start_time - datetime.datetime.now()
            #sleep_time = (self.COOLDOWN_TIME - time_diff.seconds)
            #print(f'SSR {self.process_id}\t| Waiting for {sleep_time} seconds.')
            #time.sleep(sleep_time)


    # /////////////////////////////////////////////////////////////////
    #   Method:     comment_queue_reader
    #   Purpose:    Collect live reddit comments and pass them to queue
    # /////////////////////////////////////////////////////////////////
    def comment_queue_reader(self):
        if self.comment_queue.empty():
            self.p(f'{self.sub_name}: no comments')
            return

        self.p(f'{self.sub_name}: {self.comment_queue.qsize()} total comments collected')
        comments_processed = 0  # total comments processed
        tickers = {'hot':{}, 'stream':{}} # dictionary of tickers (key: symbol, value: score)

        # Pops all comments each hour until queue is empty
        while not self.comment_queue.empty():
            # Checks if there is a comment to get
            # Comment Queue: Queue(Tuple(string, comment))
            r_comment = self.comment_queue.get()
            
            comments_processed += 1
            comment = Comment_Info(r_comment[1].body, -1, r_comment[1].score)
            ticker_result = comment_score(comment)

            if ticker_result is not None:
                ticker_type = r_comment[0]
                # Pulls out metion data and comglomerates for each ticker
                for new_ticker in ticker_result:
                    symbol = new_ticker.symbol
                    if symbol in tickers[ticker_type]:
                        tickers[ticker_type][symbol] = tickers[ticker_type][symbol] + new_ticker.score
                    else:
                        tickers[ticker_type][symbol] = new_ticker.score
        # End queue processing loop

        # End Comment processing
        for key in tickers:
            if tickers[key] is not None:
                # Sort the tickers into a list of tuples (symbol, score)
                sorted_tickers = sorted(tickers[key].items(), key=lambda x:x[1], reverse=True)

                if len(sorted_tickers) != 0:
                    self.p(f'Queue reader processed {comments_processed} {key} comments from {self.sub_name}, got {len(sorted_tickers)} ticker result(s)')
                    data = (sorted_tickers, key, self.sub_name)
                    self.storage_queue.put(data)
        