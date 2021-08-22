import os
import time
import multiprocessing as mp
from Process_Wrapper import Process_Wrapper

class Queue_Watcher(Process_Wrapper):
    PROCESS_TYPE_NAME = 'QUEUE'
    COOLDOWN_TIME = 90

    def __init__(self, queue, name):
        Process_Wrapper.__init__(self)
        self.queue = queue
        self.sub_name = name
    
    def watch_queue(self):
        self.PROCESS_ID = os.getpid()
        self.thread_print(f'Starting watcher for {self.sub_name} queue.')

        while True:
            watcher = mp.Process(target=self.thread_print, args=(f'Queue size: {self.queue.qsize()}',))
            watcher.start()
            watcher.join()

            time.sleep(self.COOLDOWN_TIME)