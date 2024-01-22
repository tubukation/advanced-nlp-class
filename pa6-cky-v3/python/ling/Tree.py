
from Constituent import Constituent

class Tree:

    # TODO: deepCopy() ?

    def __init__(self, label, children = []):
        """
            The constructor.
        """
        self.label = label
        self.children = children

    def is_leaf(self):
        """
            Returns true at the word (leaf) level of a tree.
        """
        return len(self.children) == 0

    def is_preterminal(self):
        """
            Returns true level for non-terminals which are directly above
            single words (leaves).
        """
        return len(self.children) == 1 and self.children[0].is_leaf()

    def is_phrasal(self):
        # Seems to be defined incorrectly. Not used anywhere.
        return not self.is_leaf() and not self.is_preterminal()

    def _append_yield(self, leaf_labels):
        if self.is_leaf():
            leaf_labels.append(self.label)
            return
        for child in self.children:
            child._append_yield(leaf_labels)

    def get_yield(self):