import os

import ling.Trees as Trees

class NumberRangeFileFilter:
    """
    Class to use as filter for files (by file number).
    """
    def __init__(self, extension, low_filenum, high_filenum, recurse):
        self.i = -1
        self.high_filenum = high_filenum
        self.low_filenum = low_filenum
