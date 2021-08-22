import time
import signal
import multiprocessing as mp

from Util import *
from Storage_Manager import StorageManager
from Stream_Writer import Stream_Writer
from Hot_Writer import Hot_Writer
from Queue_Reader import Queue_Reader
from Queue_Watcher import Queue_Watcher
from Init import initialize


# /////////////////////////////////////////////////////////////////
#   Method: signal_handler
#   Purpose: Handles SIGINT (^C)
# /////////////////////////////////////////////////////////////////
def signal_handler(sig, frame):
    print('Abort detected.  Do you wish to quit?  y/N')
    response = input()
    if response == 'Y' or response == 'y':
        exit(0)
    print('Abort cancelled. Continuing..')
    idle()


# /////////////////////////////////////////////////////////////////
#   Method: idle
#   Purpose: Parent thread waiting and periodically error checking
# /////////////////////////////////////////////////////////////////
def idle():
    print('Main: Idle')
    #signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(1000)
        # check parent queue messages


# /////////////////////////////////////////////////////////////////
#   Method: __main__
#   Purpose: Starting point
# /////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    procs = []
    # List of subreddit names
    subreddits = { 'wallstreetbets', 'investing', 'stocks', 'pennystocks' }

    # Run initialization TODO: Merge more into this
    initialize(subreddits)
    mp.set_start_method('spawn')
    storage_queue = mp.Queue()
    comment_queue = mp.Queue()

    # Start storage manager
    # Start another thread to watch the storage queue
    storage_manager = StorageManager(data_queue=storage_queue)
    storage_watcher = Queue_Watcher(queue=storage_queue, name='storage')
    mp.Process(target=storage_manager.storage_manager, name='storage-manager').start()
    mp.Process(target=storage_watcher.watch_queue, name='storage-queue-watcher').start()

    comment_queue_reader = Queue_Reader(comment_queue=comment_queue, storage_queue=storage_queue, subreddits=subreddits)
    comment_queue_watcher   = Queue_Watcher(queue=comment_queue, name='comments')
    mp.Process(target=comment_queue_reader.reader_wrapper, name='comment-queue-reader').start()
    mp.Process(target=comment_queue_watcher.watch_queue, name='comment-queue-watcher').start()

    # Starting processes for stream_scraper_writer, scrape_hot_posts, and stream_scraper_reader
    # Each new sub needs one thread for each method
    for sub in subreddits:
        # Create the wrapper objects for each thread
        hot_comment_writer     = Hot_Writer(comment_queue=comment_queue, sub_name=sub)
        stream_comment_writer  = Stream_Writer(comment_queue=comment_queue, sub_name=sub)
        
        mp.Process(target=stream_comment_writer.writer_wrapper, name=f'{sub}-stream-scraper').start()
        mp.Process(target=hot_comment_writer.hot_wrapper, name=f'{sub}-hot-scraper').start()

    # allow parent thread to idle
    idle()

######################################################################################
