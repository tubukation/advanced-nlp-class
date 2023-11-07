
package nlpclass.ling;

import nlpclass.util.Filter;

import java.io.IOException;
import java.io.PushbackReader;
import java.io.Reader;
import java.io.StringReader;
import java.util.*;

/**
 * Tools for displaying, reading, and modifying trees.
 *
 * @author Dan Klein
 * @author Paul Baumstarck (added GENIA and BioIE readers 2008.4)
 */
public class Trees {

    public static interface TreeTransformer<E> {
        Tree<E> transformTree(Tree<E> tree);
    }

    public static class FunctionNodeStripper implements TreeTransformer<String> {
        public Tree<String> transformTree(Tree<String> tree) {
            String transformedLabel = tree.getLabel();
            int cutIndex = transformedLabel.indexOf('-');