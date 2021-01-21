#!/usr/bin/python3

class Stats:
    '''
    Simple class to manage stats.

    Once the object is created, stat value can be increased, returned
    and reset to zero.
    '''

    def __init__(self):
        self.value = 0

    def increase(self):
        self.value += 1

    def get(self):
        return self.value

    def reset(self):
        self.value = 0
