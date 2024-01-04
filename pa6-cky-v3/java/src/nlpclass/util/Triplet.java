package nlpclass.util;

/**
 * A generic-typed tiplet of objects.
 * @author Paul Baumstarck
 */
public class Triplet<F,S,T> {
    F first;
    S second;
    T third;

    public F getFirst() {
        return first;
    }

    public S getSecond() {
        return second;
    }

    public T getThird() {
        return third;
    }

    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Triplet)) return false;

        @SuppressWarnings("unchecked")
        final Triplet triplet = (Triplet) o;