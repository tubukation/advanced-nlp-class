
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

        def __init__(self):
            self.in_info_box = False
            self.name = None
            self.spouse = None
            self.spouse_dict = {}
            
        def process(self, line):
            if not self.in_info_box:
                if '{{Infobox' in line:
                    self.in_info_box = True
                    self.name = None
                    self.spouse = None
            else:
                m = _RE_INFO_BOX_NAME.search(line)
                if m:    
                    self.name = m.group(1)
                m = _RE_INFO_BOX_WIFE.search(line)
                if not m:
                     m = _RE_INFO_BOX_WIFE2.search(line)
                if m:
                    self.spouse = m.group(1).strip()
                    self.spouse = ' '.join(self.spouse.split())
                if line.startswith('}}'):
                    in_info_box = False
                    if name and spouse:
                        self.spouse_dict[self.name] = self.spouse

def parse_infobox(f):
    """Generator for extracting info box fields from f which is a text file, hence
        a generator of text lines
    """
    in_info_box = False

    for i,line in enumerate(f):
        if not in_info_box:
            if '{{Infobox' in line:
                in_info_box = True
                name = None
                wife = None
                #print i, 'start info box'
                continue
        else:
            if line.startswith('}}'):
                in_info_box = False
                #print i, ' end info box', name, wife
                if name and wife:
                    yield (name, wife)
            #print '     ', line,
            line = convert_unicode(line)
            line = _RE_QUOTES.sub('', line)
            m = _RE_INFO_BOX_NAME.search(line)
            if m:
                name = m.group(1)
                #print i, ' wife=', wife, '---',  m.group(0),
                continue
            m = _RE_INFO_BOX_WIFE.search(line)
            if not m:
                m = _RE_INFO_BOX_WIFE2.search(line)
            if m:
                wife = m.group(1).strip()
                wife = ' '.join(wife.split())
                print i, ' wife="%s" --- %s' % (wife, m.group(0))
                continue
            

_RE_CASE_TITLE = re.compile(r'^[A-Z][a-z]+$')
def is_title(word):
    title = bool(_RE_CASE_TITLE.search(word)) and (word.lower() not in _NOT_PERSONS) 
    #if word == 'Pennsylvania':
    #    print title, word
    #    exit()
    return title
   


if False:   
    _stop_words = file('stop.words', 'rt').read()  
    _STOP_WORDS_LIST = ' '.join(_stop_words.split('\n')).split()
    _STOP_WORDS_LIST = set([w.strip() for w in _STOP_WORDS_LIST if w.strip()])
