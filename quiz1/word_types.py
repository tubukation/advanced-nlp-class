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
    for w in types:
        case_variations[w.lower()] = case_variations.get(w.lower(), set([])) | set([w])
    return dict([(k,v) for (k,v) in case_variations.items() if len(v) > 1])   

if __name__ == '__main__':
    import sys

    # Read text from file
    text = file(sys.argv[1], 'rt').read()
   
    #
    # Compute tokens, types, types without case variations, case variants and coun