import threading
import traceback
import random
from operator import attrgetter
import time

from Util import *
from Storage_Manager import *

# 60 Second wait period to let the queue fill up
COOLDOWN_TIME = 60


def reader_wrapper(q, sub, l, storage_manager, timeout):
    pass


# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_reader
#   Purpose: Collect live reddit comments and pass them to queue
#   Inputs:
#           'q'                 - ref to comment queue
#           'sub'               - the Subreddit being scraped
#           'l'                 - Instance of the Log object
#           'storage_manager'   - Instance of the StorageManager object
#           print(f'SSR {thread_native_id}\t| ')
# /////////////////////////////////////////////////////////////////
def stream_scraper_reader(q, sub, l, storage_manager):
    sub_name = sub.display_name                 # name of sub to scrape
    thread_native_id = threading.get_native_id()  # id of thread

    print(f'SSR {thread_native_id}\t| Stream reader started on {sub_name}')

    # Hourly loop to read comments from queue
    while True:
        # Wait for between 5 and 10 seconds to begin processing
        n = (random.random() * 5.0) + 5.0
        print(f'SSR {thread_native_id}\t| Waiting {n:.2f} seconds before processing stream from {sub_name}')
        time.sleep(n)
        print(f'SSR {thread_native_id}\t| Begin processing stream from {sub_name}')

        comments_processed = 0  # total comments processed
        tickers = {}            #dictionary of tickers (key: symbol, value:score

        #print(f'SSR {thread_native_id}\t| {len(q)} {sub_name} comments collected')
        #print(f'SSR {thread_native_id}\t| queue: {q}')

        # Pops all comments each hour until queue is empty
        while True:
            # Checks if there is a comment to get
            if len(q) == 0:
                break

            r_comment = q.pop(0)
            #print(f'{r_comment}')

            # Get Comment score
            comments_processed += 1
            comment = Comment_Info(r_comment.body, -1, r_comment.score)
            ticker_result = comment_score(comment)
            #print(f'c:{comment}\nr:{result}')

            # Process Tickers scraped
            if ticker_result != None:
                # Pulls out metion data and comglomerates for each ticker
                for new_ticker in ticker_result:
                    symbol = new_ticker.symbol
                    if symbol in tickers:
                        tickers[symbol] = tickers[symbol] + new_ticker.score
                    else:
                        tickers[symbol] = new_ticker.score

        # End loop
        print(f'SSR {thread_native_id}\t| Queue reader loop ended {thread_native_id}.')

        # End Comment processing
        sorted_tickers = sorted(tickers.items(), key=lambda x:x[1], reverse=True)

        print(f'SSR {thread_native_id}\t| Processed {comments_processed} stream comments from {sub_name}')
        #print(f'SSR {thread_native_id}\t| Writing out stream results from {sub_name}')

        # Try writing data to file
        storage_manager.write_data(sorted_tickers, 'stream', sub_name)

        print(f'SSR {thread_native_id}\t| Waiting for {COOLDOWN_TIME} seconds.')
        time.sleep(COOLDOWN_TIME)

