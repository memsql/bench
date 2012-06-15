import time

class Reporter(object):
    '''A utility class that can report the number of actions per second to a
    listening master process over a pipe.'''
    def __init__(self, pipe):
        '''Initialize the reporter, writing on given pipe.'''
        self.pipe = pipe
        self.count = 0
        self.start_time = time.time()
    
    def mark_event(self):
        '''Mark that an event has occurred, automatically reporting the number
        of actions per second to the master.'''
        self.count += 1
        if time.time() - self.start_time > 1.0:
            self.report()

    def report(self):
        '''Recalculate and send the number of actions per second.'''
        self.pipe.send(self.count / (time.time() - self.start_time))
        self.start_time = time.time()
        self.count = 0

