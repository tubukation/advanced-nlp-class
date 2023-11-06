
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