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
            children = children[0].children
        transformed_children = []
        for child in children:
            transformed_children.append(XOverXRemover.transform_tree(child))
        return Tree(label, transformed_children)

class StandardTreeNormalizer(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        tree = FunctionNodeStripper.transform_tree(tree)
        tree = EmptyNodeStripper.transform_tree(tree)
        tree = XOverXRemover.transform_tree(tree)
        return tree

class TreeReader:
    """
        Abstract base class for tree readers.
        NOTE: Does not implement read_root_tree()
        NOTE: self.ff is an open file object for reading a file
    """

    def __iter__(self):
        return self

    def next(self):
        if self.next_tree is None:
            raise StopIteration
        else:
            tree = self.next_tree
            self.next_tree = self.read_root_tree()
            return tree

    # Java version of iterable...
    """
    def has_next(self):
        return self.next_tree is not None

    def next(self):
        if not self.has_next():
            raise LookupError("No more trees!")
        tree = self.next_tree
        self.next_tree = self.read_root_tree()
        return tree
    """

    def read_root_tree(self):
        raise NotImplementedError()

    def peek(self):
        ch = self.ff.read(1)  # read a byte
        self.ff.seek(-1, 1)   # move back one byte
        return ch

    def read_label(self):
      