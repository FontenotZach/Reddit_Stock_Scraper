import time
import signal
import multiprocessing as mp

from Util import *
from QueueMessage import QueueMessage
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
    print('MAIN: Idle')
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(10)
        # check parent queue messages


# /////////////////////////////////////////////////////////////////
#   Method: __main__
#   Purpose: Starting point
# /////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    procs = []
    # List of subreddit names
    subreddits = [ 'wallstreetbets', 'investing', 'stocks', 'pennystocks' ]

    # Run initialization TODO: Merge more into this
    initialize(subreddits)
    mp.set_start_method('spawn')

    # Start storage manager
    storage_queue = mp.Queue() 
    storage_manager = StorageManager(storage_queue)
    procs.append(mp.Process(target=storage_manager.process_queue, name='storage-manager'))
    
    # Start another thread to watch the storage queue
    storage_watcher = Queue_Watcher(storage_queue, 'storage-queue')
    procs.append(mp.Process(target=storage_watcher.periodic_check, name='storage-q-watcher'))
    
    # These are formed into a list of Tuples with the form (subreddit_name, stream_queue)
    subreddit_list = []

    for sub_name in subreddits:
        empty_queue = mp.Queue()
        subreddit_list.append((sub_name, empty_queue))

    # Starting processes for stream_scraper_writer, scrape_hot_posts, and stream_scraper_reader
    # Each new sub needs one thread for each method
    for sub in subreddit_list:
        # Create the wrapper objects for each thread
        comment_queue_reader    = Queue_Reader(sub[1], sub[0], storage_queue)
        stream_comment_manager  = Stream_Writer(sub[1], sub[0])
        hot_comment_manager     = Hot_Writer(sub[1], sub[0])
        comment_queue_watcher   = Queue_Watcher(sub[1], f'{sub[0]}-comments')

        procs.append(mp.Process(target=comment_queue_reader.reader_wrapper, name=f'{sub[0]}-q-reader'))
        procs.append(mp.Process(target=stream_comment_manager.writer_wrapper, name=f'{sub[0]}-stream-scraper'))
        procs.append(mp.Process(target=hot_comment_manager.hot_wrapper, name=f'{sub[0]}-hot-scraper'))
        procs.append(mp.Process(target=comment_queue_watcher.periodic_check, name=f'{sub[0]}-q-watcher'))

    for proc in procs:
        print(f'MAIN: Starting process {proc.name}')
        proc.start()

    # allow parent thread to idle
    idle()

######################################################################################
