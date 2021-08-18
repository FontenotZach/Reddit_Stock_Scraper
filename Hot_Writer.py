import praw
import os
import time
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

class Hot_Writer(Process_Wrapper):
    COOLDOWN_TIME = 3600    # Wait a full hour before scraping hot posts again
    SCRAPE_LIMIT = 30       # The number of top posts to scrape each hour
    COMMENT_TYPE = 'hot'
    PROCESS_TYPE_NAME = 'HOT'
    
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


    # /////////////////////////////////////////////////////////////////
    #   Method: hot_wrapper
    #   Purpose: Manages scrape_hot_posts
    # /////////////////////////////////////////////////////////////////
    def hot_wrapper(self):
        self.PROCESS_ID = os.getpid()
        
        print(f'{self.PROCESS_TYPE_NAME:6} {self.PROCESS_ID}\t| {self.sub_name} hot post scraper started')
        
        while True:
            hot_scraper = mp.Process(target=self.scrape_hot_posts)
            hot_scraper.start()
            hot_scraper.join()

            self.p(f'Sleeping for {self.COOLDOWN_TIME} seconds.')
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
            