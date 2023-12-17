package nlpclass.util;

import java.util.Iterator;
import java.util.NoSuchElementException;
import java.util.List;
import java.util.ArrayList;
import java.io.Serializable;

/**
 * A priority queue based on a binary heap.  Note that this implementation does
 * not efficiently support containment, removal, or element promotion
 * (decreaseKey) -- these methods are therefore not yet implemented.
 *
 * @author Dan Klein
 */
public class PriorityQueue <E> i