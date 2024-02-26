import collections
import copy
import optparse
import os

import ling.Tree as Tree
import ling.Trees as Trees
import pennParser.EnglishPennTreebankParseEvaluator as EnglishPennTreebankParseEvaluator
import io.PennTreebankReader as PennTreebankReader
import io.MASCTreebankReader as MASCTreebankReader

from PCFGParserTester import *

if __name__ == '__main__':
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--path', dest='path', default='../data/parser')
    opt_parser.add_option('--maxLength', dest='max_length', default='20')
    opt_parser.add_option('--testData', dest='test_data', default='')

    options, args = opt_parser.parse_args()
    options = vars(options)

    print '