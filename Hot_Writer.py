import praw
import prawcore
from prawcore.exceptions import PrawcoreException
import os
import time
import multiprocessing as mp

from Util import get_post_comments, comment_score

class Hot_Writer:
    COOLDOWN_TIME = 3600    # Wait a full hour before scraping hot posts again
    SCRAPE_LIMIT = 30       # The number of top posts to scrape each hour
    COMMENT_TYPE = 'hot'
    DEBUG = True
    
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
        self.reddit = praw.Reddit("stockscraper")
        self.subreddit = self.reddit.subreddit(self.sub_name)


    def p(self, s):
        if self.DEBUG:
            print(f'HOT {self.process_id}\t| {s}')


    # /////////////////////////////////////////////////////////////////
    #   Method: hot_wrapper
    #   Purpose: Manages scrape_hot_posts
    # /////////////////////////////////////////////////////////////////
    def hot_wrapper(self):
        self.process_id = os.getpid()
        
        print(f'HOT {self.process_id}\t| {self.sub_name} hot post scraper started')
        
        while True:
            hot_scraper = mp.Process(target=self.scrape_hot_posts)
            hot_scraper.start()
            hot_scraper.join()

            print(f'HOT {self.process_id}\t| Waiting for {self.COOLDOWN_TIME} seconds.')
            time.sleep(self.COOLDOWN_TIME)

    # /////////////////////////////////////////////////////////////////
    #   Method: scrape_hot_posts
    #   Purpose: Collects comments from hottest Subreddit posts
    # /////////////////////////////////////////////////////////////////
    def scrape_hot_posts(self):
        for submission in self.subreddit.hot(limit=self.SCRAPE_LIMIT):
            self.p(f'Getting all comments from {self.sub_name} -> {submission.title[:30]}')
            
            # Get all comments for the post
            submission.comments.replace_more(limit=None)
            
            for r_comment in submission.comments:
                self.comment_queue.put((self.COMMENT_TYPE, r_comment))
            