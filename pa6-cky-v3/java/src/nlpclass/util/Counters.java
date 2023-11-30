
package nlpclass.util;

import java.util.List;
import java.util.ArrayList;

/**
 * Utility methods related to Counters and CounterMaps.
 *
 * @author Dan Klein
 */
public class Counters {

  public static <E> Counter<E> normalize(Counter<E> counter) {
    Counter<E> normalizedCounter = new Counter<E>();
    double total = counter.totalCount();