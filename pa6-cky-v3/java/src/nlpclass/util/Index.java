
package nlpclass.util;

import java.util.*;

/**
 * Maintains a two-way map between a set of objects and contiguous integers from
 * 0 to the number of objects.  Use get(i) to look up object i, and
 * indexOf(object) to look up the index of an object.
 *
 * @author Dan Klein
 */
public class Index <E> extends AbstractList<E> {