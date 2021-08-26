import praw
import os
import time
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

class Stream_Writer(Process_Wrapper):
    COOLDOWN_TIME = 60      # ~60 second wait to let praw comment stream populate
    VARIANCE = 10           # Variance between processes
    PRINT_FREQUENCY = 100   # Print something for every 100 comments scraped
    COMMENT_TYPE = 'stream'
    PROCESS_TYPE_NAME = 'STRW'

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

    # /////////////////////////////////////////////////////////////////
    #   Method: writer_wrapper
    #   Purpose: Manages stream_scraper_writer
    # /////////////////////////////////////////////////////////////////
    def writer_wrapper(self):
        self.PROCESS_ID = os.getpid()
        # Each process that scrapes reddit needs its own instance of praw
        self.reddit = praw.Reddit(
            client_id = os.getenv('praw_client_id'),
            client_secret = os.getenv('praw_client_secret'),
            user_agent='Reddit Stock Scraper v0.5 by FontenotZ, JBurns',
        )
        
        self.thread_print(f'Stream writer started.')

        while True:
            self.debug_print(f'Scraping stream from {self.sub_name}') 
            writer = mp.Process(target=self.stream_scraper_writer)
            writer.start()
            writer.join()

            self.random_sleep(self.COOLDOWN_TIME, self.VARIANCE)


    # /////////////////////////////////////////////////////////////////
    #   Method: stream_scraper_writer
    #   Purpose: Processes queue of streamed comments into a comment queue
    # /////////////////////////////////////////////////////////////////
    def stream_scraper_writer(self):
        comments_scraped = 0

        try:
            self.subreddit = self.reddit.subreddit(self.sub_name)
            for r_comment in self.subreddit.stream.comments(skip_existing=True):
                if r_comment is not None:
                    self.comment_queue.put((self.COMMENT_TYPE, r_comment))
                    comments_scraped += 1
                    if comments_scraped % self.PRINT_FREQUENCY == 0:
                        self.debug_print(f'{comments_scraped} comments scraped from the {self.sub_name} stream')
        except Exception as e:
            self.thread_print(f'Encountered exception {e}')
            self.random_sleep(self.VARIANCE * 2, self.VARIANCE)
