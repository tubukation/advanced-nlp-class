
from ling.Constituent import Constituent
from ling.Tree import Tree
import ling.Trees as Trees

"""
    Evaluates precision and recall for English Penn Treebank parse
    trees.  NOTE: Unlike the standard evaluation, multiplicity over
    each span is ignored.  Also, punctuation is NOT currently deleted
    properly (approximate hack), and other normalizations (like AVDP ~
    PRT) are NOT done.
"""

class AbstractEval:

    def __init__(self):
        self.string = ''
        self.exact = 0
        self.total = 0
        self.correct_events = 0
        self.guessed_events = 0
        self.gold_events = 0

    def evaluate(self, guess, gold):
        """
            Evaluates precision and recall by calling makeObjects() to make a
            set of structures for guess Tree and gold Tree, and compares them
            with each other.
        """
        guessed_set = self.make_objects(guess)
        gold_set = self.make_objects(gold)
        gold_set = self.make_objects(gold) # Seems redundant
        correct_set = set()
        correct_set.update(gold_set)
        correct_set.intersection_update(guessed_set)
        # correct_set = gold_set & guessed_set

        self.correct_events += len(correct_set)
        self.guessed_events += len(guessed_set)
        self.gold_events += len(gold_set)

        current_exact = 0
        if len(correct_set) == len(guessed_set) and \
                len(correct_set) == len(gold_set):
            self.exact += 1
            current_exact = 1
        self.total += 1

        return self.display_prf(self.string + ' [Current] ', len(correct_set),
                len(guessed_set), len(gold_set), current_exact, 1)

    def display_prf(self, pre_str, correct, guessed, gold, exact, total):

        precision = correct / float(guessed) if guessed > 0 else 1.0
        recall = correct / float(gold) if gold > 0 else 1.0
        f1 = 2.0 / (1.0 / precision + 1.0 / recall) \
                if precision > 0.0 and recall > 0.0 else 0.0
        exact_match = exact / float(total)

        print '%s   P: %5.2f   R: %5.2f   F1: %5.2f   EX: %5.2f' % \
                (pre_str, 100.0 * precision, 100.0 * recall, 100.0 * f1,
                        100.0 * exact_match)
        return 100.0 * f1

    def display(self, verbose):
        return self.display_prf(self.string + ' [Average] ', self.correct_events,
                self.guessed_events, self.gold_events, self.exact,
                self.total)

class LabeledConstituent:

    def __init__(self, label, start, end):
        self.label = label
        self.start = start
        self.end = end

    def __eq__(self, o):
        if self is o:     # tests if they are the same exact object
            return True