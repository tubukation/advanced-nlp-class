package nlpclass.util;

import java.util.Map;
import java.util.HashMap;

/**
 * Utilities for managing command line flags and arguments.
 *
 * @author Dan Klein
 */
public class CommandLineUtils {

  /**
   * Simple method which turns an array of command line arguments into a
   * map, where each token starting with a '-' is a key and the following
   * non '-' initial token, if there is one, is the value.  For example,
   * '-size 5 -verbose' will produce a map with entries (-size, 5) and
   * (-verbose, null).
   */
    public static Map<String, String> simpleCommandLineParser(String[] args) {
        Map<String, String> map = new HashMap<String, String>();
        