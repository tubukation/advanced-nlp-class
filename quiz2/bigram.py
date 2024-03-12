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
    
def get_bigrams(text):
    def get_line_bigrams(line):
        tokens = tokenize(line)
        return [B(tokens[i-1:i+1]) for i in range(1,len(tokens))]

    lines = get_lines(text)
    return sum([get_line_bigrams(ln) for ln in lines], []) 

def get_counts_dict(alist):
    counts = {}
    for t in alist:
        counts[t] = counts.get(t, 0) + 1
    return counts 

def get_count(counts_dict, key):  
    return counts_dict.get(key, 0)

def header(name):
    print '-- %s %s' % (name, '-' * (76 - len(name)))
    
def show_dict(d, name):
    header('%s: keys=%d, vals=%d' % (name, len(d), sum(d.values())))
    for k in sorted(d.keys(), key = lambda k: (-d[k], d)):
        print '%20s : %s' % (k, d[k])

#
# Code execution starts here
#        
text = '''    
    <s> I am Sa