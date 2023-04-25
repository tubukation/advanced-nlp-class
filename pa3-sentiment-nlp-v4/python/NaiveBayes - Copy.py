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
    'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 
    'further', 'furthermore', 'g', 'get', 'gets', 'getting', 'given', 'gives', 
    'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'h', 'had', 
    #'hadn\'t', 
    'happens', 'hardly', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 
    'he', 'he\'s', 'hello', 'help', 'hence', 'her', 'here', 'here\'s', 'hereafter', 
    'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 
    'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'i', 'i\'d', 
    'i\'ll', 'i\'m', 'i\'ve', 'ie', 'if', 
    #'ignored', 
    'immediate', 'in', 'inasmuch', 
    'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 
    'instead', 'into', 'inward', 'is', 
    #'isn\'t',
    'it', 'it\'d', 'it\'ll', 'it\'s', 
    'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'known', 
    'knows', 'l', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 
    'lest', 'let', 'let\'s', 'like', 
    #'liked',
    'likely', 'little', 'look', 
    'looking', 'looks', 'ltd', 'm', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 
    'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 
    'must', 'my', 'myself', 'n', 'name', 'namely', 'nd', 'near', 'nearly', 
    'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 
    'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 
    #'not', 
    'nothing', 'novel', 'now', 'nowhere', 'o', 'obviously', 'of', 'off', 
    'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 
    'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 
    'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'p', 'particular', 
    'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 
    'presumably', 'probably', 'provides', 'q', 'que', 'quite', 'qv', 'r', 'rather', 
    'rd', 're',