else:
    _STOP_WORDS_LIST = set(['secondly', 'all', 'consider', 'whoever', 'results', 'four', 'edu', 'go', 'causes', 'seemed', 'rd', 'certainly', "when's", 'vs', 'ts', 'to', 'does', 'present', 'th', 'under', 'sorry', 'promptly', "a's", 'mug', 'sent', 'outside', 'very', 'mg', 'every', 'yourselves', "we'll", 'went', 'did', 'forth', "they've", 'try', 'p', 'shows', 'noted', 'added', "it'll", "i'll", 'says', "you'd", 'd', 'past', 'likely', 'invention', 'further', 'even', 'index', 'what', 'appear', 'giving', 'section', 'brief', 'above', 'sup', 'new', 'poorly', 'ever', "c'mon", 'whose', 'youd', 'respectively', 'never', 'here', 'let', 'others', 'hers', 'along', "aren't", 'suggest', 'obtained', 'ref', 'k', 'allows', 'proud', "i'd", 'resulting', "weren't", 'usually', 'whereupon', "i'm", 'changes', 'thats', 'hither', 'via', 'followed', 'merely', 'put', 'ninety', 'vols', 'viz', 'ord', 'readily', 'everybody', 'use', 'from', 'would', 'contains', 'two', 'next', 'few', 'therefore', 'taken', 'themselves', 'thru', 'until', 'more', 'knows', 'mr', 'becomes', 'hereby', 'it', "ain't", 'particular', 'known', "who'll", 'must', 'me', 'none', 'f', 'this', 'ml', 'oh', 'anywhere', 'nine', 'can', 'theirs', 'following', 'my', 'example', 'indicated', 'give', "didn't", 'near', 'indicates', 'something', 'want', 'arise', 'information', 'needs', 'end', 'rather', 'ie', 'meanwhile', 'makes', 'how', 'instead', 'okay', 'tried', 'may', 'stop', 'after', 'eighty', 'different', 'hereupon', 'ff', 'date', 'such', 'a', 'thered', 'third', 'whenever', 'maybe', 'appreciate', 'q', 'ones', 'so', 'specifying', 'allow', 'keeps', "that's", 'six', 'help', "don't", 'indeed', 'over', 'mainly', 'soon', 'course', 'through', 'looks', 'still', 'its', 'refs', 'before', 'thank', "he's", 'selves', 'inward', 'fix', 'actually', "he'd", 'whether', 'willing', 'thanx', 'ours', 'might', "haven't", 'then', 'them', 'someone', 'somebody', 'thereby', 'auth', "you've", 'they', 'not', 'awfully', 'nor', 'nos', 'several', 'hereafter', 'always', 'reasonably', 'whither', 'l', 'sufficiently', 'each', 'found', 'entirely', "mustn't", "isn't", 'mean', 'everyone', 'significantly', 'doing', 'ed', 'eg', 'related', 'tip', 'owing', 'ex', 'substantially', 'et', 'beyond', 'couldnt', 'out', 'shown', 'furthermore', 'since', 'research', 'looking', 're', 'seriously', "shouldn't", "they'll", 'got', 'cause', 'thereupon', "doesn't", 'million', 'little', 'quite', "what'll", 'que', 'besides', 'x', 'ask', 'anyhow', 'beginning', 'g', 'could', 'similarly', 'tries', 'keep', 'w', 'ltd', 'hence', 'onto', 'think', 'first', 'already', 'seeming', 'omitted', 'thereafter', 'thereof', 'yourself', 'done', 'approximately', 'another', 'miss', "you're", 'given', 'necessarily', 'indicate', 'together', 'accordingly', 'least', 'name', 'anyone', 'their', 'too', 'hundred', 'gives', 'mostly', 'that', 'exactly', 'took', 'immediate', 'regards', 'somewhat', 'off', 'believe', 'herself', 'than', "here's", 'begins', 'b', 'unfortunately', 'showed', 'accordance', 'gotten', 'second', 'nevertheless', 'r', 'were', 'toward', 'anyways', 'and', 'youre', 'ran', 'thoughh', 'beforehand', 'say', 'unlikely', 'have', 'need', 'seen', 'seem', 'saw', 'any', 'relatively', 'zero', 'thoroughly', 'latter', 'able', 'aside', 'thorough', 'predominantly', 'also', 'take', 'which', 'begin', 'nobody', 'unless', 'shall', 'who', "where's", 'most', 'eight', 'amongst', 'significant', 'nothing', 'why', 'sub', 'kg', 'especially', 'noone', 'later', 'm', 'km', 'mrs', 'heres', "you'll", 'definitely', 'normally', 'came', 'saying', 'particularly', 'show', 'anyway', 'ending', "that'll", 'fifth', 'one', 'specifically', 'behind', 'should', 'only', 'going', 'specify', 'announce', 'itd', "there've", 'do', 'his', 'goes', 'get', 'hopefully', 'overall', 'truly', "they'd", 'cannot', 'hid', 'nearly', 'words', 'despite', 'during', 'him', 'regarding', 'qv', 'h', 'twice', 'she', 'contain', "won't", 'where', 'thanks', 'ignored', "hasn't", 'namely', 'sec', 'are', "that've", 'throug', 'best', 'wonder', 'said', 'away', 'currently', 'please', 'ups', 'enough', "there's", 'various', 'between', 'affecting', 'probably', 'neither', 'across', 'available', 'we', 'recently', 'useful', 'importance', 'however', 'meantime', 'come', 'both', 'c', 'last', 'thou', 'many', "wouldn't", 'thence', 'according', 'against', 'etc', 's', 'became', 'com', 'comes', 'otherwise', 'among', 'liked', 'co', 'afterwards', 'seems', 'ca', 'whatever', "hadn't", 'non', "couldn't", 'moreover', 'throughout', 'considering', 'better', 'pp', 'described', "it's", 'three', 'been', 'quickly', 'whom', 'much', 'wherein', 'ah', 'whod', 'hardly', "it'd", 'wants', 'corresponding', 'latterly', "what's", 'else', 'former', 'those', 'myself', 'novel', 'look', 'unlike', 'these', 'means', 'nd', 'thereto', 'value', 'n', 'will', 'while', 'taking', 'theres', 'seven', 'whereafter', 'almost', 'wherever', 'is', 'thus', 'herein', 'cant', 'itself', 'im', 'in', 'affected', 'alone', 'id', 'if', 'containing', 'anymore', 'perhaps', 'insofar', 'make', 'same', 'clearly', 'beside', 'potentially', 'widely', 'gets', 'howbeit', 'used', 'slightly', 'see', 'somewhere', 'upon', 'effect', 'uses', "he'll", 'wheres', 'recent', 'kept', 'whereby', 'largely', 'i', 'whole', 'nonetheless', 'well', 'anybody', 'obviously', 'without', "can't", 'y', 'the', 'yours', 'lest', 'world', "she'll", 'just', 'less', 'being', 'downwards', 'therere', 'presumably', 'greetings', 'immediately', 'regardless', 'yes', 'yet', 'unto', 'now', 'wed', "we've", 'had', 'except', 'thousand', 'lets', 'has', 'adj', 'ought', 'gave', "t's", 'arent', 'around', "who's", 'possible', 'usefully', 'possibly', 'five', 'know', 'using', 'part', 'apart', 'abst', 'nay', 'necessary', 'like', 'follows', 'theyre', 'serious', 'either', 'become', 'page', 'towards', 'therein', "why's", 'shed', 'because', 'old', 'often', 'successfully', 'some', 'somehow', 'self', 'sure', 'shes', 'specified', 'home', "'ve", 'ourselves', "shan't", 'happens', 'vol', "there'll", 'for', 'affects', 'though', 'per', 'everything', 'asking', 'provides', 'tends', 't', 'be', 'run', 'sensible', 'obtain', 'nowhere', 'although', 'by', 'on', 'about', 'ok', 'anything', 'getting', 'of', 'v', 'o', 'whomever', 'whence', 'plus', 'act', 'consequently', 'or', 'seeing', 'own', 'whats', 'formerly', 'previously', 'somethan', 'into', 'within', 'www', 'due', 'down', 'appropriate', 'right', 'primarily', 'theyd', "c's", 'whos', 'your', "how's", 'her', 'hes', 'aren', 'apparently', 'there', 'biol', 'pages', 'hed', 'inasmuch', 'inner', 'way', 'resulted', 'was', 'himself', 'elsewhere', "i've", 'becoming', 'but', 'back', 'hi', 'et-al', 'line', 'trying', 'with', 'he', 'usefulness', "they're", 'made', "wasn't", 'wish', 'j', 'up', 'us', 'tell', 'placed', 'below', 'un', 'whim', 'z', 'similar', "we'd", 'strongly', 'gone', 'sometimes', 'associated', 'certain', 'am', 'an', 'as', 'sometime', 'at', 'our', 'inc', 'again', "'ll", 'no', 'na', 'whereas', 'when', 'lately', 'til', 'other', 'you', 'really', 'concerning', 'showns', 'briefly', 'beginnings', 'welcome', "let's", 'important', "she's", 'e', "she'd", 'having', 'u', "we're", 'far', 'everywhere', 'hello', 'once'])


