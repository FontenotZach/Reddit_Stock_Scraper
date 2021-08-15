import praw     # reddit API
from prawcore.exceptions import PrawcoreException
import multiprocessing as mp

import threading
import time
import datetime
import signal

from Util import *
from Log import *
from QueueMessage import *
from Storage_Manager import *

from Init import initialize
from Stream_Writer import stream_scraper_writer
from Stream_Reader import stream_scraper_reader
from Scrape_Hot_Posts import scrape_hot_posts

POSTS_PER_BATCH = 30


# /////////////////////////////////////////////////////////////////
#   Method: queue_report
#   Purpose: Collect live reddit comments and pass them to queue
#   Inputs:
#           'q' - ref to comment queue
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def queue_report(q, sub):
    # sleeps for a minute then reports # of comments in queue
    while True:
        time.sleep(60)
        print('SSW ', os.getpid()(), '\t| ', end='')
        print(f'{len(q)} {sub} comments currently in stream queue')


# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles SIGINT (^C)
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  y/N')
    response = input()
    if response == 'Y' or response == 'y':
        exit(0)
    print('Abort cancelled. Continuing..')
    idle()


# /////////////////////////////////////////////////////////////////
#   Method: idle
#   Purpose: Parent thread waiting and periodically error checking
# /////////////////////////////////////////////////////////////////
def idle():
    print('MAIN: Idle')
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(10)
        # check parent queue messages


# /////////////////////////////////////////////////////////////////
#   Method: get_stream
#   Purpose: Returns instance of Subreddit stream
#   Inputs:
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def get_stream(sub):
    return sub.stream.comments(skip_existing=True)


# /////////////////////////////////////////////////////////////////
#   Method: __main__
#   Purpose: Starting point
# /////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    # Run initialization TODO: Merge more into this
    initialize()
    mp.set_start_method('spawn')

    # Start log
    logger = Log()
    # Start storage manager
    storage_queue = mp.Queue() 
    storage_manager = StorageManager()

    # Setup Reddit instance
    # TODO: Look into PRAW multithread support
    reddit = praw.Reddit("stockscraper")

    # List of subreddit names
    subreddits = [ 'wallstreetbets', 'investing', 'stocks', 'pennystocks' ]

    # These are formed into a list of Tuples with the form (subreddit_name, subreddit_instance, stream_instance, stream_queue)
    subreddit_list = []

    for sub in subreddits:
        tmp = reddit.subreddit(sub)
        empty_queue = mp.Queue()
        sub_tuple = (sub, tmp, get_stream(tmp), empty_queue)
        subreddit_list.append(sub_tuple)

    # Starting processes for stream_scraper_writer, scrape_hot_posts, and stream_scraper_reader
    # Each new sub needs one thread for each method
    for sub in subreddit_list:
        print(f'MAIN: Starting processes for {sub[0]}')

        writer =  mp.Process(target=stream_scraper_writer, args=(sub[3], sub[2], sub[1], logger))
        reader =  mp.Process(target=stream_scraper_reader, args=(sub[3], sub[1], logger, storage_manager))
        scraper = mp.Process(target=scrape_hot_posts, args=(POSTS_PER_BATCH, sub[1], logger, storage_manager))

        reader.start()
        writer.start()
        scraper.start()

    # allow parent thread to idle
    idle()

######################################################################################
