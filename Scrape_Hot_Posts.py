import os
import random

from Util import *
from Storage_Manager import *

# /////////////////////////////////////////////////////////////////
#   Method: scrape_hot_posts
#   Purpose: Collects comments from hottest Subreddit posts
#   Inputs:
#           'num'               - the number of posts to scrape
#           'sub'               - the Subreddit being scraped
#           'logger'            - Instance of the Log object
#           'storage_manager'   - Instance of the Storage Manager object
# /////////////////////////////////////////////////////////////////
def scrape_hot_posts(num, sub, logger, storage_manager):
    sub_name = sub.display_name                 # name of sub to scrape
    process_id = os.getpid()()  # id of thread

    #logger.update_log('Hot post scraper running on ' + sub_name, 'SH ' + str(process_id))
    print(f'SH {process_id}\t| {sub_name} hot post scraper started')

    # Hourly loop to obtain hot posts
    while True:
        # Wait for between 5 and 10 seconds to begin processing
        n = (random.random() * 5.0) + 5.0
        print(f'SH {process_id}\t| Waiting {n:.2f} seconds before scraping hottest from {sub_name}')
        time.sleep(n)
        print(f'SH {process_id}\t| Compiling Hottest {num} {sub_name} posts')
        hot_posts = []  # list of hot posts for {sub_name}

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
                print(f'SH {process_id}\t| Exception {e}')
            if not posts_retr:
                retries += 1
                print(f'SH {process_id}\t| Posts not retrieved.')
                time.sleep(30)
            if retries >= max_retries:
                print(f'SH {process_id}\t| Timed out reading posts')
                timeout = True

        comments_processed = 0  # total comments processed
        tickers = {}            #dictionary of tickers (key: symbol, value:score)

        for submission in hot_posts:
            # If more than 45 minutes have passed (75% of hour), stop processing more posts
            # Won't eat into next hour's counting time
            #if get_index() - start_hour > 0.75:
            #    break
            print(f'SH {process_id}\t| Getting comments from -> {submission.title[:30]}')
            comments = get_post_comments(submission)  # returns tuples (body, depth, score)
            print(f'SH {process_id}\t| Scraping post -> {submission.title[:30]}')

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

        # 
        sorted_tickers = sorted(tickers.items(), key=lambda x:x[1], reverse=True)

        print(f'SH {process_id}\t| Processed {comments_processed} hot comments from {sub_name}')
        print(f'SH {process_id}\t| Writing out hot results from {sub_name}')

        #logger.update_log(f'{comments_processed} hot comments scraped from {sub_name}', 'SH '+ str(process_id))
        if len(sorted_tickers) != 0:
            storage_manager.write_data(sorted_tickers, 'hot', sub_name)

        print(f'SH {process_id}\t| waiting for the rest of the hour...')
        wait_for_next_hour()

