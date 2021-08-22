class Process_Wrapper:
    DEBUG = True
    PROCESS_ID = -1
    PROCESS_TYPE_NAME = 'GEN'

    sub_name = ''

    # Debug printer shared between all wrapped objects
    def debug_print(self, str):
        if self.DEBUG:
            self.thread_print(str)

    def thread_print(self, str):
        print(f'{self.PROCESS_TYPE_NAME[:5]:5} {self.PROCESS_ID:5} {self.sub_name[:5]:5} | {str}')
