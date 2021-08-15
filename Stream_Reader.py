import datetime
import random
import time
import os
import multiprocessing as mp

from Util import *
from Storage_Manager import *
from Comment_Info import *

class Stream_Reader:
    # 60 Second wait period to let the queue fill up
    COOLDOWN_TIME = 50
    process_id = 0
    sub_name = ''
    comment_queue = 0
    storage_queue = 0

    debug = True

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
        if self.debug:
            print(f'SSR {self.process_id}\t| {s}')

    # /////////////////////////////////////////////////////////////////
    #   Method:     reader_wrapper
    #   Purpose:    Manages stream_scraper_reader
    # /////////////////////////////////////////////////////////////////
    def reader_wrapper(self):
        self.process_id = os.getpid()
        print(f'SSR {self.process_id}\t| Stream reader started on {self.sub_name}')
        
        # Run the reader script on a set schedule
        while True:
            #start_time = datetime.datetime.now()
            reader = mp.Process(target=self.stream_scraper_reader)
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
    #   Method:     stream_scraper_reader
    #   Purpose:    Collect live reddit comments and pass them to queue
    # /////////////////////////////////////////////////////////////////
    def stream_scraper_reader(self):
        
        # Wait for between 5 and 10 seconds to begin processing
        #n = (random.random() * 5.0) + 5.0
        #print(f'SSR {self.process_id}\t| Waiting {n:.2f} seconds before processing stream from {self.sub_name}')
        #time.sleep(n)
        
        self.p(f'Begin processing stream from {self.sub_name}')

        comments_processed = 0  # total comments processed
        tickers = {}            #dictionary of tickers (key: symbol, value: score)
        self.p(f'{self.sub_name} {self.comment_queue.qsize()} comments collected')
        #print(f'SSR {thread_native_id}\t| queue: {q}')
        # Pops all comments each hour until queue is empty
        while not self.comment_queue.empty():
            # Checks if there is a comment to get
            r_comment = self.comment_queue.get()

            comments_processed += 1
            comment = Comment_Info(r_comment.body, -1, r_comment.score)
            ticker_result = comment_score(comment)

            if ticker_result is not None:
                # Pulls out metion data and comglomerates for each ticker
                for new_ticker in ticker_result:
                    symbol = new_ticker.symbol
                    if symbol in tickers:
                        tickers[symbol] = tickers[symbol] + new_ticker.score
                    else:
                        tickers[symbol] = new_ticker.score
        # End queue processing loop

        

        # End Comment processing
        # Sort the tickers into a list of tuples (symbol, score)
        sorted_tickers = sorted(tickers.items(), key=lambda x:x[1], reverse=True)
        self.p(f'Queue reader processed {comments_processed} comments from {self.sub_name}, got {len(sorted_tickers)} results')
        
        # Try writing data to file
        if len(sorted_tickers) != 0:
            data = (sorted_tickers, 'stream', self.sub_name)
            self.storage_queue.put(data)
        