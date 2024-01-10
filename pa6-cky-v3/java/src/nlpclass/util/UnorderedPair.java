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
    if (!(o instanceof UnorderedPair)) return false;

    @SuppressWarnings("unchecked")
    final UnorderedPair pair = (UnorderedPair) o;

    return (((first == null ? pair.first == null : first.equals(pair.first)) && (second == null ? pair.second == null : second.equals(pair.second))) || ((first == null ? pair.second == null : first.equals(pair.second)) && (second == null ? pair.first == null : second.equals(pair