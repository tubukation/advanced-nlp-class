
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
                Object B = backptr.getSecond();
                Object C = backptr.getThird();
                Tree<String> childB = makeTree(backs, begin, split, B);
                Tree<String> childC = makeTree(backs, split, end, C);
                children.add(childB);
                children.add(childC);
            }
            return new Tree<String>(tag, children);
        }  
    
        public Tree<String> getBestParse(List<String> sentence) {
            // TODO: implement this method
            int n = sentence.size();

            //System.out.println("getBestParse: n=" + n);

            List<List<Map<Object,Double>>> scores = new ArrayList<List<Map<Object,Double>>>(n+1);
            for (int i = 0; i < n+1; i++) {
                List<Map<Object,Double>> row = new ArrayList<Map<Object,Double>>(n+1);
                for (int j = 0; j < n+1; j++) {
                    row.add(new HashMap<Object,Double>());
                }
                scores.add(row);
            }
            List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs = new ArrayList<List<Map<Object,Triplet<Integer,Object,Object>>>>(n+1);
            for (int i = 0; i < n+1; i++) {
                List<Map<Object,Triplet<Integer,Object,Object>>> row = new ArrayList<Map<Object,Triplet<Integer,Object,Object>>>(n+1);
                for (int j = 0; j < n+1; j++) {
                    row.add(new HashMap<Object,Triplet<Integer,Object,Object>>());
                }
                backs.add(row);
            }

            /*
            System.out.println("scores=" + scores.size() + "x" + scores.get(0).size());
            System.out.println("backs=" + backs.size() + "x" + backs.get(0).size());
            printChart(scores, backs, "scores");
            */              
            // First the Lexicon
            
            for (int i = 0; i < n; i++) {
                String word = sentence.get(i);
                for (String tag : lexicon.getAllTags()) {
                    UnaryRule A = new UnaryRule(tag, word);
                    A.setScore(Math.log(lexicon.scoreTagging(word, tag)));
                    scores.get(i).get(i+1).put(A, A.getScore()); 
                    backs.get(i).get(i+1).put(A, null);
                }

                //System.out.println("Starting unaries: i=" + i + ",n=" + n );
                // Handle unaries
                boolean added = true;
                while (added) {
                    added = false;
                    Map<Object,Double> A_scores = scores.get(i).get(i+1);
                    // Don't modify the dict we are iterating
                    List<Object> A_keys = copyKeys(A_scores);
                    //for (int j = 0; j < 5 && j < A_keys.size(); j++) {
                    //	System.out.print("," + j + "=" + A_scores.get(A_keys.get(j)));  
                    //}
                    
                    for (Object oB : A_keys) {
                        UnaryRule B = (UnaryRule)oB;
                        for (UnaryRule A : grammar.getUnaryRulesByChild(B.getParent())) {
                            double prob = Math.log(A.getScore()) + A_scores.get(B); 
                            if (prob > -1000.0) {
                                
                                if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
                                    //System.out.print(" *A=" + A + ", B=" + B);
                                    //System.out.print(",  prob=" +  prob);
                                    //System.out.println(",  A_scores.get(A)=" +  A_scores.get(A));
                                    A_scores.put(A, prob);
                                    backs.get(i).get(i+1).put(A, new Triplet<Integer,Object,Object>(-1, B, null));
                                    added = true;
                                }
                                //System.out.println(", added=" + added);
                            }
                            
                        } 
                    } 
                    //System.out.println(", A_scores=" + A_scores.size() + ", added=" + added);	
                }
            }

            //printChart(scores, backs, "scores with Lexicon");

            // Do higher layers  
            // Naming is based on rules: A -> B,C
        
            long startTime = new Date().getTime();
            for (int span = 2; span < n + 1; span++) {

                for (int begin = 0; begin < n + 1 - span; begin++) {
                    int end = begin + span;

                    Map<Object,Double> A_scores = scores.get(begin).get(end);
                    Map<Object,Triplet<Integer,Object,Object>> A_backs = backs.get(begin).get(end);

                    for (int split = begin + 1; split < end; split++) {

                        Map<Object,Double> B_scores = scores.get(begin).get(split);
                        Map<Object,Double> C_scores = scores.get(split).get(end);
                        
                        List<Object> B_list = new ArrayList<Object>(B_scores.keySet());
                        List<Object> C_list = new ArrayList<Object>(C_scores.keySet());

                        // This is a key optimization. !@#$
                        // It avoids a B_list.size() x C_list.size() search in the for (Object B : B_list) loop 
                        Map<String,List<Object>> C_map = new HashMap<String,List<Object>>();
                        for (Object C : C_list) {
                            String parent = getParent(C);
                            if (!C_map.containsKey(parent)) {
                                C_map.put(parent, new ArrayList<Object>());     
                            }
                            C_map.get(parent).add(C);
                        }

                        for (Object B : B_list) { 
                            for (BinaryRule A : grammar.getBinaryRulesByLeftChild(getParent(B))) {
                                if (C_map.containsKey(A.getRightChild())) {
                                    for (Object C : C_map.get(A.getRightChild())) {
                                        // We now have A which has B as left child and C as right child 
                                        double prob = Math.log(A.getScore()) + B_scores.get(B) + C_scores.get(C);
                                        if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
                                            A_scores.put(A, prob);
                                            A_backs.put(A, new Triplet<Integer,Object,Object>(split, B, C));
                                        }
                                    } 
                                }
                            }
                        }

                    }
                   
                    // Handle unaries: A -> B
                    boolean added = true;
                    while (added) {
                        added = false;
                        // Don't modify the dict we are iterating
                        List<Object> A_keys = copyKeys(A_scores);
                        for (Object oB : A_keys) {
                            for (UnaryRule A : grammar.getUnaryRulesByChild(getParent(oB))) {
                                double prob = Math.log(A.getScore()) + A_scores.get(oB); 
                                if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
                                    A_scores.put(A, prob);
                                    A_backs.put(A, new Triplet<Integer,Object,Object>(-1, oB, null));
                                    added = true;
                                }
                            }
                        }
                    }
                   
                }    
            }

            //printChart(scores, backs, "scores with Lexicon and Grammar");
            
            Map<Object,Double> topOfChart = scores.get(0).get(n);
            
            System.out.println("topOfChart: " + topOfChart.size());
            /*
            for (Object o: topOfChart.keySet()) {
                System.out.println("o=" + o + ", score=" + topOfChart.getCount(o));
            }
            */
         
            // All parses have "ROOT" at top of tree
            Object bestKey = null;
            Object secondBestKey = null;
            double bestScore = Double.NEGATIVE_INFINITY;
            double secondBestScore = Double.NEGATIVE_INFINITY;
            for (Object key: topOfChart.keySet()) {
                double score = topOfChart.get(key);
                if (score >= secondBestScore || secondBestKey == null) {
                    secondBestKey = key;
                    secondBestScore = score;
                }
                if ("ROOT".equals(getParent(key)) && (score >= bestScore || bestKey == null)) {
                    bestKey = key;
                    bestScore = score;
                }
            }
            
           if (bestKey == null) {
                bestKey = secondBestKey;
                System.out.println("secondBestKey=" + secondBestKey);
            }
            if (bestKey == null) {
                for (Object key: topOfChart.keySet()) {
                    System.out.println("val=" + topOfChart.get(key) + ", key=" + key);
                }
            }
            System.out.println("bestKey=" + bestKey + ", log(prob)=" + topOfChart.get(bestKey));
            
            Tree<String> result = makeTree(backs, 0, n, bestKey);
            if (!"ROOT".equals(result.getLabel())) {
                List<Tree<String>> children = new ArrayList<Tree<String>>();