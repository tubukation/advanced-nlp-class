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
      double recall    = (gold    > 0 ? correct / (double) gold    : 1.0);
      double f1 = ((precision > 0.0 && recall > 0.0) ? 
                   2.0 / (1.0 / precision + 1.0 / recall) :
                   0.0);
      double exactMatch = exact / (double) total;

      pw.printf
        ("%s   P: %5.2f   R: %5.2f   F1: %5.2f   EX: %5.2f %n",
         prefixStr,
         100.0 * precision,
         100.0 * recall,
         100.0 * f1,
         100.0 * exactMatch);

      return 100.0 * f1;
    }

    public double display(boolean verbose) {
      return display(verbose, new PrintWriter(System.out, true));
    }

    public double display(boolean verbose, PrintWriter pw) {
      return displayPRF(str+" [Average] ", correctEvents, guessedEvents, goldEvents, exact, total, pw);
    }
  }

  static class LabeledConstituent<L> {
    L label;
    int start;
    int end;

    public L getLabel() {
      return label;
    }

    public int getStart() {
      return start;
    }

    public int getEnd() {
      return end;
    }

    public boolean equals(Object o) {
      if (this == o) return true;
      if (!(o instance