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

    public b