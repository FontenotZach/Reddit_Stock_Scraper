import datetime
from pathlib import Path

class Log:
    log_path = 'Log/'

    def start_log(self):
        start_timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
        self.log_path = self.log_path + start_timestamp + '.txt'
        file = open(self.log_path, 'x')
        file.close()
        file = open(self.log_path, 'a')
        start_msg = "-------------------------\nLog started @ " + start_timestamp + "\n-------------------------\n"
        file.write(start_msg)
        file.close()

    def update_log(self, message, sender):
        updated = False
        timeout = 10
        count = 0
        while not updated and count < timeout:
            count += 1
            try:
                delim = '|'
                timestamp = datetime.datetime.now().strftime("%Y:%m:%d-%H:%M:%S")
                file = open(self.log_path, 'a')
                msg = "\t" + sender + delim + timestamp + delim + message + "\n"
                file.write(msg)
                file.close()
            except:
                print('Logging error.')
            else:
                updated = True
