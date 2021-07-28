from Enums import *

class QueueMessage:

    pid = 0
    set = ''
    sub = ''
    status = Status.NONE

    def __init__(self, pid, set, sub, status):
        self.pid = pid
        self.set = set
        self.sub = sub
        self.status = status
