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
        self.read_whitespace()
        return self.read_text()

    def read_leaf(self):
        label = self.read_text()
        return Tree(label)

    def read_text(self):
        s = []
        ch = self.ff.read(1)
        while not TreeReader.is_whitespace(ch) and \
                not TreeReader.is_left_paren(ch) and \
                not TreeReader.is_right_paren(ch):
            s.append(ch)
            ch = self.ff.read(1)
        self.ff.seek(-1, 1)
        return ''.join(s)

    def read_left_paren(self):
        self.read_whitespace()
        ch = self.ff.read(1)
        if not TreeReader.is_left_paren(ch):
            raise ValueError("Format error reading tree. Character %d." % \
                    (self.ff.tell() - 1))

    def read_right_paren(self):
        self.read_whitespace()
        ch = self.ff.read(1)
        if not TreeReader.is_right_paren(ch):
            import ipdb; ipdb.set_trace()
            raise ValueError("Format error reading tree. (filename: %s)" % self.ff.name)

    def read_whitespace(self):
        ch = self.ff.read(1)
        while TreeReader.is_whitespace(ch):
            ch = self.ff.read(1)
        self.ff.seek(-1, 1)

    @classmethod
    def is_whitespace(cls, ch):
        return ch == ' ' or ch == '\t' or ch == '\f' or ch == '\r' or ch == '\n'

    @classmethod
    def is_left_paren(cls, ch):
        return ch == '('

    @classmethod
    def is_right_paren(cls, ch):
        return ch == ')'

    @classmethod
    def is_semicolon(cls, ch):
        return ch == ';'

    def remove(self):
        return NotImplementedError()

class BioIETreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            while True:
                self.read_comments_and_whitespace()
                if not TreeReader.is_left_paren(self.peek()):
                    return None
                self.ff.read(1)
                string = self.read_text()
                if string == "SENT":
                    break
                elif string == "SEC":
                    self.read_tree(False)
                else:
                    return None
            # Collections.singletonList(readTree(false)) ??
            return Tree(ROOT_LABEL, [self.read_tree(False)])
        except IOError:
            raise Exception("Error reading tree: %s\n" % self.ff.name)

    def read_tree(self, matchparen):
        if matchparen:
            self.read_left_paren()
        label = self.read_colonized_label()
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_colonized_label(self):
        self.read_whitespace()
        ret = self.read_text()
        i = ret.find(':')
        if i == -1:
            return ret
        else:
            return ret[:i]

    def read_children(self):
        self.read_whitespace()
        if not TreeReader.is_left_paren(self.peek()):
            return [self.read_leaf()] # Collections.singletonList(readLeaf())
        else:
            return self.read_child_list()

    def read_child_list(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            children.append(self.read_tree(True))
            self.read_whitespace()
        return children

    def read_comments_and_whitespace(self):
        while True:
            self.read_whitespace()
            if not TreeReader.is_semicolon(self.peek()):
                return
            ch = self.ff.read(1)
            while not ch == '\n':
                ch = self.ff.read(1)

class PennTreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            self.read_whitespace()
            if not TreeReader.is_left_paren(self.peek()):
                return None
            return self.read_tree(True)
        except IOError:
            raise Exception('Error reading tree: %s\n' % self.ff.name)

    def read_tree(self, is_root):
        self.read_left_paren()
        label = self.read_label()
        if len(label) == 0 and is_root:
            label = ROOT_LABEL
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_children(self):
        self.read_whitespace()
        if not TreeReader.is_left_paren(self.peek()):
            return [self.read_leaf()] # Collections.singletonList
        return self.read_child_list()

    def read_child_list(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            children.append(self.read_tree(False))
            self.read_whitespace()
        return children

class GENIATreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            self.read_whitespace()
            if not TreeReader.is_left_paren(self.peek()):
                return None
            return Tree(ROOT_LABEL, [self.read_tree(False)])
        except IOError:
            raise Exception("Error reading tree: %s\n" % self.ff.name)

    def read_tree(self, is_root):
        self.read_left_paren()
        label = self.read_label()
        if len(label) == 0 and is_root:
            label = ROOT_LABEL
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_children(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            if TreeReader.is_left_paren(self.peek()):
                children.append(self.read_tree(False))
            else:
                ret = self.read_slash_label()
                if ret is not None:
                    children.append(ret)
            self.read_whitespace()
        return children

    def read_slash_label(self):
        label = self.read_text()
        i = label.rfind('/')
        if i == -1:
            return None
        while i > 0 and label[i-1] == '\\':
            i = label.rfind('/', 0, i-1)
        child_label = label[:i].replace('\\\\\\/', '\\/')
        return Tree(label[i+1:], [Tree(child_label)])

class PennTreeRenderer:
    """
        Renderer for pretty-printing trees according to the Penn Treebank indenting
        guidelines (mutliline).  Adapted from code originally written by Dan Klein
        and modified by Chris Manning.
    """
    @classmethod
    def render(cls, tree):
        s = []
        PennTreeRenderer.render_tree(tree, 0, False, False, False, True, s)
        s.append('\n')
        return ''.join(s)

    @classmethod
    def render_tree(cls, tree, indent, parent_label_null, first_sibling, \
            left_sibling_preterminal, top_level, s):
        # Condition for staying on same line in Penn Treebank
        suppress_indent = parent_label_null or \
                (first_sibling and tree.is_preterminal()) or \
 