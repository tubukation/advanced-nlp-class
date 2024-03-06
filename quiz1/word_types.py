import re

_RE_TOKEN = re.compile('[^a-zA-Z]+')

def tokenize(text):
