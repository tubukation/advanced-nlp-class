package nlpclass.util;

/**
 * A generic-typed unordered pair of objects.
 * @author Dan Klein
 */
public class UnorderedPair<F,S> {
  F first;
  S second;

  public F getFirst() {
    return first;
  }

  public S getSecond() {
    return second;
  }

  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof UnorderedPai