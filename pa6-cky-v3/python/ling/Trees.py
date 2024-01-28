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
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2
        cut_idx2 = transformed_label.find(':')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2

        if cut_idx > 0 and not tree.is_leaf():
            transformed_label = transformed_label[:cut_idx]
        if tree.is_leaf():
            return Tree(transformed_label)

        transformed_children = []
        for child in tree.children:
            transformed_children.append(FunctionNodeStripper.transform_tree(child))

        return Tree(transformed_label, transformed_children)

class EmptyNodeStripper(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        label = tree.label
        if label == "-NONE-":
            return None
        if tree.is_leaf():
            return Tree(label)
        children = tree.children
        transformed_children = []
        for child in children:
            transformed_child = EmptyNodeStripper.transform_tree(child)
            if transformed_child is not None:
                transformed_children.append(transformed_child)
        if len(transformed_children) == 0:
            return None
        return Tree(label, transformed_children)

class XOverXRemover(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        label = tree.label
        children = tree.children
        while len(children) == 1 and not children[0].is_leaf() \
                and label == children[0].label:
            children = children[0