
import sys
import os
import re
import pprint

#my_first_pat = r'(\w+)\s*(?:@| at | where )\s*(\w+(?:\.w+)*)\s*(?:\.| dom | dot )\s*edu'

_RE_PARAMS = re.compile('__(\w+)__')

def _make_patttern(base_pattern, params_dict):
    """Replace the '__key__' tokens in base_pattern with params_dict[key].
        This is used for parametrized regex patterns
    """
    return _RE_PARAMS.sub(lambda m: params_dict[m.group(1)], base_pattern)  

_PATTERN_EMAIL = r'''
    __PATTERN__
    (\w+(?:__DOT__\w+)*)            # Name
    \s*                             # Optional space
    (?:@|\sat\s|\swhere\s)          # Separator Not needed so much with pre-processing
    \s*                             # Optional space
    (\w+(?:__DOT__\w+)*)           # Domain prefix  \. => (?:\.|\sdom\s|\sdo?t\s) ??
    \s*                             # Optional space
    __DOT__                         # Separator  Not needed so much with pre-processing
    \s*                             # Optional space
    ((?:edu|com|org|gov)(?:__DOT__\w{2-3})?)    # Ends in 'edu', 'com' etc with optional country
    (?:\W|$)                        # Make sure this is the end
    ''' 
    
_PATTERN_EMAIL0 = _make_patttern(_PATTERN_EMAIL, {'PATTERN': '', 'DOT': '(?:\.|\sdom\s|\sdo?t\s)'})     
if True:
    print _PATTERN_EMAIL0
    #exit()
    
regex_email0 = re.compile(r'''
    (\w+(?:\.\w+)*)         # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:\.\w+)*)         # Domain prefix  \. => (?:\.|\sdom\s|\sdo?t\s) ??
    \s*                     # Optional space
    (?:\.|\sdom\s|\sdo?t\s)  # Separator  Not needed so much with pre-processing
    \s*                     # Optional space
    ((?:edu|com|org|gov)(?:\.w{2-3})?)    # Ends in 'edu', 'com' etc with optional country
    (?:\W|$)                # Make sure this is the end
    ''', 
    re.VERBOSE | re.IGNORECASE)
    
regex_email0 = re.compile(r'''
    (email\s*(?:to)?\*s:?\s*)?
    (\w+(?:(?(1)[\.\s]|\.)\w+)*)        # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:(?(1)[\.\s]|\.)\w+)*)         # Domain prefix Allow sepators if there is email: prefix
    \s*                     # Optional space
    \.?                     # Optional .    
    \s*                     # Optional space
    ((?:edu|com|org|gov|mil|net|info)(?:\.w{2})?)    # Ends in 'edu', 'com' etc with optional country
                            # See http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains    
    (?:\W|$)                # Make sure this is the end
    ''', 
    re.VERBOSE | re.IGNORECASE)    
    
if False:    
    regex_email1 = re.compile(r'''
        (\w+(?:\.\w+)*)         # Name
        \s*                     # Optional space
        (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
        \s*                     # Optional space
        (?:
            (\w+(?:\.\w+)*)         # Domain prefix
            \s*                     # Optional space
            (?:\.|\sdom\s|\sdo?t\s)  # Separator  Not needed so much with pre-processing
            \s*                     # Optional space
            (edu|com)            # Ends in 'edu', 'com' etc
        |
            (stanford)\s+(edu) # <= Why does this not work?
        )
        ''', 
        re.VERBOSE | re.IGNORECASE)  

regex_email2 = re.compile(r'''
    email\s*:?\s*
    (\w+(?:\.\w+)*)         # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:\s+\w+)*)         # Domain prefix
    \s*                     # Optional space
    (?:\.|\sdom\s|\sdo?t\s|\s)  # Separator  Not needed so much with pre-processing
    \s*                     # Optional space
    (edu|com)            # Ends in 'edu', 'com' etc
    ''', 
    re.VERBOSE | re.IGNORECASE)     

#regex_email = re.compile(r'(\w+\.\w+)') 
regex_email = regex_email0  
    
if False:    
    line = r'<dt>Professor David Cheriton <A href="mailto:cheriton@cs.stanford.edu">cheriton at cs.stanford.edu</A>'
    #line = r'cheriton@cs.stanford.edu'
    line = r'd-l-w-h-@-s-t-a-n-f-o-r-d-.-e-d-u'
    line = line.replace('-', '')
    print line
    #line = r'dlw-h@stanford.edu'
    matches = regex_email.findall(line)
    print matches
    exit()    
    
