import praw     # reddit API
from prawcore.exceptions import PrawcoreException

from operator import attrgetter
import time
import multiprocessing
from tkinter import *
from tkinter.ttk import *
import datetime
import platform
import os.path
from os import path
import csv
import pathlib
import _thread
import signal
import sys
from threading import Thread, Lock
import traceback

# Local files
from Stream_Reader import stream_scraper_reader
from Stream_Writer import stream_scraper_writer
from Scraper import scrape_hot_posts
from Util import *
from Log import *
from QueueMessage import *

## Thread Label Key ##
#   SSR: Stream Reader thread
#   SSW: Stream Writer thread
#   SH: Hot Post thread

# Data file layout:
#   /Data
#       /hot
#           /{sub1}
#               AAPL_hot_{sub1}.csv
#               GME_hot_{sub1}.csv
#               ...
#           /{sub2}
#               AAPL_hot_{sub2}.csv
#               GME_hot_{sub2}.csv
#               ...
#            ...
#       /stream
#           /{sub1}
#               AAPL_stream_{sub1}.csv
#               GME_stream_{sub1}.csv
#               ...
#           /{sub2}
#               AAPL_stream_{sub2}.csv
#               GME_stream_{sub2}.csv
#               ...
#           ...

# /////////////////////////////////////////////////////////////////
#   Method: queue_report
#   Purpose: Reports on the status of a comment queue
#   Inputs:
#           'q'     - ref to comment queue
#           'sub'   - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def queue_report(q, sub):

    # sleeps for a minute then reports # of comments in queue
    while True:
        time.sleep(60)
        print('SSW ', _thread.get_native_id(), '\t| ', end='')
        print(f'{len(q)} {sub} comments currently in stream queue')

# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles SIGINT (^C)
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected. Do you wish to quit? [y/N]')
    response = input()
    if response == 'Y' or response == 'y':
        sys.exit(0)
    print('Abort cancelled. Continuing.')
    idle()

# /////////////////////////////////////////////////////////////////
#   Method: idle
#   Purpose: Parent thread waiting and periodically error checking
# /////////////////////////////////////////////////////////////////
def idle():
    print('Parent: Idle')
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
    mutex_lock = Lock()

    # Start log
    l = Log()
    l.start_log()

    # Setup Reddit instance
    # TODO: Look into PRAW multithread support
    reddit = praw.Reddit(
         client_id="KmWrNZao9rWwSA",
         client_secret="V5mH25xahLgeUakjH6Y_xRxQ3fmKSA",
         user_agent="My Reddit Scraper 1.0 by fontenotza"
    )

    # List of subreddit names
    subreddits = [ 'wallstreetbets', 'investing', 'stocks', 'pennystocks' ]

    # These are formed into a list of Tuples with the form (subreddit_name, subreddit_instance, stream_instance, stream_queue)
    subreddit_list = []

    for sub in subreddits:
        tmp = reddit.subreddit(sub)
        empty_list = []
        sub_tuple = (sub, tmp, get_stream(tmp), empty_list)
        subreddit_list.append(sub_tuple)

    # Starting threads for stream_scraper_writer, scrape_hot_posts, and stream_scraper_reader
    # Each new sub needs one thread for each method
    for sub in subreddit_list:
        print(f'Starting threads for {sub[0]}')
        writer = _thread.start_new_thread(stream_scraper_writer, (sub[3], sub[2], sub[1], l))
        scraper = _thread.start_new_thread(scrape_hot_posts, (30, sub[1], l))
        reader = _thread.start_new_thread(stream_scraper_reader, (sub[3], sub[1], mutex_lock, l))
        report = _thread.start_new_thread(queue_report, (sub[3], sub[0]))

    # allow parent thread to idle
    idle()

######################################################################################
