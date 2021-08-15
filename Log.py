import datetime
import os
from multiprocessing import Lock

class Log:
    log_path = 'Log/'
    log_mutex = 0

    def __init__(self):
        self.log_mutex = Lock()

        start_timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
        self.log_path = os.path.join(self.log_path, f'{start_timestamp}.txt')

        self.log_mutex.acquire()
        file = open(self.log_path, 'w')
        file.write(f'-------------------------\nLog started @ {start_timestamp}\n-------------------------\n')
        file.close()
        self.log_mutex.release()

    def update_log(self, message, sender):
        delim = ' | '
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")

        self.log_mutex.acquire()
        file = open(self.log_path, 'a')
        file.write(f'\t{sender}{delim}{timestamp}{delim}{message}\n')
        file.close()
        self.log_mutex.release()
