word_text = '''1	JJ	bloody
1	JJ	weary
1	JJ	unable
1	JJ	trusty
1	JJ	further
1	JJ	sacred
1	JJ	tropical
1	JJ	indigenous
1	JJ	temperate
1	JJ	hot
1	JJ	lucky
1	JJ	simple
1	JJ	tiny
1	JJ	hard	
1	JJ	sensational
1	JJ	comparable
1	JJ	angolian
1	JJ	yellow
1	JJ	plodding
'''

import re
RE_JJ = re.compile(r'JJ\s+(\w+)')
def get_jj(line):
	return RE_JJ.search(line).group(1)

def get_lines(text):
	return [ln.strip() for ln in text.split('\n') if ln.str