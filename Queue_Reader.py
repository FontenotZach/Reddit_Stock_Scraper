import time
import os
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

from Util import *
from Storage_Manager import *
from Comment_Info import *

class Queue_Reader(Process_Wrapper):
    # ~30 Second wait period to let the queue fill up
    COOLDOWN_TIME = 60
    VARIANCE = 10
    PROCESS_TYPE_NAME = 'QREAD'

    # /////////////////////////////////////////////////////////////////
    #   Method:     __init__
    #   Purpose:    Initializes class variables
    #   Inputs:
    #       'comment_queue' - A queue holding comments to process
    #       'storage_queue' - A queue holding data to be written to disk
    #       'sub_name'      - The set of subreddits
    # /////////////////////////////////////////////////////////////////
    def __init__(self, comment_queue, storage_queue, sub_name):
        # Initialize class variables
        self.comment_queue = comment_queue
        self.storage_queue = storage_queue
        self.sub_name = sub_name


    # /////////////////////////////////////////////////////////////////
    #   Method:     reader_wrapper
    #   Purpose:    Manages stream_scraper_reader
    # /////////////////////////////////////////////////////////////////
    def reader_wrapper(self):
        self.PROCESS_ID = os.getpid()
        time.sleep(self.COOLDOWN_TIME)
        self.thread_print(f'Comment Queue reader started.')
        
        # Run the reader script on a set schedule
        while True:
            if not self.comment_queue.empty():
                reader = mp.Process(target=self.comment_queue_reader)
                reader.start()
                reader.join()
            self.random_sleep(self.COOLDOWN_TIME, self.VARIANCE)


    # /////////////////////////////////////////////////////////////////
    #   Method:     comment_queue_reader
    #   Purpose:    Collect live reddit comments and pass them to queue
    # /////////////////////////////////////////////////////////////////
    def comment_queue_reader(self):
        self.debug_print(f'{self.comment_queue.qsize()} {self.sub_name} comments collected.')
        comments_processed = 0  # total comments processed

        # Layout of tickers:
        # Dict
        # {
        #   key: 'hot' or 'stream' (str)
        #   value: Dict
        #       {
        #           key: Ticker symbol
        #           value: Ticker score
        #       }
        # }
        tickers = {'hot':{}, 'stream':{}}

        # Pops all comments each hour until queue is empty
        while not self.comment_queue.empty():
            # Checks if there is a comment to get
            # Comment Queue: Queue(Tuple(string, string, comment))
            r_comment = self.comment_queue.get(timeout=1)
            
            comments_processed += 1
            comment = Comment_Info(body=r_comment[1].body, score=r_comment[1].score, depth=-1)
            ticker_results = comment_score(comment)

            if ticker_results is not None:
                ticker_category = r_comment[0]

                # Pulls out metion data and comglomerates for each ticker
                for new_ticker in ticker_results:
                    symbol = new_ticker.symbol
                    if symbol in tickers[ticker_category]:
                        tickers[ticker_category][symbol] += new_ticker.score
                    else:
                        tickers[ticker_category][symbol] = new_ticker.score
        # End queue processing loop

        self.thread_print(f'Processed {comments_processed} comments.')
        num_results = 0

        # send comment data to the storage manager
        for category, ticker_dict in tickers.items():
            if ticker_dict:
                ticker_list = []
                for ticker_symbol, ticker_score in ticker_dict.items():
                    ticker_list.append(Ticker(symbol=ticker_symbol, score=ticker_score))

                data = (ticker_list, category, self.sub_name)
                self.storage_queue.put(data)
                num_results += 1

        self.thread_print(f'Put {num_results} ticker results onto the data queue.')