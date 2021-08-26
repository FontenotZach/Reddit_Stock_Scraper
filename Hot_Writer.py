import praw
import os
import time
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

class Hot_Writer(Process_Wrapper):
    COOLDOWN_TIME = 1800    # Wait half an hour before scraping hot posts again
    VARIANCE = 360          # With a good amount of variance thrown in as well
    SCRAPE_LIMIT = 30       # The number of top posts to scrape each hour
    PRINT_FREQUENCY = 100   # Print something for every 100 comments scraped
    COMMENT_TYPE = 'hot'
    PROCESS_TYPE_NAME = 'HOTW'
    
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
    #   Method: hot_wrapper
    #   Purpose: Manages scrape_hot_posts
    # /////////////////////////////////////////////////////////////////
    def hot_wrapper(self):
        self.PROCESS_ID = os.getpid()
        # Each process that scrapes reddit needs its own instance of praw
        self.reddit = praw.Reddit(
            client_id = os.getenv('praw_client_id'),
            client_secret = os.getenv('praw_client_secret'),
            user_agent='Reddit Stock Scraper v0.5 by FontenotZ, JBurns',
        )
        self.subreddit = self.reddit.subreddit(self.sub_name)
        self.thread_print(f'Hot post writer started.')
        
        while True:
            hot_scraper = mp.Process(target=self.scrape_hot_posts)
            hot_scraper.start()
            hot_scraper.join()

            self.random_sleep(self.COOLDOWN_TIME, self.VARIANCE)

    # /////////////////////////////////////////////////////////////////
    #   Method: scrape_hot_posts
    #   Purpose: Collects comments from hottest Subreddit posts
    # /////////////////////////////////////////////////////////////////
    def scrape_hot_posts(self):
        comments_scraped = 0

        try:
            self.subreddit = self.reddit.subreddit(self.sub_name)
            for submission in self.subreddit.hot(limit=self.SCRAPE_LIMIT):
                self.debug_print(f'Getting all comments from {self.sub_name} -> {submission.title[:30]}')

                # Get all comments for the post
                submission.comments.replace_more(limit=None)

                for r_comment in submission.comments:
                    self.comment_queue.put((self.COMMENT_TYPE, r_comment))
                    comments_scraped += 1
                    if comments_scraped % self.PRINT_FREQUENCY == 0:
                        self.debug_print(f'{comments_scraped} comments scraped from the hot posts of {self.sub_name}')
        except Exception as e:
            self.thread_print(f'Encountered exception {e}')
            self.random_sleep(self.VARIANCE * 2, self.VARIANCE)
            