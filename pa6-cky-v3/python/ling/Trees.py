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
    def tr