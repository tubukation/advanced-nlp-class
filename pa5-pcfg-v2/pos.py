import re, sys

text = file('Vocab.gr', 'rt').read()

def get_pos(word):
    pattern = r'\d+\s+(\w+)\s+%s' % word
    return [m.group(1) for m