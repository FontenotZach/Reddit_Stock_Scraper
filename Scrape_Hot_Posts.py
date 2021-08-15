import praw
import prawcore
import os
import multiprocessing as mp

from Util import *
from Storage_Manager import *

class Scrape_Hot_Posts:
    # 5 second wait to let praw comment stream populate
    COOLDOWN_TIME = 5
    SCRAPE_LIMIT = 30

    process_id = 0
    sub_name = ''
    storage_queue = 0

    reddit = 0
    subreddit = 0

    debug = True

    # /////////////////////////////////////////////////////////////////
    #   Method: __init__
    #   Purpose: Initializes class variables and creates local praw instance
    #   Inputs:
    #           'sub_name'      - Name of the Subreddit being scraped
    #           'storage_queue' - A queue holding data to be written to disk
    # /////////////////////////////////////////////////////////////////
    def __init__(self, sub_name, storage_queue):
        # Initialize class variables
        self.sub_name = sub_name
        self.storage_queue = storage_queue
        
        # Each process that scrapes reddit needs its own instance of praw
        self.reddit = praw.Reddit("stockscraper")
        self.subreddit = self.reddit.subreddit(self.sub_name)


    def p(self, s):
        if self.debug:
            print(f'SH {self.process_id}\t| {s}')


    # /////////////////////////////////////////////////////////////////
    #   Method: hot_wrapper
    #   Purpose: Manages scrape_hot_posts
    # /////////////////////////////////////////////////////////////////
    def hot_wrapper(self):
        self.process_id = os.getpid()
        
        print(f'SH {self.process_id}\t| {self.sub_name} hot post scraper started')
        
        while True:
            hot_scraper = mp.Process(target=self.scrape_hot_posts)
            hot_scraper.start()
            hot_scraper.join()

            print(f'SH {self.process_id}\t| Finished, waiting for the rest of the hour...')
            wait_for_next_hour()

    # /////////////////////////////////////////////////////////////////
    #   Method: scrape_hot_posts
    #   Purpose: Collects comments from hottest Subreddit posts
    # /////////////////////////////////////////////////////////////////
    def scrape_hot_posts(self):
        hot_posts = []  # list of hot posts for {sub_name}
        
        # This block tries obtaining hot posts until PRAW responds correctly or timeout is reached
        posts_retr = False  # have the posts been retrieved?
        retries = 0         # number of attempts made this hour
        max_retries = 10    # max attempts per hour
        timeout = False     # has max attempts been reached?

        while not posts_retr and not timeout:
            # try to obtain posts
            try:
                for submission in self.subreddit.hot(limit=self.SCRAPE_LIMIT):
                    hot_posts.append(submission)
                # check if posts have been collected
                if len(hot_posts) > 0:
                    posts_retr = True
            except Exception as e:
                self.p(f'Exception {e}')

            if not posts_retr:
                retries += 1
                self.p(f'Posts not retrieved.')
                time.sleep(self.COOLDOWN_TIME)
            if retries >= max_retries:
                self.p(f'Timed out reading posts')
                timeout = True

        comments_processed = 0  # total comments processed
        tickers = {}            #dictionary of tickers (key: symbol, value:score)

        for submission in hot_posts:
            # If more than 45 minutes have passed (75% of hour), stop processing more posts
            # Won't eat into next hour's counting time
            #if get_index() - start_hour > 0.75:
            #    break
            self.p(f'Getting comments from -> {submission.title[:30]}')
            comments = get_post_comments(submission)  # returns tuples (body, depth, score)
            self.p(f'Scraping post -> {submission.title[:30]}')

            # Pulls out metion data and comglomerates for each ticker
            for comment in comments:
                comments_processed += 1
                result = comment_score(comment)
                if result != None:
                    for new_ticker in result:
                        scraped_symbol = new_ticker.symbol
                        if scraped_symbol in tickers:
                            #print(f'Existing ticker {new_ticker.symbol} {sub_name}')
                            tickers[scraped_symbol] = tickers[scraped_symbol] + new_ticker.score
                        else:
                            #print(f'New ticker {new_ticker.symbol} {sub_name}')
                            tickers[scraped_symbol] = new_ticker.score

        # Sort the ticker dict into a list of tuples (symbol, score)
        sorted_tickers = sorted(tickers.items(), key=lambda x:x[1], reverse=True)
        self.p(f'Processed {comments_processed} hot comments from {self.sub_name}, got {len(sorted_tickers)} results')

        if len(sorted_tickers) != 0:
            data = (sorted_tickers, 'hot', self.sub_name)
            self.storage_queue.put(data)