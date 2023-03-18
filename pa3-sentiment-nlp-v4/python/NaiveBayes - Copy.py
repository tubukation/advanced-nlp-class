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
import re

_PUNCTUATION = set([';', '.', ',', '"', '(', ')', '&', ':', '?', '[', ']'])

def _N(word):
    return 'NOT_' + word

_NEGATIVES = set([
    'not', 'cannot', 'wont',
    'no', 
    'never', 
    'cant', 
    #'against','although',
    ])    
_ENGLISH_STOP_WORDS = set([ 
    'a', 'a\'s', 'able', 'about', 'above', 'according', 'accordingly', 'across', 
    'actually', 'after', 'afterwards', 'again', 
    'against', # Seems to be a key word to omit
    'ain\'t', 'all', 
    'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 
    'although', 
    'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 
    'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 
    'appear', 
    #'appreciate', 
    'appropriate', 'are', 
    #'aren\'t', 
    'around', 'as', 
    'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 
    'b', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 
    'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 
    'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 
    'c', 
    #'c\'mon', 
    'c\'s', 'came', 'can', 'can\'t', 'cannot', 'cant', 'cause', 
    'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 
    'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 
    'containing', 'contains', 'corresponding', 'could', 'couldn\'t', 'course', 
    'currently', 'd', 'definitely', 'described', 'despite', 'did', 
    #'didn\'t', 
    'different', 'do', 'does',
    #'doesn\'t', 'doing', 
    #'don\'t', 
    'done', 'down', 
    #'downwards', 
    'during', 'e', 'each', 'edu', 'eg', 'eight', 'either', 'else', 
    'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 
    'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 
    'example', 
    #'except', 
    'f', 'far', 'few', 'fifth', 'first', 'five', 'followed', 
    'following', 'follows', 'for', 'fo