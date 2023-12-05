package nlpclass.util;

import java.util.Map;

/**
 * Canonicalizes objects.  Given an object, the intern() method returns a
 * canonical representation of that object, that is, an object which equals()
 * the input.  Furthermore, given two objects x and y, it is guaranteed that if
 * x.equals(y), then intern(x) == intern(y).  The default behavior is that the
 * interner is backed by a HashMap and the canonical version of an object x is
 * simply the first object that equals(x) which is passed to the interner.  In
 * this case, it can be true that intern(x) == x.  The backing map can be
 * specified by passing a MapFactory on construction (though the only standard
 * option which makes much sense is the WeakHashMap, which is slower than a
 * HashMap, but which allows unneeded keys to be reclaimed by the garbage
 * collector).  The source of canonical elements can be changed by specifying an
 * Interner.Factory on construction.
 *
 * @author Dan Klein
 */
public class Interner <T> {
  /**
   * The source of can