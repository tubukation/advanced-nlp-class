# NLP Programming Assignment #3
# NaiveBayes
# 2012

#
# The area for you to implement is marked with TODO!
# Generally, you should not need to touch things *not* marked TODO
#
# Remember that when you submit your code, it is not run from the command line 
# and your main() will *not* be run. To be safest, restrict your changes to
# addExample() and classify() and anything you further invoke from there.
#

import sys
import getopt
import os
import math

_ENGLISH_STOP_WORDS = set([ 
    'a', 'a\'s', 'able', 'about', 'above', 'according', 'accordingly', 'across', 
    'actually', 'after', 'afterwards', 'again', 
    'against', # Seems to be a key word to omit
    'ain\'t', 'all', 
    'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 
    'always', 'am', 'among', 'amongst', 'an', 'and', 'another', '