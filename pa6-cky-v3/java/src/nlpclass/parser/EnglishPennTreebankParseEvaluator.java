package nlpclass.parser;

import nlpclass.ling.Tree;
import nlpclass.ling.Trees;

import java.util.*;
import java.io.PrintWriter;
import java.io.StringReader;

/**
 * Evaluates precision and recall for English Penn Treebank parse
 * trees.  NOTE: Unlike the standard evaluation, multiplicity over
 * each span is ignored.  Also, punctuation is NOT currently deleted
 * properly (approximate hack), and other normalizations (like AVDP ~
 * PRT) are NOT done.
 *
 * @author Dan Klein
 */
public class EnglishPennTreebankParseEvaluator<L> {
    abstract static class AbstractEval<L> {

    protected String str = "";

    private int exact = 0;
    private int total = 0;

    private int correctEvents = 0;
    private int guessedEvents = 0;
    private int goldEvents = 0;

    abstract Set<Object> makeObjects(Tree<L> tree);

    public void evaluate(Tree<L> guess, Tree<L> gold) {
      evaluate(guess, gold, new PrintWriter(System.out, true));
    }

    /* evaluates precision and recall by calling makeObjects() to make a
     * set of structures for guess Tree and gold Tree, and compares them
     * with each other.  */
    public double evaluate(Tree<L> guess, Tree<L> gold, PrintWriter pw) {
      Set<Object> guessedSet = makeObjects(guess);
      Set<Object> goldSet = makeObjects(gold);
      Set<Object> correctSet = new HashSet<Object>();
      correctSet.addAll(goldSet);
      correctSet.retainAll(guessedSet);

      correctEvents += correctSet.size();
      guessedEvents += guessedSet.size();
      goldEvents += goldSet.size();

      int currentExact = 0;
      if (correctSet.size() == guessedSet.size() &&
          correctSet.size() == goldSet.size()) {
        exact++;
        currentExact = 1;
      }
      total++;

      // guess.pennPrint(pw);
      // gold.pennPrint(pw);
      return displayPRF(str + " [Current] ", 
                 correctSet.size(), guessedSet.size(), goldSet.size(), 
                 currentExact, 1, pw);

    }

    private double displayPRF(String prefixStr,
                            int correct,
                            int guessed,
                            int gold,
                            int exact,
                            int total,
                            PrintWriter pw) {

      double precision = (guessed > 0 ? correct / (double) guessed : 1.0);
      double recall    = (gold    > 0 ? correct / (double) gold 