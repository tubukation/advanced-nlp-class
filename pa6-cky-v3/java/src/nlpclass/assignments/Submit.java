
package nlpclass.assignments;

import nlpclass.util.Base64;
import nlpclass.assignments.PCFGParserTester.*;
import nlpclass.io.MASCTreebankReader;
import nlpclass.ling.Tree;
import nlpclass.ling.Trees;
import nlpclass.parser.EnglishPennTreebankParseEvaluator;
import nlpclass.util.*;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.io.StringReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.OutputStream;
import java.io.StringWriter;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;


public class Submit {

  private static int MAX_LENGTH = 20;

  public void submit(Integer partId) {
    System.out.println(String.format("==\n== [nlp] Submitting Solutions" +
                " | Programming Exercise %s\n==", homework_id()));

    partId = promptPart();
    List<String> partNames = validParts();
    if(!isValidPartId(partId)) {
      System.err.println("!! Invalid homework part selected.");
      System.err.println(String.format("!! Expected an integer from 1 to %d.", 
                          partNames.size() + 1));
      System.err.println("!! Submission Cancelled");
      return;
    }
  
    String [] loginPassword = loginPrompt();
    String login = loginPassword[0];
    String password = loginPassword[1];

    if(login == null || login.equals("")) {
      System.out.println("!! Submission Cancelled");
      return;
    }

    System.out.print("\n== Connecting to coursera ... ");

    // Setup submit list
    List<Integer> submitParts = new ArrayList<Integer>();
    if(partId == partNames.size() + 1) {
      for(int i = 1; i < partNames.size() + 1; i++) {
        submitParts.add(new Integer(i));
      }
    }
    else {
      submitParts.add(new Integer(partId));
    }

    for(Integer part : submitParts) {
      // Get Challenge
      String [] loginChSignature = getChallenge(login, part);
      if(loginChSignature == null) {
        return;
      }
      login = loginChSignature[0];
      String ch = loginChSignature[1];
      String signature = loginChSignature[2];
      String ch_aux = loginChSignature[3];

      // Attempt Submission with Challenge
      String ch_resp = challengeResponse(login, password, ch);
      String result = submitSolution(login, ch_resp, part.intValue(), output(part, ch_aux),
                                      source(part), signature);
      if(result == null) {
        result = "NULL RESPONSE";
      }
      System.out.println(String.format(
              "\n== [nlp] Submitted Homework %s - Part %d - %s",
              homework_id(), part, partNames.get(part - 1)));
      System.out.println("== " + result.trim());
      if (result.trim().equals("Exception: We could not verify your username / password, please try again. (Note that your password is case-sensitive.)")) {
	  System.out.println("== The password is not your login, but a 10 character alphanumeric string displayed on the top of the Assignments page.");
      }
    }
  }


  private String homework_id() {
    return "6";
  }


  private List<String> validParts() {
    List<String> parts = new ArrayList<String>();
    parts.add("Development Sentences");
    parts.add("Test Sentences");
    return parts;
  }
    
  private List<List<String>> sources() {
      List<List<String>> srcs = new ArrayList<List<String>>();
      List<String> tmp;
      tmp = new ArrayList<String>();
      tmp.add("src/nlpclass/assignments/PCFGParserTester.java");
      srcs.add(tmp);  // once for train
      tmp = new ArrayList<String>();
      tmp.add("src/nlpclass/assignments/PCFGParserTester.java");
      srcs.add(tmp);  // once for test
      return srcs;
  }

  private String challenge_url() {
    return "https://class.coursera.org/nlp/assignment/challenge";
    //return "https://class.coursera.org/nlp-staging/assignment/challenge";
  }

  private String submit_url() {
    return "https://class.coursera.org/nlp/assignment/submit";
    //return "https://class.coursera.org/nlp-staging/assignment/submit";
  }

 
  private static List<Tree<String>> readMASCTrees(String basePath, int low, int high) {
    Collection<Tree<String>> trees = MASCTreebankReader.readTrees(basePath, low, high);
    // normalize trees
    Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
    List<Tree<String>> normalizedTreeList = new ArrayList<Tree<String>>();
    for (Tree<String> tree : trees) {
      Tree<String> normalizedTree = treeTransformer.transformTree(tree);
      normalizedTreeList.add(normalizedTree);
    }
    return normalizedTreeList;
  }


