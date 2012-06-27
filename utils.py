#  Copyright 2012 MemSQL, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


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

