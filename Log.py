import datetime
from pathlib import Path

class Log:
    log_path = 'Log/'

    def start_log(self):
        start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = self.log_path + start_timestamp + '.txt'
        file = open(self.log_path, 'x')
        file.close()
        file = open(self.log_path, 'a')
        start_msg = "-------------------------\nLog started @ " + start_timestamp + "\n-------------------------\n"
        file.write(start_msg)
        file.close()

    def update_log(self, message, sender):
        delim = '|'
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
        file = open(self.log_path, 'a')
        msg = "\n\t" + sender + delim + timestamp + delim + message
        file.write(msg)
        file.close()
