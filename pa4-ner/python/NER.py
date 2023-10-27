import sys, os
from subprocess import Popen, PIPE
from FeatureFactory import FeatureFactory

"""
    Do not modify this class
    The submit script does not use this class 
    It directly calls the methods of FeatureFactory and MEMM classes.
"""
def main(argv):
    if len(argv) < 2:
        print 'USAGE: python NER.py 