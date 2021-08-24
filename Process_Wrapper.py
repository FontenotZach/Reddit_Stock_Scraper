import time
import random

class Process_Wrapper:
    DEBUG = True
    PROCESS_ID = -1
    PROCESS_TYPE_NAME = 'GEN'

    sub_name = ''


    # Debug printer shared between all wrapped objects
    def debug_print(self, str):
        if self.DEBUG:
            self.thread_print(str)


    # Process object print function to automatically format process-specific data
    def thread_print(self, str):
        print(f'{self.PROCESS_TYPE_NAME[:5]:5} {self.PROCESS_ID:5} {self.sub_name[:8]:8} | {str}', flush=self.DEBUG)


    # Sleeps for a random amount of time, with an average of avg_time and a range given by variance
    def random_sleep(self, avg_time, variance):
        t = avg_time + ((random.random() - 0.5) * variance)
        self.debug_print(f'Sleeping for {t:.2f} seconds.')
        time.sleep(t)
        pass
