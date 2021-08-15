import time
import signal
import multiprocessing as mp

from Util import *
from Log import *
from QueueMessage import *
from Storage_Manager import *
from Stream_Writer import *
from Stream_Reader import *
from Scrape_Hot_Posts import *

from Init import initialize

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
        print(f'{q.qsize()} {sub} comments currently in stream queue')


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
    storage_manager = StorageManager(storage_queue)
    sm = mp.Process(target=storage_manager.process_queue)
    sm.start()

    # Setup Reddit instance
    # TODO: Look into PRAW multithread support
    #reddit = praw.Reddit("stockscraper")

    # List of subreddit names
    subreddits = [ 'wallstreetbets', 'investing', 'stocks', 'pennystocks' ]

    # These are formed into a list of Tuples with the form (subreddit_name, subreddit_instance, stream_instance, stream_queue)
    subreddit_list = []

    for sub_name in subreddits:
        #sub = reddit.subreddit(sub_name)
        empty_queue = mp.Queue()
        #sub_tuple = (sub_name, sub, sub.stream.comments(skip_existing=True), empty_queue)
        sub_tuple = (sub_name, empty_queue)
        subreddit_list.append(sub_tuple)

    # Starting processes for stream_scraper_writer, scrape_hot_posts, and stream_scraper_reader
    # Each new sub needs one thread for each method
    for sub in subreddit_list:
        print(f'MAIN: Starting processes for {sub[0]}')

        # Create the wrapper objects for each thread
        reader_manager = Stream_Reader(sub[1], sub[0], storage_queue)
        writer_manager = Stream_Writer(sub[1], sub[0])
        hot_scraper_manager = Scrape_Hot_Posts(sub[0], storage_queue)

        writer =  mp.Process(target=writer_manager.writer_wrapper)
        reader =  mp.Process(target=reader_manager.reader_wrapper)
        scraper = mp.Process(target=hot_scraper_manager.hot_wrapper)

        writer.start()
        reader.start()
        scraper.start()

    # allow parent thread to idle
    idle()

######################################################################################
