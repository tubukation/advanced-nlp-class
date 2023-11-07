
package nlpclass.ling;

//import nlpclass.util.Counter;
//import nlpclass.util.CollectionUtils;

import java.util.*;

/**
 * Represent linguistic trees, with each node consisting of a label
 * and a list of children.
 * @author Dan Klein
 */
public class Tree<L> {
    L label;
    List<Tree<L>> children;

    public List<Tree<L>> getChildren() {
        return children;
    }
    
    public void setChildren(List<Tree<L>> children) {
        this.children = children;
    }
    
    public L getLabel() {
        return label;
    }
    
    public void setLabel(L label) {
        this.label = label;
    }

    /* Returns true at the word(leaf) level of a tree */
    public boolean isLeaf() {
        return getChildren().isEmpty();
    }

    /* Returns true level of non-terminals which are directly above
     * single words(leafs) 
     */
    public boolean isPreTerminal() {
        return getChildren().size() == 1 && getChildren().get(0).isLeaf();
    }

    public boolean isPhrasal() {
        return !(isLeaf() || isPreTerminal());
    }

    /* Returns a list of words at the leafs of this tree gotten by
     * traversing from left to right 
     */
    public List<L> getYield() {
        List<L> yield = new ArrayList<L>();
        appendYield(this, yield);