def is_stop_word(w):
   return w.lower() in _STOP_WORDS_LIST
    
def decode_text(text):
    words = text.split()
    words = [w for w in words if not is_stop_word(w)]
    persons = []

    is_virginia = 'Virginia' in text
    #is_virginia = False
    # First extract the person from [[person|other name]]
    start = end = -1
    for i,w in enumerate(words):
        if w[:2] == '[[':
            start = i
            w = words[i] = w[2:]
        if w[:7] == '{{main|':
            start = i
            w = words[i] = w[7:]
            #print '~~', w, words[i]
        if start >= 0:    
            if '|' in w:
                end = i+1
                words[i] = w.split('|')[0]
            elif w[-2:] == ']]' or w[-2:] == '}}':
                end = i+1
                words[i] = w[:-2]
        if start >= 0 and end >= 0:
            #if is_virginia: print '@@', start, end, words[start:end]; 
            #if is_virginia: print all([is_title(v) for v in words[start:end]]) 
            if all([is_title(v) for v in words[start:end]]) and end > start +1:
                persons.append((start,end))
            #if is_virginia: exit()
            start = end = -1
    
    # Remove the [[ and ]]
    if False:
        for start,end in persons:
            #print words[end-1], 
            words[start] = words[start][2:]
            words[end-1] = words[end-1][:-2]
            #print '=>', words[end-1] 

    if is_virginia:
        print persons
        #exit()
    return words,persons

