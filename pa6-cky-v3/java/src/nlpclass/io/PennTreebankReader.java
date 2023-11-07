
package nlpclass.io;

import nlpclass.ling.Tree;
import nlpclass.ling.Trees;
import nlpclass.util.ConcatenationIterator;

import java.util.*;
import java.io.*;

/**
 * @author Dan Klein
 */
public class PennTreebankReader {

  static class TreeCollection extends AbstractCollection<Tree<String>> {

    List<File> files;

    static class TreeIteratorIterator implements Iterator<Iterator<Tree<String>>> {
      Iterator<File> fileIterator;
      Iterator<Tree<String>> nextTreeIterator;

      public boolean hasNext() {
        return nextTreeIterator != null;
      }

      public Iterator<Tree<String>> next() {
        Iterator<Tree<String>> currentTreeIterator = nextTreeIterator;
        advance();
        return currentTreeIterator;
      }

      public void remove() {
        throw new UnsupportedOperationException();
      }

      private void advance() {
        nextTreeIterator = null;
        while (nextTreeIterator == null && fileIterator.hasNext()) {
          try {
            File file = fileIterator.next();
            System.out.println(file.getName());
            nextTreeIterator = new Trees.PennTreeReader(new BufferedReader(new FileReader(file)));
          } catch (FileNotFoundException e) {
          }
        }
      }

      TreeIteratorIterator(List<File> files) {
        this.fileIterator = files.iterator();
        advance();
      }
    }

    public Iterator<Tree<String>> iterator() {
      return new ConcatenationIterator<Tree<String>>(new TreeIteratorIterator(files));
    }

    public int size() {
      int size = 0;
      Iterator i = iterator();
      while (i.hasNext()) {
        size++;
        i.next();
      }