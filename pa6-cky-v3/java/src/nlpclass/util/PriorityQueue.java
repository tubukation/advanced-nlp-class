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
public class PriorityQueue <E> implements Iterator<E>, Serializable, Cloneable {
  int size;
  int capacity;
  List<E> elements;
  double[] priorities;

  protected void grow(int newCapacity) {
    List<E> newElements = new ArrayList<E>(newCapacity);
    double[] newPriorities = new double[newCapacity];
    if (size > 0) {
      newElements.addAll(elements);
      System.arraycopy(priorities, 0, newPriorities, 0, priorities.length);
    }
    elements = newElements;
    priorities = newPriorities;
    capacity = newCapacity;
  }

  protected int parent(int loc) {
    return (loc - 1) / 2;
  }

  protected int leftChild(int loc) {
    return 2 * loc + 1;
  }

  protected int rightChild(int loc) {
    return 2 * loc + 2;
  }

  protected void heapifyUp(int loc) {
    if (loc ==