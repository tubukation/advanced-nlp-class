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

    private int exact