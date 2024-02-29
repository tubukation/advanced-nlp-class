
from __future__ import division
#!/usr/bin/env python
import json
import math
import os
import re
import sys
import glob
import heapq

from PorterStemmer import PorterStemmer

class IRSystem:

    def __init__(self):
        # For holding the data - initialized in read_data()
        self.titles = []
        self.docs = []
        self.vocab = []
        # For the text pre-processing.
        self.re_alphanum = re.compile(r'[^a-zA-Z0-9]')
        self.p = PorterStemmer()

    def get_uniq_words(self):
        return set(word for doc in self.docs for word in doc)

    def __read_raw_data(self, dirname):
        print 'Stemming Documents...'

        titles = []
        docs = []
        os.mkdir(os.path.join(dirname, 'stemmed'))
        re_title = re.compile(r'(.*)\s+\d+\.txt')

        # make sure we're only getting the files we actually want
        filenames = [fn for fn in glob.glob(os.path.join(dirname, 'raw', '*.txt'))
                        if not os.path.isdir(fn)] 

        for i, filename in enumerate(filenames):
            title = re_title.search(os.path.basename(filename)).group(1)
            print '    Doc %d of %d: %s' % (i+1, len(filenames), title)
            titles.append(title)
            contents = []