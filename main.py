import multiprocessing as mp

from Util import *
from Storage_Manager import StorageManager
from Stream_Writer import Stream_Writer
from Hot_Writer import Hot_Writer
from Queue_Reader import Queue_Reader
from Queue_Watcher import Queue_Watcher
from Init import initialize

# /////////////////////////////////////////////////////////////////
#   Method: __main__
#   Purpose: Starting point
# /////////////////////////////////////////////////////////////////
if __name__ == '__main__':
    procs = []
    # List of subreddit names
    subreddits = { 'wallstreetbets', 'investing', 'stocks', 'pennystocks' }

    # Run initialization
    initialize(subreddits)

    # Create the process-safe queues for comments and ticker data storage
    storage_queue = mp.Queue()
    comment_queue = mp.Queue()

    # Create and start storage manager, then start another process to watch the
    # storage queue
    storage_manager = StorageManager(data_queue=storage_queue)
    storage_watcher = Queue_Watcher(queue=storage_queue, name='storage')
    mp.Process(target=storage_manager.storage_manager, name='storage-manager').start()
    mp.Process(target=storage_watcher.watch_queue, name='storage-queue-watcher').start()

    # Start comment queue reader, then start another process to watch the
    # comment queue
    comment_queue_reader = Queue_Reader(comment_queue=comment_queue, storage_queue=storage_queue, subreddits=subreddits)
    comment_queue_watcher   = Queue_Watcher(queue=comment_queue, name='comments')
    mp.Process(target=comment_queue_reader.reader_wrapper, name='comment-queue-reader').start()
    mp.Process(target=comment_queue_watcher.watch_queue, name='comment-queue-watcher').start()

    # Starting processes for hot_comment_writer and stream_comment_writer. Each
    # new sub needs one process for each method
    for sub in subreddits:
        # Create the wrapper objects for each thread
        hot_comment_writer     = Hot_Writer(comment_queue=comment_queue, sub_name=sub)
        stream_comment_writer  = Stream_Writer(comment_queue=comment_queue, sub_name=sub)
        
        mp.Process(target=stream_comment_writer.writer_wrapper, name=f'{sub}-stream-scraper').start()
        mp.Process(target=hot_comment_writer.hot_wrapper, name=f'{sub}-hot-scraper').start()
