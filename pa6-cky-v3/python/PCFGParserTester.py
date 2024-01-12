
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
                #logging.debug(' unaries: [%d,%d]' % (begin,end)) 
                added = True
                while added:
                    added = False
                    these_scores = copy.copy(scores[begin][end])
                    for B in these_scores:
                        for A in grammar.get_unary_rules_by_child(B.parent):
                            prob = B.score * these_scores[B] 
                            if prob > these_scores.get(A, 0): 
                                scores[begin][end][A] = prob
                                back[begin][end][A] = [B] 
                                #print 'added %s => %s' % (A,B)
                                added = True

        if False and _VERBOSE:
            #s = [[D(d) for d in r] for r in scores]
            #PP(s)
            print_chart(scores, 'scores')
            print_chart(back, 'back')
            #exit()

        # Build tree from backpointers
        top = scores[0][n]
        if True and _VERBOSE:
            print 'top'
            PP(D(top))
            #exit()
        #print [k.parent for k in top]
        #print 'top roots'
        top_roots = dict([(k,top[k]) for k in top if k.parent == 'ROOT'])
        if True and _VERBOSE:
            print 'top_roots'
            PP(D(top_roots))
        # Take highest probabilty
        k = max(top_roots, key=lambda x: top_roots[x])
        top_roots = {k:top[k]}
        if True and _VERBOSE:
            print 'the top_root'
            PP(D(top_roots))
            exit()
            
        def make_tree(begin, end, A, depth = 0):
            s = '   ' * (depth)
            #print s, 'make_tree(%d, %d, "%s")' % (begin, end, str(A)),
            backptrs = back[begin][end][A]
            #print D(backptrs)
            tag = A.parent
            if not backptrs: 
                #print s, '**', str(A), tag, A.child
                return Tree(tag, [Tree(A.child)])
            if len(backptrs) == 1:
                [B] = backptrs
                child = make_tree(begin, end, B, depth+1)
                return Tree(tag, [child])
            elif len(backptrs) == 3:
                [split, B, C] = backptrs
                childB = make_tree(begin, split, B, depth+1)
                childC = make_tree(split, end, C, depth+1)
                return Tree(tag, [childB, childC]) 

        #print '-' * 80
        logging.debug('start making tree')
        out_trees = []
        for root in top_roots:
            tree = make_tree(0, n, root)
            #print '!' * 80
            out_trees.append(tree)
            if False:
                print '^' * 80
                print Trees.PennTreeRenderer.render(tree)
                print '.' * 80
                exit()
 
        out_trees = [TreeAnnotations.unannotate_tree(tree) for tree in out_trees]
        if False:
            print '^' * 80
            print Trees.PennTreeRenderer.render(out_trees[0])
            print ',' * 80
        logging.debug('done tree')    
        return out_trees[0]

class BaselineParser(Parser):

    def train(self, train_trees):
        self.lexicon = Lexicon(train_trees)
        self.known_parses = {}
        self.span_to_categories = {}
        for train_tree in train_trees:
            tags = train_tree.get_preterminal_yield()
            tags = tuple(tags)  # because lists are not hashable, but tuples are
            if tags not in self.known_parses:
                self.known_parses[tags] = {}
            if train_tree not in self.known_parses[tags]:
                self.known_parses[tags][train_tree] = 1
            else:
                self.known_parses[tags][train_tree] += 1
            self.tally_spans(train_tree, 0)

    def get_best_parse(self, sentence):
        tags = self.get_baseline_tagging(sentence)
        tags = tuple(tags)
        if tags in self.known_parses:
            return self.get_best_known_parse(tags, sentence)
        else:
            return self.build_right_branch_parse(sentence, list(tags))

    def build_right_branch_parse(self, words, tags):
        cur_position = len(words) - 1
        right_branch_tree = self.build_tag_tree(words, tags, cur_position)
        while cur_position > 0:
            cur_position -= 1
            right_branch_tree = self.merge(
                    self.build_tag_tree(words, tags, cur_position),
                    right_branch_tree)
        right_branch_tree = self.add_root(right_branch_tree)
        return right_branch_tree

    def merge(self, left_tree, right_tree):
        span = len(left_tree.get_yield()) + len(right_tree.get_yield())
        maxval = max(self.span_to_categories[span].values())
        for key in self.span_to_categories[span]:
            if self.span_to_categories[span][key] == maxval:
                most_freq_label = key
                break
        return Tree(most_freq_label, [left_tree, right_tree])

    def add_root(self, tree):
        return Tree('ROOT', [tree])

    def build_tag_tree(self, words, tags, cur_position):
        leaf_tree = Tree(words[cur_position])
        tag_tree = Tree(tags[cur_position], [leaf_tree])
        return tag_tree

    def get_best_known_parse(self, tags, sentence):
        # Simpler 
        # parses = self.known_parses[tags]
        # parse = max(parses.keys(), key = lambda k: parses[k])
        
        maxval = max(self.known_parses[tags].values())
        for key in self.known_parses[tags]:
            if self.known_parses[tags][key] == maxval:
                parse = key
                break
        parse = copy.deepcopy(parse)
        parse.set_words(sentence)
        return parse

    def get_baseline_tagging(self, sentence):
        return [self.get_best_tag(word) for word in sentence]

    def get_best_tag(self, word):
        # Simpler 
        # return max(self.lexicon.get_all_tags(), 
        #    key = lambda k: self.lexicon.score_tagging(word, k))
        best_score = 0
        best_tag = None
        for tag in self.lexicon.get_all_tags():
            score = self.lexicon.score_tagging(word, tag)
            if best_tag is None or score > best_score:
                best_score = score
                best_tag = tag
        return best_tag

    def tally_spans(self, tree, start):
        if tree.is_leaf() or tree.is_preterminal():
            return 1
        end = start
        for child in tree.children:
            child_span = self.tally_spans(child, end)
            end += child_span
        category = tree.label
        if category != "ROOT":
            if end-start not in self.span_to_categories:
                self.span_to_categories[end-start] = {}
            if category not in self.span_to_categories[end-start]:
                self.span_to_categories[end-start][category] = 1
            else:
                self.span_to_categories[end-start][category] += 1