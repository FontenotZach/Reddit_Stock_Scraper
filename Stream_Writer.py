import praw
from prawcore.exceptions import PrawcoreException
import _thread
import datetime

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

    sub_name = sub.display_name                 # name of sub to scrape
    thread_native_id = _thread.get_native_id()  # id of thread
    print('SSW ', thread_native_id, '\t| ', end='')
    print(f'{sub_name} stream up and running')
    l.update_log(f'Started stream writer for {sub_name}', f'SSW {thread_native_id}')

    # Constantly looks for new comments and writes to queue
    while True:
        try:
            for r_comment in stream:
                if r_comment is None:
                    time.sleep(3)
                else:
                    q.append(r_comment)
        # If stream fails, get new stream
        except PrawcoreException as e:
            l.update_log(f'Unexpected fatal error while reading stream from {sub_name} :{e}', f'SSW {thread_native_id}')
            stream = get_stream(sub)
        except Exception as e:
            l.update_log(f'Unexpected fatal error while reading stream from {sub_name} :{e}', f'SSW {thread_native_id}')
