
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

        public boolean isRightParen(int ch) {
            return ch == ')';
        }
        
        public boolean isSemicolon(int ch) {
            return ch == ';';
        }

        public void remove() {
            throw new UnsupportedOperationException();
        }
    }

    public static class BioIETreeReader extends TreeReader implements Iterator<Tree<String>> {
        
        public Tree<String> readRootTree() {
            try {
                for (;;) {
                    readCommentsAndWhiteSpace();
                    if (!isLeftParen(peek()))
                        return null;
                    in.read(); // (
                    String str = readText();
                    if ( str.equals("SENT") )
                        break; // read the sentence
                    else if ( str.equals("SEC") ) {
                        // read in the section, "("-less tree, then throw it away
                        readTree(false);
                    } else {
                        //System.out.println("Failed: "+str);
                        return null; // reading error
                    }
                }
                // We have stripped off "(SENT", so read a "("-less tree.
                return new Tree<String>(ROOT_LABEL, Collections.singletonList(readTree(false)));
            } catch (IOException e) {
                throw new RuntimeException("Error reading tree."+e.toString());
            }
        }

        private Tree<String> readTree(boolean matchparen) throws IOException {
            if ( matchparen )
                readLeftParen();
            String label = readColonizedLabel();
            //System.out.println("  "+label);
            List<Tree<String>> children = readChildren();
            readRightParen();
            return new Tree<String>(label, children);
        }
        
        public String readColonizedLabel() throws IOException {
            readWhiteSpace();
            String ret = readText();
            int i = ret.indexOf(":");
            if ( i == -1 )
                return ret;
            else
                return ret.substring(0,i);
        }
        
        private List<Tree<String>> readChildren() throws IOException {
            readWhiteSpace();
            if (!isLeftParen(peek()))
                return Collections.singletonList(readLeaf());
            else
                return readChildList();
        }

        private List<Tree<String>> readChildList() throws IOException {
            List<Tree<String>> children = new ArrayList<Tree<String>>();
            readWhiteSpace();
            while (!isRightParen(peek())) {
                children.add(readTree(true));
                readWhiteSpace();
            }
            return children;
        }
                
        private void readCommentsAndWhiteSpace() throws IOException {
            int ch;
            for (;;) {
                readWhiteSpace();
                if ( !isSemicolon(peek()) )
                    return;
                // read a line
                ch = in.read();
                while ( ch != '\n' )
                    ch = in.read();
            }
        }

        public BioIETreeReader(Reader in) {
            this.in = new PushbackReader(in);
            nextTree = readRootTree();
        }
    }

    public static class PennTreeReader extends TreeReader implements Iterator<Tree<String>> {
        
        public Tree<String> readRootTree() {
            try {
                readWhiteSpace();
                if (!isLeftParen(peek()))
                    return null;
                return readTree(true);
            } catch (IOException e) {
                throw new RuntimeException("Error reading tree.");
            }
        }

        private Tree<String> readTree(boolean isRoot) throws IOException {
            readLeftParen();
            String label = readLabel();
            if (label.length() == 0 && isRoot)
                label = ROOT_LABEL;
            List<Tree<String>> children = readChildren();
            readRightParen();
            return new Tree<String>(label, children);
        }

        private List<Tree<String>> readChildren() throws IOException {
            readWhiteSpace();
            if (!isLeftParen(peek()))
                return Collections.singletonList(readLeaf());
            return readChildList();
        }

        private List<Tree<String>> readChildList() throws IOException {
            List<Tree<String>> children = new ArrayList<Tree<String>>();
            readWhiteSpace();
            while (!isRightParen(peek())) {
                children.add(readTree(false));
                readWhiteSpace();
            }
            return children;
        }

        public PennTreeReader(Reader in) {
            this.in = new PushbackReader(in);
            nextTree = readRootTree();
        }
    }

    public static class GENIATreeReader extends TreeReader implements Iterator<Tree<String>> {

        public Tree<String> readRootTree() {
            try {
                readWhiteSpace();
                if (!isLeftParen(peek()))
                    return null;
                return new Tree<String>(ROOT_LABEL, Collections.singletonList(readTree(false)));
            } catch (IOException e) {
                throw new RuntimeException("Error reading tree.");
            }
        }

        private Tree<String> readTree(boolean isRoot) throws IOException {
            readLeftParen();
            String label = readLabel();
            if (label.length() == 0 && isRoot)
                label = ROOT_LABEL;
            List<Tree<String>> children = readChildren();
            readRightParen();
            return new Tree<String>(label, children);
        }

        private List<Tree<String>> readChildren() throws IOException {
            List<Tree<String>> children = new ArrayList<Tree<String>>();
            readWhiteSpace();
            while (!isRightParen(peek())) {
                if ( isLeftParen(peek()) ) {
                    children.add(readTree(false));
                } else {
                    Tree<String> ret = readSlashLabel();
                    if ( ret != null )
                        children.add(ret);
                }
                readWhiteSpace();
            }
            return children;
        }
        
        private Tree<String> readSlashLabel() throws IOException {
            String label = readText();
            int i = label.lastIndexOf("/");
            if ( i == -1 ) return null;
            while ( i > 0 && label.charAt(i-1) == '\\' ) {
                i = label.lastIndexOf("/",i-1);
            }
            return new Tree<String>(label.substring(i+1),
                    Collections.singletonList(new Tree<String>( label.substring(0,i).replaceAll("\\\\\\/","\\/") )));
        }

        public GENIATreeReader(Reader in) {
            this.in = new PushbackReader(in);
            nextTree = readRootTree();
        }
    }

    /**
     * Renderer for pretty-printing trees according to the Penn Treebank indenting
     * guidelines (mutliline).  Adapted from code originally written by Dan Klein
     * and modified by Chris Manning.
     */
    public static class PennTreeRenderer {

        /**