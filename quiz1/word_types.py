import re

_RE_TOKEN = re.compile('[^a-zA-Z]+')

def tokenize(text):
    "Tokenize text by splitting on non-alphabetic characters"
    return [x for x in _RE_TOKEN.split(text) if x]
      
def get_variants(types): 
    """types is a set of words
        Returns dict of types that differ only in case
            key = lowercase variant of a word
            value = all case variants of key in types
    """
    case_variations = {}
    f