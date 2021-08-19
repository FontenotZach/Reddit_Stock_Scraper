import praw
import os
import time
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

class Stream_Writer(Process_Wrapper):
    COOLDOWN_TIME = 5   # 5 second wait to let praw comment stream populate
    COMMENT_TYPE = 'stream'
    PROCESS_TYPE_NAME = 'STREAM'

    # /////////////////////////////////////////////////////////////////
    #   Method: __init__
    #   Purpose: Initializes class variables and creates local praw instance
    #   Inputs:
    #           'comment_queue' - A queue holding comments to process
    #           'sub_name'      - Name of the Subreddit being scraped
    # /////////////////////////////////////////////////////////////////
    def __init__(self, comment_queue, sub_name):
        # Initialize class variables
        self.sub_name = sub_name
        self.comment_queue = comment_queue

        # Each process that scrapes reddit needs its own instance of praw
        self.reddit = praw.Reddit(
            client_id = os.getenv('praw_client_id'),
            client_secret = os.getenv('praw_client_secret'),
            user_agent='Reddit Stock Scraper v0.5 by FontenotZ, JBurns',
        )
        self.subreddit = self.reddit.subreddit(self.sub_name)

    # /////////////////////////////////////////////////////////////////
    #   Method: writer_wrapper
    #   Purpose: Manages stream_scraper_writer
    # /////////////////////////////////////////////////////////////////
    def writer_wrapper(self):
        self.PROCESS_ID = os.getpid()
        print(f'{self.PROCESS_TYPE_NAME:6} {self.PROCESS_ID}\t| {self.sub_name} stream writer started')

        while True:
            self.p(f'Scraping stream from {self.sub_name}') 
            writer = mp.Process(target=self.stream_scraper_writer)
            writer.start()
            writer.join()

            self.p(f'Sleeping for {self.COOLDOWN_TIME} seconds.')
            time.sleep(self.COOLDOWN_TIME)


    # /////////////////////////////////////////////////////////////////
    #   Method: stream_scraper_writer
    #   Purpose: Processes queue of streamed comments into a comment queue
    # /////////////////////////////////////////////////////////////////
    def stream_scraper_writer(self):
        stream = self.subreddit.stream.comments(skip_existing=True)

        for r_comment in stream:
            if r_comment is not None:
                self.comment_queue.put((self.COMMENT_TYPE, r_comment))