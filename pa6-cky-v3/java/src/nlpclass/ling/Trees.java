
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
            int cutIndex2 = transformedLabel.indexOf('=');
            if (cutIndex2 > 0 && (cutIndex2 < cutIndex || cutIndex == -1))
                cutIndex = cutIndex2;
            cutIndex2 = transformedLabel.indexOf('^');
            if (cutIndex2 > 0 && (cutIndex2 < cutIndex || cutIndex == -1))
                cutIndex = cutIndex2;
            cutIndex2 = transformedLabel.indexOf(':');
            if (cutIndex2 > 0 && (cutIndex2 < cutIndex || cutIndex == -1))
                cutIndex = cutIndex2;

            if (cutIndex > 0 && !tree.isLeaf()) {
                transformedLabel = new String(transformedLabel.substring(0,
                        cutIndex));
            }
            if (tree.isLeaf()) {
                return new Tree<String>(transformedLabel);
            }
            List<Tree<String>> transformedChildren = new ArrayList<Tree<String>>();
            for (Tree<String> child : tree.getChildren()) {
                transformedChildren.add(transformTree(child));
            }
            return new Tree<String>(transformedLabel, transformedChildren);
        }
    }

    public static class EmptyNodeStripper implements TreeTransformer<String> {
        public Tree<String> transformTree(Tree<String> tree) {
            String label = tree.getLabel();
            if (label.equals("-NONE-")) {
                return null;
            }
            if (tree.isLeaf()) {
                return new Tree<String>(label);
            }
            List<Tree<String>> children = tree.getChildren();
            List<Tree<String>> transformedChildren = new ArrayList<Tree<String>>();
            for (Tree<String> child : children) {
                Tree<String> transformedChild = transformTree(child);
                if (transformedChild != null)
                    transformedChildren.add(transformedChild);
            }
            if (transformedChildren.size() == 0)
                return null;
            return new Tree<String>(label, transformedChildren);
        }
    }

    public static class XOverXRemover<E> implements TreeTransformer<E> {
        public Tree<E> transformTree(Tree<E> tree) {
            E label = tree.getLabel();
            List<Tree<E>> children = tree.getChildren();
            while (children.size() == 1 && !children.get(0).isLeaf()
                    && label.equals(children.get(0).getLabel())) {
                children = children.get(0).getChildren();
            }
            List<Tree<E>> transformedChildren = new ArrayList<Tree<E>>();
            for (Tree<E> child : children) {
                transformedChildren.add(transformTree(child));
            }
            return new Tree<E>(label, transformedChildren);
        }
    }

    public static class StandardTreeNormalizer implements
            TreeTransformer<String> {
        EmptyNodeStripper emptyNodeStripper = new EmptyNodeStripper();
        XOverXRemover<String> xOverXRemover = new XOverXRemover<String>();
        FunctionNodeStripper functionNodeStripper = new FunctionNodeStripper();

        public Tree<String> transformTree(Tree<String> tree) {
            tree = functionNodeStripper.transformTree(tree);
            tree = emptyNodeStripper.transformTree(tree);
            tree = xOverXRemover.transformTree(tree);
            return tree;
        }
    }

    public static class TreeReader {
        public static String ROOT_LABEL = "ROOT";
        
        PushbackReader in;
        Tree<String> nextTree;

        public boolean hasNext() {
            return (nextTree != null);
        }

        public Tree<String> next() {
            if (!hasNext())
                throw new NoSuchElementException();
            Tree<String> tree = nextTree;
            nextTree = readRootTree();
            return tree;
        }
        
        public Tree<String> readRootTree() {
            throw new RuntimeException("readRootTree() undefined.");
        }

        public int peek() throws IOException {
            int ch = in.read();
            in.unread(ch);
            return ch;
        }

        public String readLabel() throws IOException {
            readWhiteSpace();
            return readText();
        }
        
        public Tree<String> readLeaf() throws IOException {
            String label = readText();
            return new Tree<String>(label);
        }
        
        public String readText() throws IOException {
            StringBuilder sb = new StringBuilder();
            int ch = in.read();
            while (!isWhiteSpace(ch) && !isLeftParen(ch) && !isRightParen(ch)) {
                sb.append((char) ch);
                ch = in.read();
            }
            in.unread(ch);
            //      System.out.println("Read text: ["+sb+"]");
            return sb.toString().intern();
        }
        
        public void readLeftParen() throws IOException {
            //      System.out.println("Read left.");
            readWhiteSpace();
            int ch = in.read();
            if (!isLeftParen(ch)) {
                throw new RuntimeException("Format error reading tree.");
            }
        }

        public void readRightParen() throws IOException {
            //      System.out.println("Read right.");
            readWhiteSpace();
            int ch = in.read();
            if (!isRightParen(ch)) {
                throw new RuntimeException("Format error reading tree.");
            }
        }

        public void readWhiteSpace() throws IOException {
            int ch = in.read();
            while (isWhiteSpace(ch)) {
                ch = in.read();
            }
            in.unread(ch);
        }

        public boolean isWhiteSpace(int ch) {
            return (ch == ' ' || ch == '\t' || ch == '\f' || ch == '\r' || ch == '\n');
        }

        public boolean isLeftParen(int ch) {
            return ch == '(';
        }
