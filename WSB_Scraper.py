import praw     # reddit API
from prawcore.exceptions import PrawcoreException

from tkinter import *
from tkinter.ttk import *
from operator import attrgetter
from os import path
from threading import Thread, Lock
import time
import multiprocessing
import datetime
import platform
import csv
import pathlib
import _thread
import signal
import sys
import traceback

from Util import *
from Log import *
from QueueMessage import *
from Storage_Manager import *
from Init import initialize
from Stream_Writer import stream_scraper_writer
from Stream_Reader import stream_scraper_reader
from Scrape_Hot_Posts import scrape_hot_posts

# Parent queue for message passing (not implemented)
#parent_q = []
mutex_lock = Lock()


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
        print('SSW ', _thread.get_native_id(), '\t| ', end='')
        print(f'{len(q)} {sub} comments currently in stream queue')


# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles SIGINT (^C)
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  y/N')
    response = input()
    if response == 'Y' or response == 'y':
        sys.exit(0)
    print('Abort cancelled. Continuing..')
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
    # Run initialization TODO: Merge more into this
    initialize()

    # Start log
    logger = Log()

    # Start storage manager
    storage_manager = StorageManager()

    # Setup Reddit instance
    # TODO: Look into PRAW multithread support
    # TODO: Remove these from the public github repo
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
        writer = _thread.start_new_thread(stream_scraper_writer, (sub[3], sub[2], sub[1], logger))
        scraper = _thread.start_new_thread(scrape_hot_posts, (30, sub[1], logger, storage_manager))
        reader = _thread.start_new_thread(stream_scraper_reader, (sub[3], sub[1], logger, storage_manager))

    # allow parent thread to idle
    idle()

######################################################################################
