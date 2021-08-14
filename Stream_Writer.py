import praw
from prawcore.exceptions import PrawcoreException
import threading
import datetime

# 5 second wait to let praw comment stream populate
COOLDOWN_TIME = 5

# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_writer
#   Purpose: Processes queue of streamed comments
#   Inputs:
#           'q'         - ref to comment queue
#           'stream'    - the praw comment stream
#           'sub'       - the Subreddit being scraped
#           'l'         - Instance of the Log object
# /////////////////////////////////////////////////////////////////
def stream_scraper_writer(q, stream, sub, l):

    sub_name = sub.display_name                     # name of sub to scrape
    thread_native_id = threading.get_native_id()    # id of thread
    comment_rate = 5                                # Number of comments to print a message for
    comment_number = 0                              # Number of comments processed
    print(f'SSW {thread_native_id}\t| {sub_name} stream writer started')

    # Constantly looks for new comments and writes to queue
    while True:
        try:
            for r_comment in stream:
                if r_comment is None:
                    time.sleep(COOLDOWN_TIME)
                else:
                    comment_number += 1
                    if (comment_number % comment_rate) == 0:
                        print(f'SSW {thread_native_id}\t| Comment {comment_number} in {sub_name} added to the queue')
                    q.append(r_comment)

        # If stream fails, get new stream
        except PrawcoreException as e:
            print(f'Praw core exception from writer thread {thread_native_id}: {e}')
            stream = get_stream(sub)
        except Exception as e:
            print(f'Exception from writer thread {thread_native_id}: {e}')
