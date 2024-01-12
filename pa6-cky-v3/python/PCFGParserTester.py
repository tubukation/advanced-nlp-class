
import collections
import copy
import optparse

from ling.Tree import Tree
import ling.Trees as Trees
import pennParser.EnglishPennTreebankParseEvaluator as EnglishPennTreebankParseEvaluator
import io.PennTreebankReader as PennTreebankReader
import io.MASCTreebankReader as MASCTreebankReader


import logging
logging.basicConfig(#filename='test2.log', 
        level=logging.ERROR, 
        format='%(asctime)s [%(levelname)s] %(message)s')

_VERBOSE = False
if _VERBOSE:
    def P(x): print '> %s' % x
    
    def PP(x, indent=4): 
        """Pretty print x"""
        import pprint
        pp = pprint.PrettyPrinter(indent=indent)
        pp.pprint(x)

    def D(dct): 
        """Convert keys and values of dct strings recursively"""
        if isinstance(dct, dict):    return dict([(str(k),D(dct[k])) for k in dct])
        elif isinstance(dct, list):  return [D(x) for x in dct]
        elif isinstance(dct, tuple): return tuple([D(x) for x in dct])    
        return str(dct)   

    def print_chart(chart, name, indent=4):
        """Print a CKY chart"""
        print '-' * 80
        print name
        for span in range(len(chart) - 1, 0, -1):
            for begin in range(len(chart) - span):
                end = begin + span
                print '%2d,%2d:' % (begin,end)
                PP(D(chart[begin][end]), indent * (len(chart) - span)) 

class Parser:
    """(Effectively abstract) base class"""

    def train(self, train_trees):
        pass

    def get_best_parse(self, sentence):
        """
            Should return a Tree
        """
        pass

class PCFGParser(Parser):

    def train(self, train_trees):
        # TODO: before you generate your grammar, the training
        #       trees need to be binarized so that rules are at
        #       most binary

        annotated_trees = [TreeAnnotations.annotate_tree(tree) for tree in train_trees]
        self.lexicon = Lexicon(annotated_trees)
        self.grammar = Grammar(annotated_trees)

        if False:
            print 'trees'
            for tree in annotated_trees: print tree
            print 'lexicon'
            lex = dict(((k,dict(v)) for k,v in self.lexicon.word_to_tag_counters.items())) 
            PP(lex)
            print 'grammar' 
            PP(self.grammar)
            #exit()

    def get_best_parse(self, sentence):
        """
            Should return a Tree.
            'sentence' is a list of strings (words) that form a sentence.
            
            function CKY(words, grammar) returns [most_probable_parse,prob] 
              score = new double[#(words)+1][#(words)+1][#(nonterms)] 
              back = new Pair[#(words)+1][#(words)+1][#nonterms]] 
              for i=0; i<#(words); i++ 
                for A in nonterms
                  if A -> words[i] in grammar 
                    score[i][i+1][A] = P(A -> words[i]) 
                //handle unaries
                boolean added = true 
                while added  
                  added = false 
                  for A, B in nonterms
                    if score[i][i+1][B] > 0 && A->B in grammar 
                      prob = P(A->B)*score[i][i+1][B] 
                      if prob > score[i][i+1][A] 
                        score[i][i+1][A] = prob
                        back[i][i+1][A] = B 
                        added = true
                        
              for span = 2 to #(words)
                for begin = 0 to #(words)- span
                    end = begin + span
                    for split = begin+1 to end-1
                        for A,B,C in nonterms
                            prob=score[begin][split][B]*score[split][end][C]*P(A->BC)
                            if prob > score[begin][end][A]
                                score[begin]end][A] = prob
                                back[begin][end][A] = new Triple(split,B,C)
                    //handle unaries
                    boolean added = true
                    while added
                        added = false
                        for A, B in nonterms
                        prob = P(A->B)*score[begin][end][B];
                            if prob > score[begin][end][A]
                                score[begin][end][A] = prob
                                back[begin][end][A] = B
                                added = true           
        """
        # TODO: implement this method
        logging.debug('get_best_parse(%s)' % sentence)
        lexicon = self.lexicon
        grammar = self.grammar
        #nonterms = grammar.binary_rules_by_left_child
        
        #print 'grammar.unary_rules_by_child'
        #PP(dict([(k,[str(s) for s in v]) for k,v in grammar.unary_rules_by_child.items()]))
        rules = [str(s) for s in grammar.unary_rules_by_child['N']]
        #print 'grammar.unary_rules_by_child[%s]=%s' % ('N', rules)
            
        n = len(sentence)
        #m = len(nonterms)
        scores = [[{} for j in range(n+1)] for i in range(n+1)]
        back = [[{} for j in range(n+1)] for i in range(n+1)]
        
        # First the Lexicon
        logging.debug('start lexicon n=%d' % n)
        for i in range(n):
            word = sentence[i]
            for tag in lexicon.get_all_tags():
                A = UnaryRule(tag, word)
                A.score = lexicon.score_tagging(word, tag)
                scores[i][i+1][A] = A.score 
                back[i][i+1][A] = None

            # handle unaries
            added = True
            while added:
                added = False
                # Don't modify the dict we are iterating
                these_scores = copy.copy(scores[i][i+1])
                for B in these_scores:
                    for A in grammar.get_unary_rules_by_child(B.parent):
                         if these_scores[B] > 0:
                            prob = B.score * these_scores[B] 
                            if prob > these_scores.get(A, 0): 
                                scores[i][i+1][A] = prob
                                back[i][i+1][A] = [B] 
                                added = True
            
        # Do higher layers
        logging.debug('start higher layers')    
        for span in range(2, n + 1):
            for begin in range(n - span + 1):
                end = begin + span
                #logging.debug(' binaries: [%d,%d]' % (begin,end)) 
                for split in range(begin + 1, end):
                    B_scores = scores[begin][split]
                    C_scores = scores[split][end]
                    for B in B_scores:
                        for A in grammar.get_binary_rules_by_left_child(B.parent):
                            C2_scores = [C for C in C_scores if C.parent == A.right_child]
                            for C in C2_scores:
                                # Now have A which has B as left child and C as right child 
                                prob = B_scores[B] * C_scores[C] * A.score
                                if prob > scores[begin][end].get(A, 0):
                                    scores[begin][end][A] = prob
                                    back[begin][end][A] = [split, B, C]
                # Handle unaries