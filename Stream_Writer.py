import praw
import prawcore
from prawcore.exceptions import PrawcoreException
import os
import time
import multiprocessing as mp

class Stream_Writer:
    # 5 second wait to let praw comment stream populate
    COOLDOWN_TIME = 5

    process_id = 0
    sub_name = ''

    reddit = 0
    subreddit = 0

    comment_rate = 10   # Number of comments to print a message for
    comment_number = 0  # Number of comments processed

    debug = True

    # /////////////////////////////////////////////////////////////////
    #   Method: __init__
    #   Purpose: Initializes class variables and creates local praw instance
    #   Inputs:
    #       'comment_queue' - A queue holding comments to process
    #       'sub_name'      - Name of the Subreddit being scraped
    # /////////////////////////////////////////////////////////////////
    def __init__(self, comment_queue, sub_name):
        # Initialize class variables
        self.sub_name = sub_name
        self.comment_queue = comment_queue

        # Each process that scrapes reddit needs its own instance of praw
        self.reddit = praw.Reddit("stockscraper")
        self.subreddit = self.reddit.subreddit(self.sub_name)

    def p(self, s):
        if self.debug:
            print(f'SSW {self.process_id}\t| {s}')

    # /////////////////////////////////////////////////////////////////
    #   Method: writer_wrapper
    #   Purpose: Manages stream_scraper_writer
    # /////////////////////////////////////////////////////////////////
    def writer_wrapper(self):
        self.process_id = os.getpid()
        print(f'SSW {self.process_id}\t| {self.sub_name} stream writer started')

        while True:            
            writer = mp.Process(target=self.stream_scraper_writer)
            writer.start()
            writer.join()

            print(f'SSW {self.process_id}\t| Waiting for {self.COOLDOWN_TIME} seconds.')
            time.sleep(self.COOLDOWN_TIME)


    # /////////////////////////////////////////////////////////////////
    #   Method: stream_scraper_writer
    #   Purpose: Processes queue of streamed comments into a comment queue
    # /////////////////////////////////////////////////////////////////
    def stream_scraper_writer(self):
        stream = self.subreddit.stream.comments(skip_existing=True)

        for r_comment in stream:
            if r_comment is not None:
                self.comment_number += 1
                if (self.comment_number % self.comment_rate) == 0:
                    self.p(f'Comment {self.comment_number} in {self.sub_name} added to the queue')
                self.comment_queue.put(r_comment)