import praw
from Util import *
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
from prawcore.exceptions import PrawcoreException

reddit = praw.Reddit(
     client_id="KmWrNZao9rWwSA",
     client_secret="V5mH25xahLgeUakjH6Y_xRxQ3fmKSA",
     user_agent="My Reddit Scraper 1.0 by fontenotza"
 )



def stream_scraper_reader(q, sub):

    while True:
        print('SSR ', _thread.get_native_id(), '\t| ', end='')
        print('Reading comment stream from ' + sub.display_name)
        comments_processed = 0
        tickers = []

        print('SSR ', _thread.get_native_id(), '\t| ', end='')
        print(str(len(q)) + ' '+  sub.display_name + ' comments collected')

        while True:

            try:
                r_comment = q.pop(0)
            except:
                break

            if r_comment is None:
                break

            comments_processed += 1
            comment = Comment_Info(r_comment.body, -1, r_comment.score)
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

        tickers.sort(key = attrgetter('score'), reverse = True)
        print('SSR ', _thread.get_native_id(), '\t| ', end='')
        print('Processed ' + str(comments_processed) + ' stream comments from ' + sub.display_name)
        print('SSR ', _thread.get_native_id(), '\t| ', end='')
        print('Writing out stream results from ' + sub.display_name )

        storage_manager(tickers, 'stream', sub)
        print('SSR ', _thread.get_native_id(), '\t| ', end='')
        print('Waiting...')
        wait_for_next_hour()


def scrape_hot_posts(num, sub):

    while True:
        hot_posts = []
        print('SH ', _thread.get_native_id(), '\t| ', end='')
        print('Compiling Hottest ' + str(num) + ' ' + sub.display_name + ' posts')
        for submission in sub.hot(limit=num):
            hot_posts.append(submission)

        tickers = []
        comments_processed = 0

        for submission in hot_posts:
            comments = get_post_comments(submission)  # returns tuples (body, depth, score)
            print('SH ', _thread.get_native_id(), '\t| ', end='')
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

        tickers.sort(key = attrgetter('score'), reverse = True)
        print('SH ', _thread.get_native_id(), '\t| ', end='')
        print('Processed ' + str(comments_processed) + ' hot comments from ' + sub.display_name)
        print('SH ', _thread.get_native_id(), '\t| ', end='')
        print('Writing out hot results from ' + sub.display_name)
        storage_manager(tickers, 'hot', sub)

        print('SH ', _thread.get_native_id(), '\t| ', end='')
        print('Waiting...')
        wait_for_next_hour()

def storage_manager(tickers, set, sub):

    for ticker in tickers:
        file_name = 'Data\\' + set + '\\' + sub.display_name + '\\' + ticker.symbol + '_data_' + set + '.csv'
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

        write_to_excel(tickers, set, sub.display_name)
        write_to_csv(tickers, set, sub.display_name)


def stream_scraper_writer(q, stream, sub):

    t_report = _thread.start_new_thread(queue_report, (q, sub.display_name,))
    print('SSW ', _thread.get_native_id(), '\t| ', end='')
    print(sub.display_name + ' stream up and running')
    while True:
        try:
            for r_comment in stream:
                if r_comment is None:
                    time.sleep(3)
                else:
                    q.append(r_comment)
        except PrawcoreException:
            stream = get_stream(sub)


def queue_report(q, sub):

    while True:
        time.sleep(60)
        print('SSW ', _thread.get_native_id(), '\t| ', end='')
        print(str(len(q)) + ' ' + sub + ' comments currently in stream queue')



def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  Y/N')
    response = input()
    if response == 'Y':
        sys.exit(0)
    print('Abort aborted')
    idle()

def idle():
    print('Parent: Idle')
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(100)
        #check for errors

def get_stream(sub):
    return sub.stream.comments(skip_existing=True)

if __name__ == '__main__':

    wsb = reddit.subreddit('wallstreetbets')
    inv = reddit.subreddit('investing')

    wsb_stream = get_stream(wsb)
    inv_stream = get_stream(inv)

    wsb_comment_queue = []
    inv_comment_queue = []

    print('Starting threads')

    t1 = _thread.start_new_thread(stream_scraper_writer, (wsb_comment_queue, wsb_stream, wsb,))
    t2 = _thread.start_new_thread(stream_scraper_writer, (inv_comment_queue, inv_stream, inv,))

    t3 = _thread.start_new_thread(scrape_hot_posts, (30, wsb,))
    t4 = _thread.start_new_thread(scrape_hot_posts, (30, inv,))

    t5 = _thread.start_new_thread(stream_scraper_reader, (wsb_comment_queue, wsb,))
    t6 = _thread.start_new_thread(stream_scraper_reader, (inv_comment_queue, inv,))


    idle()



######################################################################################
