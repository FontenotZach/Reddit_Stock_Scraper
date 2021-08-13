import _thread
import traceback
from operator import attrgetter

from Util import *
from Storage_Manager import *

# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_reader
#   Purpose: Collect live reddit comments and pass them to queue
#   Inputs:
#           'q'                 - ref to comment queue
#           'sub'               - the Subreddit being scraped
#           'l'                 - Instance of the Log object
#           'storage_manager'   - Instance of the StorageManager object
# /////////////////////////////////////////////////////////////////
def stream_scraper_reader(q, sub, l, storage_manager):

    # Fatal error catching block
    try:
        sub_name = sub.display_name                 # name of sub to scrape
        thread_native_id = _thread.get_native_id()  # id of thread
        # Catch issues with logging
        try:
            l.update_log(f'Stream scraper running on {sub_name}', 'SSR '+ str(thread_native_id))
        except Exception as e:
            print('error updating log')
        # Hourly loop to read comments from queue
        while True:
            try:
                print('SSR ', thread_native_id, '\t| ', end='')
                print(f'Reading comment stream from {sub_name}')

                comments_processed = 0  # total comments processed
                tickers = []            # list of tuples for tickers found in comments (symbol, score)

                print('SSR ', thread_native_id, '\t| ', end='')
                print(f'{len(q)} {sub_name} comments collected')

                # Pops all comments each hour until queue is empty
                while True:
                    # Checks if there is a comment to get
                    try:
                        r_comment = q.pop(0)
                    except Exception as e:
                        break

                    if r_comment is None:
                        break

                    # Get Comment score
                    comments_processed += 1
                    comment = Comment_Info(r_comment.body, -1, r_comment.score)
                    result = comment_score(comment)

                    # Process Tickers scraped
                    try:
                        if result != None:
                            # Pulls out metion data and comglomerates for each ticker
                            for new_ticker in result:
                                new = True
                                for ticker in tickers:
                                    if new_ticker.is_same_symbol(ticker):
                                        new = False
                                        ticker.score = ticker.score + new_ticker.score
                                        break
                                if new:
                                    tickers.append(new_ticker)
                    except Exception as e:
                        l.update_log(f'Error in processing comments from {sub_name}: {e}', 'SSR '+ str(thread_native_id))

                # End Comment processing

                tickers.sort(key = attrgetter('score'), reverse = True)
                print('SSR ', thread_native_id, '\t| ', end='')
                print(f'Processed {comments_processed} stream comments from {sub_name}')
                print('SSR ', thread_native_id, '\t| ', end='')
                print(f'Writing out stream results from {sub_name}')

                l.update_log(f'{comments_processed} stream comments scraped from {sub_name}', 'SSR '+ str(thread_native_id))

                # Try writing data to file
                storage_manager.write_data(tickers, 'stream', sub_name)

                print('SSR ', thread_native_id, '\t| ', end='')
                print('Waiting...')
                wait_for_next_hour()
            except Exception as e:
                l.update_log(f'Unexpected error while scraping {sub_name}: {e}', 'SSR '+ str(thread_native_id))
        # End hourly loop
    except Exception as e:
        l.update_log(f'Unexpected fatal error while scraping {sub_name}: {e}', 'SSR '+ str(thread_native_id))

