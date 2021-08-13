import datetime
import os
from threading import Lock

class Log:
    log_path = 'Log/'
    log_mutex = Lock()

    def start_log(self):
        start_timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
        self.log_path = os.path.join(self.log_path, f'{start_timestamp}.txt')

        log_mutex.acquire()
        file = open(self.log_path, 'w')
        file.write(f'-------------------------\nLog started @ {start_timestamp}\n-------------------------\n')
        file.close()
        log_mutex.release()

    def update_log(self, message, sender, log_mutex):
        delim = ' | '
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")

        log_mutex.acquire()
        file = open(self.log_path, 'a')
        file.write(f'\t{sender}{delim}{timestamp}{delim}{message}\n')
        file.close()
        log_mutex.release()
