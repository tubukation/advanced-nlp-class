import os
import sys

from io.NumberRangeFileFilter import NumberRangeFileFilter
import ling.Trees as Trees


class TreeCollection:
    """
    Collection of Trees.
    """

    def __init__(self, path, low_filenum, high_filenum):
        self.file_filter = NumberRangeFileFilter(
                ".mrg", low_filenum, high_filenum, True)
        self.files = self.get_files_under(path)
    