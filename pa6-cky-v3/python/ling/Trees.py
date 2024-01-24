from Tree import Tree

# TODO: should I replace rendering of tree.label to str(tree.label)??

##################
# Class Methods
##################
ROOT_LABEL = "ROOT"

class TreeTransformer:
    """
        Abstract base class for different Tree transformation classes.
    """
    @classmethod
    def transform_tree(cls, tree):
        raise NotImplementedError()

class FunctionNodeStripper(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        transformed_label = tree.label
        cut_idx = transformed_label.find('-')
        cut_idx2 = transformed_label.find('=')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2
        cut_idx2 = transformed_label.find('^')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx 