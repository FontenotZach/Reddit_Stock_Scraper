import os
import time

class Queue_Watcher:
    def __init__(self, queue, name, timeout=30):
        self.queue = queue
        self.name = name
        self.timeout = timeout
    
    def periodic_check(self):
        self.process_id = os.getpid()
        while True:
            print(f'QUE {self.process_id}\t| Queue {self.name}: {self.queue.qsize()}')
            time.sleep(self.timeout)