  private static double testParser(Parser parser, List<Tree<String>> testTrees, PrintStream out) {
    EnglishPennTreebankParseEvaluator.LabeledConstituentEval<String> eval = 
      new EnglishPennTreebankParseEvaluator.LabeledConstituentEval<String>
      (Collections.singleton("ROOT"), 
       new HashSet<String>(Arrays.asList(new String[] {"''", "``", ".", ":", ","})));
    int numTrees = testTrees.size();
    for (int i = 0; i < numTrees; i++) {
      int treenum = i + 1;
      out.println("== Parsing tree " + treenum + " of " + numTrees + "...");
      Tree<String> testTree = testTrees.get(i);

      List<String> testSentence = testTree.getYield();
      if (testSentence.size() > MAX_LENGTH)
        continue;
      Tree<String> guessedTree = parser.getBestParse(testSentence);

      //out.println("Guess:\n"+Trees.PennTreeRenderer.render(guessedTree));
      //out.println("Gold:\n"+Trees.PennTreeRenderer.render(testTree));

      eval.evaluate(guessedTree, testTree);
    }
    return eval.display(true);
  }

 

  protected String output(int partId, String ch_aux) {
      System.out.println(String.format("== getting output for part: %d", partId));
      //System.out.println(String.format("== getting output for part: %d, ch_aux: %s", partId, ch_aux));
      if (ch_aux == null) {
        System.out.println("== Error receiving data from server. Please try again.");
      }

      /* override stdout */
      PrintStream out = System.out;
      System.setOut(new PrintStream(new OutputStream() {
        @Override public void write(int b) throws IOException {}
      }));

      int version = 1;

      //Parser parser = new BaselineParser();
      Parser parser = new PCFGParser();
      String basePath = "../data/parser/masc/";

      out.println("== Training parser...");
      List<Tree<String>> trainTrees = readMASCTrees(basePath + "train", 0, 38);
      parser.train(trainTrees);
      out.println("== done training.");

      double f1;
      if (partId == 1) {
        out.println("== Reading in development set...");
        List<Tree<String>> testTrees = readMASCTrees(basePath + "devtest", 0, 11);
        out.println("== Testing on development set...");
        f1 = testParser(parser, testTrees, out);
      } else if (partId == 2) {
        out.println("== Reading in test set...");

        StringReader testTreeReader = new StringReader(ch_aux);
        Trees.PennTreeReader ptr = new Trees.PennTreeReader(testTreeReader);

        List<Tree<String>> rawTestTrees = new ArrayList<Tree<String>>();
        while (ptr.hasNext()) {
          rawTestTrees.add(ptr.next());
        }

        Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
        List<Tree<String>> testTrees = new ArrayList<Tree<String>>();
        for (Tree<String> tree : rawTestTrees) {
          Tree<String> normalizedTree = treeTransformer.transformTree(tree);
          testTrees.add(normalizedTree);
        }

        out.println("== Testing on test set...");
        f1 = testParser(parser, testTrees, out);
      } else {
        out.println("!!! Invalid part choice: " + partId);
        System.setOut(out);
        return null;
      }

      System.setOut(out);
      String jsonSubmit = "[" + partId + "," + version + "," + f1 + "]";

      return jsonSubmit;
  }

  // ========================= CHALLENGE HELPERS =========================

  private String source(int partId) {
    StringBuffer src = new StringBuffer();
    List<List<String>> src_files = sources();
    if(partId < src_files.size()) {
      List<String> flist = src_files.get(partId - 1);
      for(String fname : flist) {
        try {
          BufferedReader reader = new BufferedReader(new FileReader(fname));
          String line;
          while((line = reader.readLine()) != null) {
            src.append(line);
          }
          reader.close();
          src.append("||||||||");
        } catch (IOException e) {
          System.err.println(String.format("!! Error reading file '%s': %s",
                                            fname, e.getMessage()));
          return src.toString();
        }
      }
    }
    return src.toString();
  }


  private boolean isValidPartId(int partId) {
    List<String> partNames = validParts();
    return (partId >= 1 && partId <= partNames.size() + 1);
  }