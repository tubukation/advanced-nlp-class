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

    /* evaluates precision and re