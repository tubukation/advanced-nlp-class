
package nlpclass.assignments;

import nlpclass.io.MASCTreebankReader;
import nlpclass.io.PennTreebankReader;
import nlpclass.ling.Tree;
import nlpclass.ling.Trees;
import nlpclass.parser.EnglishPennTreebankParseEvaluator;
import nlpclass.util.*;
//import nlpclass.classify.ProbabilisticClassifier;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Harness for PCFG Parser project.
 *
 * @author Dan Klein
 */
public class PCFGParserTester {

    // Parser interface ===========================================================

    /**
     * Parsers are required to map sentences to trees.  How a parser is
     * constructed and trained is not specified.
     */
    public static interface Parser {
        public void train(List<Tree<String>> trainTrees);
        public Tree<String> getBestParse(List<String> sentence);
    }

    // PCFGParser =================================================================

    /**
     * The PCFG Parser you will implement.
     */
    public static class PCFGParser implements Parser {
    
        private Grammar grammar;
        private Lexicon lexicon;

        public void train(List<Tree<String>> trainTrees) {
            // TODO: before you generate your grammar, the training trees
            // need to be binarized so that rules are at most binary

            List<Tree<String>> annotatedTrees = new ArrayList<Tree<String>>();
            for (Tree<String> tree: trainTrees) {
                 annotatedTrees.add(TreeAnnotations.annotateTree(tree));
            }
            
            /*
            System.out.println("trainTrees: " );
            for (Tree<String> tree: trainTrees)  System.out.println("  " + tree);
            System.out.println("annotatedTrees: " );
            for (Tree<String> tree: annotatedTrees)  System.out.println("  " + tree);
             */
            lexicon = new Lexicon(annotatedTrees);
            grammar = new Grammar(annotatedTrees);
            
            /*
            System.out.println("lexicon: " + lexicon.getAllTags());
            System.out.println("grammar: " + grammar);
            */
            //System.exit(-1);
        }
        
        private static String getParent(Object o) {
            if (o instanceof BinaryRule) {
                return ((BinaryRule)o).getParent();
            } else if (o instanceof UnaryRule) {
                return ((UnaryRule)o).getParent();
            } else {
                return null;
            }
        }
        
        // Print a CKY chart
        private static void printChart(List<List<Map<Object,Double>>> chart, 
                                List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs, 
                                String name) {
            System.out.println("-------------------- $$$$$ --------------------");
            System.out.println(name);
            String spacer = ""; 
            for (int span = chart.size() - 1; span > 0; span--) {
                for (int begin = 0; begin < chart.size() - span; begin++) {
                    int end = begin + span;
                    System.out.println(spacer + begin + "," + end);
                    Map<Object,Double> counter = chart.get(begin).get(end);
                    Map<Object,Triplet<Integer,Object,Object>> backptr = backs.get(begin).get(end);
                    for (Object o: counter.keySet()) {
                        System.out.println(spacer + " " + o  
                            + " : " + counter.get(o) 
                            + " : " + backptr.get(o));
                    }
                }
                spacer += "\t";
            }
            System.out.println("-------------------- ***** --------------------");
        }

        private static List<Object> copyKeys(Map<Object,Double> counter) {
            List<Object> keys = new ArrayList<Object>();
            for (Object k: counter.keySet()) {
                keys.add(k);
            }
            return keys;
        }

        private Tree<String> makeTree(
                            List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs, 
                            int begin, int end, Object A) {

            Triplet<Integer,Object,Object> backptr = backs.get(begin).get(end).get(A);
            String tag = getParent(A);

            //System.out.println("makeTree: begin=" + begin + ",end=" + end + ",A=" + A + " : " + "backptr=" + backptr);

            List<Tree<String>> children = new ArrayList<Tree<String>>();
            
            if (backptr == null) { 
                // No back pointer. Terminal
                Tree<String> child = new Tree<String>(((UnaryRule)A).getChild()); 
                children.add(child);
            } else  if (backptr.getFirst() < 0) {
                // Single back pointer. Unary rule 
                Object B = backptr.getSecond();
                Tree<String> child = makeTree(backs, begin, end, B); 
                children.add(child);
            } else {
                // Two back pointers. Binary rule
                int split = backptr.getFirst();