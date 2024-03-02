
import re

_COUNTRIES = ['new york', 'australia', 'greece', 'california' ]

_RE_LOCATION = re.compile(r'<LOCATION>\s*?(.*?)\s*?</LOCATION>')

if False:
    text = '<em><ORGANIZATION>Stanford</ORGANIZATION>, <LOCATION>California</LOCATION></em>,'
    matches = _RE_LOCATION.finditer(text)
    print [m.group(1) for m in matches]
    exit()
    
_RE_MARKUP = re.compile(r'<.*?>')
    
def clean_markup(text): 
    cleaned = _RE_MARKUP.sub('', text)
    #print 'clean_markup(%s) = "%s"' % (text, cleaned)
    return cleaned

def get_locations(data):
    #print type(query)