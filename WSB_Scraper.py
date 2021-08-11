import praw     # reddit API
from prawcore.exceptions import PrawcoreException

from Util import *
from Log import *
from QueueMessage import *

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

# Parent queue for message passing (not implemented)
#parent_q = []
mutex_lock = Lock()


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
#   Method: stream_scraper_reader
#   Purpose: Collect live reddit comments and pass them to queue
#   Inputs:
#           'q' - ref to comment queue
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def stream_scraper_reader(q, sub):

    # Fatal error catching block
    try:
        sub_name = sub.display_name                 # bane of sub to scrape
        thread_native_id = _thread.get_native_id()  # id of thread
        # Catch issues with logging
        try:
            l.update_log('Stream scraper running on ' + sub_name, 'SSR '+ str(thread_native_id))
        except Exception as e:
            print('error updating log')
        # Hourly loop to read comments from queue
        while True:
            try:
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Reading comment stream from ' + sub_name)

                comments_processed = 0  # total comments processed
                tickers = []            # list of tuples for tickers found in comments (symbol, score)

                print('SSR ', thread_native_id, '\t| ', end='')
                print(str(len(q)) + ' '+  sub_name + ' comments collected')

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
                        l.update_log('Error in processing comments from ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))

                # End Comment processing

                tickers.sort(key = attrgetter('score'), reverse = True)
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Processed ' + str(comments_processed) + ' stream comments from ' + sub_name)
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Writing out stream results from ' + sub_name )

                l.update_log(str(comments_processed) + ' stream comments scraped from ' + sub_name, 'SSR '+ str(thread_native_id))

                # Try writing data to file
                try:
                    storage_manager(tickers, 'stream', sub_name)
                    mutex_lock.release()
                except Exception as e:
                    mutex_lock.release()
                    l.update_log('Error storing tickers from ' + sub_name + ' to file: ' + str(e), 'SSR '+ str(thread_native_id))
                    l.update_log('Stack trace: ' + traceback.format_exc(), 'SSR '+ str(thread_native_id))

                print('SSR ', thread_native_id, '\t| ', end='')
                print('Waiting...')
                wait_for_next_hour()
            except Exception as e:
                l.update_log('Unexpected error while scraping ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))
        # End hourly loop
    except Exception as e:
        l.update_log('Unexpected fatal error while scraping ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))



    # /////////////////////////////////////////////////////////////////
    #   Method: scrape_hot_posts
    #   Purpose: Collects comments from hottest Subreddit posts
    #   Inputs:
    #           'num' - the number of posts to scrape
    #           'sub' - the Subreddit being scraped
    # /////////////////////////////////////////////////////////////////
def scrape_hot_posts(num, sub):
    # Fatal error catching block
    try:
        sub_name = sub.display_name                 # bane of sub to scrape
        thread_native_id = _thread.get_native_id()  # id of thread
        # Catch issues with logging
        try:
            l.update_log('Hot post scraper running on ' + sub_name, 'SH ' + str(thread_native_id))
        except Exception as e:
            print('error updating log')
        # Hourly loop to obtain hot posts
        while True:
            # Inner loop try block ensures PRAW interrutions are handled
            try:
                hot_posts = []  # list of hot posts for {sub_name}
                print('SH ', thread_native_id, '\t| ', end='')
                print('Compiling Hottest ' + str(num) + ' ' + sub_name + ' posts')

                start_hour = int(get_index())   # the current hour at start

                # This block tries obtaining hot posts until PRAW responds correctly or timeout is reached
                posts_retr = False  # have the posts been retrieved?
                retries = 0         # number of attempts made this hour
                max_retries = 10    # max attempts per hour
                timeout = False     # has max attempts been reached?
                while not posts_retr and not timeout:
                    # try to obtain posts
                    try:
                        for submission in sub.hot(limit=num):
                            hot_posts.append(submission)
                        # check if posts have been collected
                        if len(hot_posts) > 0:
                            posts_retr = True
                    except Exception as e:
                        l.update_log('Could not retrieve hot posts from ' + sub_name + ": " + str(e), 'SH ' + str(thread_native_id))
                    if not posts_retr:
                        retries += 1
                        time.sleep(30)
                    if retries >= max_retries:
                        timeout = True

                comments_processed = 0  # total comments processed
                tickers = []            # list of tuples for tickers found in comments (symbol, score)

                try:
                    for submission in hot_posts:

                        # If more than 45 minutes have passed (75% of hour), stop processing more posts
                        # Won't eat into next hour's counting time
                        if get_index() - start_hour > 0.75:
                            break
                        comments = get_post_comments(submission)  # returns tuples (body, depth, score)
                        print('SH ', thread_native_id, '\t| ', end='')
                        print('Scraping post -> ' + submission.title)

                        # Pulls out metion data and comglomerates for each ticker
                        for comment in comments:
                            comments_processed += 1
                            result = comment_score(comment)
                            if result != None:
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
                    l.update_log('Error in processing hot posts from ' + sub_name + " :" + str(e), 'SH '+ str(thread_native_id))


                tickers.sort(key = attrgetter('score'), reverse = True)
                print('SH ', thread_native_id, '\t| ', end='')
                print('Processed ' + str(comments_processed) + ' hot comments from ' + sub_name)
                print('SH ', thread_native_id, '\t| ', end='')
                print('Writing out hot results from ' + sub_name)

                l.update_log(str(comments_processed) + ' hot comments scraped from ' + sub_name, 'SH '+ str(thread_native_id))

                # Try writing data to file
                try:
                    storage_manager(tickers, 'hot', sub_name)
                    mutex_lock.release()
                except Exception as e:
                    mutex_lock.release()
                    l.update_log('Error storing tickers from ' + sub_name + ' to file:' + str(e), 'SH '+ str(thread_native_id))
                    l.update_log('Stack trace: ' + traceback.format_exc(), 'SH '+ str(thread_native_id))


                print('SH ', thread_native_id, '\t| ', end='')
                print('Waiting...')
                # TODO: Pass queue message to parent.  If message isn't present at beginning of next hour, kill thread and start over
                wait_for_next_hour()
            except Exception as e:
                l.update_log('Unexpected error while scraping ' + sub_name + " :" + str(e), 'SH '+ str(thread_native_id))

    except Exception as e:
        l.update_log('Unexpected fatal error while scraping ' + sub_name + " :" + str(e), 'SH '+ str(thread_native_id))


# /////////////////////////////////////////////////////////////////
#   Method: storage_manager
#   Purpose: Manages file output
#   Inputs:
#           'tickers' - list of scraped tickers
#           'set' - the set the comments belong to
#               > TODO: convert to enum
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def storage_manager(tickers, set, sub_name):

    # Write each ticker score to appropriate SymbolDirectory

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

    # process each ticker

    mutex_lock.acquire()
    for ticker in tickers:
        file_name = 'Data/' + set + '/' + ticker.symbol + '_data_' + set + '.csv'
        file_path = pathlib.Path(file_name)
        if file_path.exists():
            file = open(file_name, 'r')
        else:
            file = open(file_name, 'x')
            file.close()
            file = open(file_name, 'r')

        try:
            reader = csv.reader(file)
            values = list(reader)
            updated_values = []
            for value in values:
                updated_values.append(value[0])
            index = int(get_index())


            current_length = len(values)

            while len(updated_values) <= index:
                updated_values.append(0)

            updated_values[index] = float(updated_values[index]) + ticker.score
            #new_values = values[current_length:]
            file.close()
            file = open(file_name, 'w')
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(map(lambda x: [x], updated_values))

            file.close()

                #write_to_excel(tickers, set, sub_name)
            write_to_csv(tickers, set, sub_name)
        except:
            print(updated_values)
            raise Exception('Error in file I/O')


# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_writer
#   Purpose: Processes queue of streamed comments
#   Inputs:
#           'q' - ref to comment queue
#           'stream' - the praw comment stream
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def stream_scraper_writer(q, stream, sub):

    sub_name = sub.display_name                 # bane of sub to scrape
    thread_native_id = _thread.get_native_id()  # id of thread
    t_report = _thread.start_new_thread(queue_report, (q, sub_name,))   # Start thread to track queue
    print('SSW ', thread_native_id, '\t| ', end='')
    print(sub_name + ' stream up and running')

    # Constantly looks for new comments and writes to queue
    while True:
        try:
            for r_comment in stream:
                if r_comment is None:
                    time.sleep(3)
                else:
                    q.append(r_comment)
        # If stream fails, get new stream
        except PrawcoreException:
            stream = get_stream(sub)
        except Exception as e:
            l.update_log('Unexpected fatal error while reading stream from ' + sub_name + " :" + str(e), 'SSW '+ str(thread_native_id))

# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_reader
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
        print(str(len(q)) + ' ' + sub + ' comments currently in stream queue')

# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles SIGINT (^C)
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  Y/N')
    response = input()
    if response == 'Y':
        sys.exit(0)
    print('Abort aborted')
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
        writer = _thread.start_new_thread(stream_scraper_writer, (sub[3], sub[2], sub[1]))
        scraper = _thread.start_new_thread(scrape_hot_posts, (30, sub[1]))
        reader = _thread.start_new_thread(stream_scraper_reader, (sub[3], sub[1]))

    # allow parent thread to idle
    idle()

######################################################################################
