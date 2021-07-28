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

# Start log
l = Log()
l.start_log()

# setup Reddit instance
reddit = praw.Reddit(
     client_id="KmWrNZao9rWwSA",
     client_secret="V5mH25xahLgeUakjH6Y_xRxQ3fmKSA",
     user_agent="My Reddit Scraper 1.0 by fontenotza"
)

parent_q = []

# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_reader
#   Purpose: Collect live reddit comments and pass them to queue
#   Inputs:
#           'q' - ref to comment queue
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def stream_scraper_reader(q, sub, parent_q):

    try:
        sub_name = sub.display_name
        thread_native_id = _thread.get_native_id()
        try:
            l.update_log('Stream scraper running on ' + sub_name, 'SSR '+ str(thread_native_id))
        except Exception as e:
            print('error updating log')
        while True:
            try:
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Reading comment stream from ' + sub_name)

                comments_processed = 0  # total comments processed
                tickers = []            # list of tuples for tickers found in comments (symbol, score)

                print('SSR ', thread_native_id, '\t| ', end='')
                print(str(len(q)) + ' '+  sub_name + ' comments collected')

                while True:
                    try:
                        r_comment = q.pop(0)
                    except Exception as e:
                        break

                    if r_comment is None:
                        break

                    comments_processed += 1
                    comment = Comment_Info(r_comment.body, -1, r_comment.score)
                    result = comment_score(comment)

                    try:
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
                        l.update_log('Error in processing comments from ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))


                tickers.sort(key = attrgetter('score'), reverse = True)
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Processed ' + str(comments_processed) + ' stream comments from ' + sub_name)
                print('SSR ', thread_native_id, '\t| ', end='')
                print('Writing out stream results from ' + sub_name )

                l.update_log(str(comments_processed) + ' stream comments scraped from ' + sub_name, 'SSR '+ str(thread_native_id))

                try:
                    storage_manager(tickers, 'stream', sub_name)
                except Exception as e:
                    l.update_log('Error storing tickers from ' + sub_name + ' to file: ' + str(e), 'SSR '+ str(thread_native_id))

                print('SSR ', thread_native_id, '\t| ', end='')
                print('Waiting...')
                wait_for_next_hour()
            except Exception as e:
                l.update_log('Unexpected error while scraping ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))
    except Exception as e:
        l.update_log('Unexpected fatal error while scraping ' + sub_name + " :" + str(e), 'SSR '+ str(thread_native_id))



    # /////////////////////////////////////////////////////////////////
    #   Method: scrape_hot_posts
    #   Purpose: Collects comments from hottest Subreddit posts
    #   Inputs:
    #           'num' - the number of posts to scrape
    #           'sub' - the Subreddit being scraped
    # /////////////////////////////////////////////////////////////////
def scrape_hot_posts(num, sub, parent_q):

    try:
        sub_name = sub.display_name
        thread_native_id = _thread.get_native_id()
        try:
            l.update_log('Hot post scraper running on ' + sub_name, 'SH ' + str(thread_native_id))
        except Exception as e:
            print('error updating log')

        while True:
            try:
                hot_posts = []
                print('SH ', thread_native_id, '\t| ', end='')
                print('Compiling Hottest ' + str(num) + ' ' + sub_name + ' posts')

                start_hour = int(get_index())   # the current hour at start

                posts_retr = False
                retries = 0
                max_retries = 10
                timeout = False
                while not posts_retr and not timeout:
                    try:
                        for submission in sub.hot(limit=num):
                            hot_posts.append(submission)
                        if len(hot_posts) > 0:
                            posts_retr = True
                    except Exception as e:
                        l.update_log('Could not retrieve hot posts from ' + sub_name + ": " + str(e), 'SH ' + str(thread_native_id))
                    if not posts_retr:
                        retries += 1
                        sleep(5)
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

                try:
                    storage_manager(tickers, 'hot', sub_name)
                except Exception as e:
                    l.update_log('Error storing tickers from ' + sub_name + ' to file:' + str(e), 'SH '+ str(thread_native_id))


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

    for ticker in tickers:
        file_name = 'Data/' + set + '/' + sub_name + '/' + ticker.symbol + '_data_' + set + '.csv'
        file_path = pathlib.Path(file_name)
        if file_path.exists():
            file = open(file_name, 'r')
        else:
            file = open(file_name, 'x')
            file.close()
            file = open(file_name, 'r')

        reader = csv.reader(file)
        values = list(reader)
        index = int(get_index())

        current_length = len(values)

        while len(values) <= index:
            values.append(0)

        values[index] =  ticker.score
        new_values = values[current_length:]
        file.close()
        file = open(file_name, 'a')
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(map(lambda x: [x], new_values))

        file.close()

        #write_to_excel(tickers, set, sub_name)
        write_to_csv(tickers, set, sub_name)


# /////////////////////////////////////////////////////////////////
#   Method: stream_scraper_writer
#   Purpose: Processes queue of streamed comments
#   Inputs:
#           'q' - ref to comment queue
#           'stream' - the praw comment stream
#           'sub' - the Subreddit being scraped
# /////////////////////////////////////////////////////////////////
def stream_scraper_writer(q, stream, sub, parent_q):

    sub_name = sub.display_name
    thread_native_id = _thread.get_native_id()
    t_report = _thread.start_new_thread(queue_report, (q, sub_name,))
    print('SSW ', thread_native_id, '\t| ', end='')
    print(sub_name + ' stream up and running')
    while True:
        try:
            for r_comment in stream:
                if r_comment is None:
                    time.sleep(3)
                else:
                    q.append(r_comment)
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

    while True:
        time.sleep(60)
        print('SSW ', _thread.get_native_id(), '\t| ', end='')
        print(str(len(q)) + ' ' + sub + ' comments currently in stream queue')

# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles escapes
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  Y/N')
    response = input()
    if response == 'Y':
        sys.exit(0)
    print('Abort aborted')
    idle(parent_q)

# /////////////////////////////////////////////////////////////////
#   Method: idle
#   Purpose: Parent thread waiting and periodically error checking
# /////////////////////////////////////////////////////////////////
def idle(parent_q):
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



    wsb = reddit.subreddit('wallstreetbets')
    inv = reddit.subreddit('investing')
    sto = reddit.subreddit('stocks')
    pen = reddit.subreddit('pennystocks')

    wsb_stream = get_stream(wsb)
    inv_stream = get_stream(inv)
    sto_stream = get_stream(sto)
    pen_stream = get_stream(pen)

    wsb_comment_queue = []
    inv_comment_queue = []
    sto_comment_queue = []
    pen_comment_queue = []


    print('Starting threads')

    t1 = _thread.start_new_thread(stream_scraper_writer, (wsb_comment_queue, wsb_stream, wsb, parent_q,))
    t2 = _thread.start_new_thread(stream_scraper_writer, (inv_comment_queue, inv_stream, inv, parent_q,))
    t3 = _thread.start_new_thread(stream_scraper_writer, (sto_comment_queue, sto_stream, sto, parent_q,))
    t4 = _thread.start_new_thread(stream_scraper_writer, (pen_comment_queue, pen_stream, pen, parent_q,))

    t5 = _thread.start_new_thread(scrape_hot_posts, (30, wsb, parent_q,))
    t6 = _thread.start_new_thread(scrape_hot_posts, (30, inv, parent_q,))
    t7 = _thread.start_new_thread(scrape_hot_posts, (30, sto, parent_q,))
    t8 = _thread.start_new_thread(scrape_hot_posts, (30, pen, parent_q,))

    t9 = _thread.start_new_thread(stream_scraper_reader, (wsb_comment_queue, wsb, parent_q,))
    t0 = _thread.start_new_thread(stream_scraper_reader, (inv_comment_queue, inv, parent_q,))
    tA = _thread.start_new_thread(stream_scraper_reader, (sto_comment_queue, sto, parent_q,))
    tB = _thread.start_new_thread(stream_scraper_reader, (pen_comment_queue, pen, parent_q,))


    idle(parent_q)



######################################################################################
