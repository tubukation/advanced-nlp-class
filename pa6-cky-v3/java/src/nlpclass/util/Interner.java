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
 * option wh