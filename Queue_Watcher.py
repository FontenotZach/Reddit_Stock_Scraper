import os
import time
from Process_Wrapper import Process_Wrapper

class Queue_Watcher(Process_Wrapper):
    def __init__(self, queue, name, timeout=30):
        self.queue = queue
        self.name = name
        self.timeout = timeout
        self.DEBUG = True
        self.PROCESS_TYPE_NAME = 'QUEUE'
    
    def periodic_check(self):
        self.PROCESS_ID = os.getpid()
        while True:
            self.p(f'Queue {self.name}: {self.queue.qsize()}')
            time.sleep(self.timeout)