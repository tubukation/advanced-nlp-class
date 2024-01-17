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
        self.trees = self.get_trees()
        self.index = 0


    def __iter__(self):
        return self


    def next(self):
        if self.index < len(self.trees):
            tree = self.trees[self.index]
            self.index += 1
            return tree
        else:
            raise StopIteration


    def get_files_under(self, path):
        files = []
        self.add_files_under(path, files)
        return files


    def add_files_under(self, root, files):
        #if not filter(root, self.file_filter.accept):
        if no