if False:
    line = r'em>ada&#x40;graphics.stanford.edu</em>'
    print line
    line = line.replace(r'&#x40;', '@') #
    print line
    matches = regex_email.findall(line)
    print matches
    exit()
    
if False:
    line = r"email: pal at cs stanford edu, but I receive more email than I can handle. Please don't be offended if I don't reply."
    print line
    matches = regex_email2.findall(line)
    print matches
    exit()
    
# obfuscate('stanford.edu','jurafsky'); 
regex_obfuscate = re.compile(r"obfuscate\('(.*)','(.*)'\)", re.IGNORECASE)
    
name_exclusions = ['server', 'www', 'ftp', 'http', 'name']  

def deobfuscate(line):
    m = regex_obfuscate.search(line)
    if not m:
        return line
    g = m.groups()
    if False:
        print line[:-1]
        print g
        exit()
     
    return '%s@%s' % (g[1], g[0])     

#import urllib
#import xml.sax.saxutils

RE_UNICODE = re.compile(r'&#(x[0-9a-f]{2,4}|\d{2,4});', re.IGNORECASE)

if False:
    m = RE_UNICIODE.search(r'&#x40;stanford.edu</em>')
    print m
    if m:
        print m.groups()
    exit()

# FIXME: Combine all the re.sub() !@#$    
    
def preprocess_unicode(line):
    def replacer(m):
        number = m.group(1)
        if number.lower()[0] == 'x':
            n = int(number[1:], 16)
        else:
            n = int(number)
        if n > 255:
            return ' ' # Cannot handle non-ASCII characters
        return chr(n)
        
    return RE_UNICODE.sub(replacer, line) 

CODES_MAP = { 
    'lt'    : '<',
    'gt'    : '>',
    'amp'   : '&',
    'nbsp'  : ' ',
    'quot'  : '"',
    'ldquo' : '"',
    'rdquo' : '"',
    'lsquo' : "'",
    'rsquo' : "'",
    'hellip': '...',
    'mdash' : '-',
    'ndash' : '-',
}
PATTERN_CODES = r'&(' + '|'.join(CODES_MAP.keys()) + ');'
RE_SPECIAL_CODES = re.compile(PATTERN_CODES, re.IGNORECASE) 

def preprocess_special_codes(line):
    def replacer(m):
        return CODES_MAP[m.group(1)]
        
    return RE_SPECIAL_CODES.sub(replacer, line)     

def preprocess(line):
    if False:
        line = line.replace(r'&#x40;', '@') # levoy: <em>ada&#x40;graphics.stanford.edu</em>
        line = line.replace('&lt;', '<').replace('&gt;', '>')
        line = line.replace('&ldquo;', '"').replace('&rdquo;', '"')  # seen in ouster
        return line
    else: 
                        
        #line2 = xml.sax.saxutils.unescape(line) 
        line2 = line
        line3 = preprocess_unicode(line2)        
        if False:
            if line3 != line2:
                print line2
                print line3
                exit()
        line2 = line3
        line2 = preprocess_special_codes(line2) # Picks up a few left by xml.sax.saxutils.unescape()
        #line2 = line2.replace('&ldquo;', '"').replace('&rdquo;', '"')  # seen in ouster
        #line2 = line2.replace(r'&#x40;', '@') # levoy: <em>ada&#x40;graphics.stanford.edu</em>
        if '&ldquo;'  in line2 or '&lt;' in line2 or '&#x40;'  in line2:
            print '=' * 80
            print line
            print line2
            exit()
        return line2    

RE_AT = re.compile(r'\s(?:at|where)\s', re.IGNORECASE)
RE_DOT = re.compile(r'\s(?:do?t|dom)\s', re.IGNORECASE)
        
def get_emails(line):
    emails_found = []
    
    line = line.lower()
    
    # This line must come first so that other lines do not change &#x40;'
    line = preprocess(line)
   
     # Handle separately
    line = deobfuscate(line)
    
    line = line.replace('-', '') # dwf
    line = line.replace('(', '').replace(')', '') # ouster
    line = line.replace('"', '').replace('followed by', '') # ouster
    
    line = RE_AT.sub('@', line)
    line = RE_DOT.sub('.', line)
         
    #line = line.replace(' at ', '@')
    #line = line.replace(' dot ', '.')
    #line = line.replace(' dt ', '.')   # ullman
    
    line = line.replace(';', '.')  # jks Gives false +ve on manning if no '&lt;' => '<' above
    
    matches = regex_email.findall(line)
    if False:
        if not matches:
            matches = regex_email2.findall(line)
            if matches:
                #print 'before:', matches
                matches = [tuple([re.sub('\s+', '.', x) for x in m]) for m in matches]
                #print 'after: ', matches