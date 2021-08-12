import _thread
from operator import attrgetter
from Util import *

# /////////////////////////////////////////////////////////////////
#   Method: scrape_hot_posts
#   Purpose: Collects comments from hottest Subreddit posts
#   Inputs:
#           'num'   - the number of posts to scrape
#           'sub'   - the Subreddit being scraped
#           'l'     - Instance of the Log object
# /////////////////////////////////////////////////////////////////
def scrape_hot_posts(num, sub, l):
    # Fatal error catching block
    try:
        sub_name = sub.display_name                 # bane of sub to scrape
        thread_native_id = _thread.get_native_id()  # id of thread
        # Catch issues with logging
        try:
            l.update_log('Hot post scraper running on ' + sub_name, 'SH ' + str(thread_native_id))
        except Exception as e:
            print('error updating log')
        # Hourly loop to obtain hot posts
        while True:
            # Inner loop try block ensures PRAW interrutions are handled
            try:
                hot_posts = []  # list of hot posts for {sub_name}
                print('SH ', thread_native_id, '\t| ', end='')
                print('Compiling Hottest ' + str(num) + ' ' + sub_name + ' posts')

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
                        l.update_log(f'Could not retrieve hot posts from {sub_name}: {str(e)}', 'SH ' + str(thread_native_id))
                    if not posts_retr:
                        retries += 1
                        time.sleep(30)
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
                        print(f'Scraping post -> {submission.title}')

                        # Pulls out metion data and comglomerates for each ticker
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
                    l.update_log(f'Error in processing hot posts from {sub_name}: {str(e)}', 'SH '+ str(thread_native_id))


                tickers.sort(key = attrgetter('score'), reverse = True)
                print('SH ', thread_native_id, '\t| ', end='')
                print(f'Processed {comments_processed} hot comments from {sub_name}')
                print('SH ', thread_native_id, '\t| ', end='')
                print(f'Writing out hot results from {sub_name}')

                l.update_log(f'{str(comments_processed)} hot comments scraped from {sub_name}', 'SH '+ str(thread_native_id))

                # Try writing data to file
                try:
                    storage_manager(tickers, 'hot', sub_name)
                except Exception as e:
                    l.update_log('Error storing tickers from ' + sub_name + ' to file:' + str(e), 'SH '+ str(thread_native_id))
                    l.update_log('Stack trace: ' + traceback.format_exc(), 'SH '+ str(thread_native_id))
                print('SH ', thread_native_id, '\t| ', end='')
                print('Waiting...')
                # TODO: Pass queue message to parent.  If message isn't present at beginning of next hour, kill thread and start over
                wait_for_next_hour()
            except Exception as e:
                l.update_log(f'Unexpected error while scraping {sub_name}: {str(e)}', 'SH '+ str(thread_native_id))

    except Exception as e:
        l.update_log(f'Unexpected fatal error while scraping {sub_name}: {str(e)}', 'SH '+ str(thread_native_id))

