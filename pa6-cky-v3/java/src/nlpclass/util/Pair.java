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
    if (this == o) return true;
    if (!(o instanceof Pair)) return false;
    
    @SuppressWarnings("unchecked")
    final Pair pair = (Pair) o;

    if (first != null ? !first.equals(pair.first) : pair.first 