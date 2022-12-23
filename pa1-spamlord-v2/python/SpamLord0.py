
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
