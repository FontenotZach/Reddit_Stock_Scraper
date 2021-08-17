class Process_Wrapper:
    DEBUG = True
    PROCESS_ID = 0
    PROCESS_TYPE_NAME = ''

    # Debug printer shared between all wrapped objects
    def p(self, str):
        if self.DEBUG:
            print(f'{self.PROCESS_TYPE_NAME:6} {self.PROCESS_ID}\t| {str}')


    #
    def wait_random(self):
        pass