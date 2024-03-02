
import sys, traceback, re, collections
from pprint import pprint

_NOT_PERSONS = set(['city', 'harbor', 'river', 'county', 'hotel', 'prize', 
    'married', 'returning', 'pennsylvania', 'baltimore', 'reinstated']) 
def not_person(words):
    np = all(w.lower() not in _NOT_PERSONS for w in words)
    print '^^', np, words
    return np

_RE_START_INFO_BOX = re.compile(r'\{\{Infobox')
_RE_END_INFO_BOX = re.compile(r'\}\}')
_RE_INFO_BOX_NAME = re.compile(r'\|name\s*=\s*(\S.+\S)\s*$')
_RE_INFO_BOX_WIFE = re.compile(r'\|spouse\s*=.*\[\[(.+)\]\]')

# |spouse = Janice Goldfinger (1970-)
_RE_INFO_BOX_WIFE2 = re.compile(r'\|spouse\s*=\s*([A-Za-z\s]+)\s*?\(')

if False:
    line = '|spouse = Janice Goldfinger (1970-)'
    line = '|spouse        = Susann Margreth Branco (February 6, 1988 &amp;ndash; December 1994 annulled 1997)&lt;br&gt;Elizabeth &quot;Liz&quot; Watson (January 10, 1998 &amp;ndash;)&lt;br&gt;Kimberly Bell|'
    print line
    m = _RE_INFO_BOX_WIFE2.search(line)
    print '= "%s"' % m.group(1)
    exit()


# Partial map of HTML unicode symbols
# http://blog.stevenlevithan.com/archives/multi-replace
# http://scribble-count.com/Ref/ASCII.htm
_UNICODE_MAP = { 
    'lt'    : '<',
    'gt'    : '>',
    'amp'   : '&',
    'nbsp'  : ' ',
    'quot'  : '"',
    'ldquo' : '"',
    'rdquo' : '"',
    'lsquo' : "'",
    'rsquo' : "'",
    'middot': chr(183),
    'hellip': '...',
    'mdash' : '-',
    'ndash' : '-',
}

# Add the HTML unicode numerical codes
# http://www.fileformat.info/info/unicode/char/40/index.htm
_UNICODE_PATTERNS = _UNICODE_MAP.keys() + ['#x[\da-f]{2,4}', '#\d{2,4}']

# Combine all the uncicode codes into regex
# We don't need to be comprehensive about this as long as we get @, -, and .
_RE_UNICODE = re.compile(r'&(%s);' % '|'.join(_UNICODE_PATTERNS)) 

# Catch all the unicode codes we missed
_RE_UNICODE_CATCH_ALL = re.compile(r'&[a-z]{2-6};')   

def convert_unicode(line):
    """Replace all Unicode &(%s); codes with their values"""
    def replacer(m):
        p = m.group(1)
        if p in _UNICODE_MAP.keys(): 
            return _UNICODE_MAP[p]
        else:
            n = int(p[2:], 16) if p[1] == 'x' else int(p[1:])
            return chr(n) if n <= 255 else ' '

    line = _RE_UNICODE.sub(replacer, line) 
    return _RE_UNICODE_CATCH_ALL.sub(' ', line) 
    
# HTML markup
_RE_MARKUP = re.compile(r'<.*?>')     

# Wiki parentheses
_RE_PARENTHESES = re.compile(r'\(.+?\)')     

_RE_QUOTES = re.compile(r'".+?"')   
  
def preprocess(line): 
    """Preprocessing that is applied to all text. 
        Convert to lower case, replace unicode characters and strip 
        HTML markup
        
             See http://studentaffairs.stanford.edu/resed/directory
    """
    #line = line.lower()
    line = convert_unicode(line)
    line = _RE_MARKUP.sub('', line)
    line = _RE_PARENTHESES.sub('', line)
    # Periods are word boundaries
    line = line.replace('.', ' ')
    line = line.replace(',', ' ')
    line = line.replace('=', ' ')
    return line

if False:
    m = _RE_START_INFO_BOX.search('<text xml:space="preserve">{{Infobox Governor')
    print m.group(0)
    m = _RE_END_INFO_BOX.search('}}')
    print m.group(0)
    m = _RE_INFO_BOX_NAME.search('|name         = Arnold Schwarzenegger')
    print m.group(0)
    m = _RE_INFO_BOX_WIFE.search('|spouse       = {{nowrap|[[Maria Shriver]] (1986&amp;ndash;present)}}')
    print m.group(0)
    exit()
    
    class InfoBox:
