package nlpclass.util;

/**
 * A generic-typed pair of objects.
 * @author Dan Klein
 */
public class Pair<F,S> {
  F first;
  S second;

  public F getFirst() {
    return first;
  }

  public S getSecond() {
    return second;
  }

  public boolean equals(Object o) {
    if (this == o) ret