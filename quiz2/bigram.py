from __future__ import division

import re

_RE_TOKEN = re.compile(r'\s')

def tokenize(text):
    "Tokenize text by splitting on spaces"
    return [x for x in _RE_TOKEN.split(text) if x]

def get_lines(text):
    lines = [ln.strip() for ln in text.split('\n')]
    return [ln for ln in lines if ln]

def B(words):
    """Convert an N-gram to text. Safe because input text was tokenized on space"""
    return ' '.join(words)    
    
def