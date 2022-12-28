import sys
import SpamLord

def get_personal_info(path):
    data = file(path, 'rt').read()
    result = SpamLord.extract_personal_info(path, data)
    print result
    uniques = dict([(e[2].strip('\n'), (e[0]