def get_person_in_range(persons, i0, i1, words):
    """Persons is a list of (start,end) tuples sorted by start
        Return person such that i0 <= start < end <= i1
    """
    #print 'get_person_in_range(%d, %d)' % (i0, i1)
    
    # First try the [[]] fields
    for start,end in persons:
        #if start > i1:       return -1, -1
        if i0 <= start and end <= i1:
            #print '$%$', start, end
            return start,end, 1
            
    do_show = True
    
    
    # Next 2 consecutive title case words    
    matches = []
    last_was_title = False
    if i1 >= i0:
        j0 = i0 + 1
        j1 = i1
        delta = 1
    else:
        j0 = i0 
        j1 = i1 -1
        delta = -1
    #print '&&', j0, j1, delta    
    for j in range(j0,j1,delta):
        this_is_title = is_title(words[j])
        #if do_show:  print words[j], this_is_title
        if last_was_title and this_is_title:
            return j-1, j+1, 2 # if not_person(words[j-1:j+1]) else 10 
        last_was_title = this_is_title
    return -1, -1, 3 

def get_spouses(text):
    words,persons = decode_text(text)
    n = len(words)
    #print words
    #print '-' * 80, n
    
    do_test = 'Clemm' in text
    do_test = False
    if do_test: print '$$$$', text; 
    
    spouses = []
    def get_person(i0, i1):
        #if do_test: print 'get_person(%d, %d) %s' % (i0, i1, words[min(i0,i1):max(i0,i1) ])
        start,end,rank = get_person_in_range(persons, i0, i1, words)
        if start < 0: return None, 100
        if not all(is_title(w) for w in words[start:end]): return None, 100
        result = ' '.join(words[start:end]) if start >= 0 else None
        #if do_test: print '>>>', words[i0:i1], start, end, result 
        return result,rank

    for i,w in enumerate(words):
        if w.lower() == 'married' or w.lower() == 'marriage':
            if do_test: print '$$', i, w
            spouse,rank = get_person(i, max(0,i-6))
            if spouse:
                spouses.append((spouse,rank))
            spouse,rank = get_person(i, min(i+7,n))
            if spouse:
                spouses.append((spouse,rank)) 
    if do_test: 