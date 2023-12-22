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
    if (loc == 0) return;
    int parent = parent(loc);
    if (priorities[loc] > priorities[parent]) {
      swap(loc, parent);
      heapifyUp(parent);
    }
  }

  protected void heapifyDown(int loc) {
    int max = loc;
    int leftChild = leftChild(loc);
    if (leftChild < size()) {
      double priority = priorities[loc];
      double leftChildPriority = priorities[leftChild];
      if (leftChildPriority > priority)
        max = leftChild;
      int rightChild = rightChild(loc);
      if (rightChild < size()) {
        double rightChildPriority = priorities[rightChild(loc)];
        if (rightChildPriority > priority && rightChildPriority > leftChildPriority)
          max = rightChild;
      }
    }
    if (max == loc)
      return;
    swap(loc, max);
    heapifyDown(max);
  }

  protected void swap(int loc1, int loc2) {
    double tempPriority = priorities[loc1];
    E tempElement = elements.get(loc1);
    priorities[loc1] = priorities[loc2];
    elements.set(loc1, elements.get(loc2));
    priorities[loc2] = tempPriority;
    elements.set(loc2, tempElement);
  }

  protected void removeFirst() {
    if (size < 1) return;
    swap(0, size - 1);
    size--;
    elements.remove(size);
    heapifyDown(0);
  }

  /**
   * Returns true if the priority queue is non-empty
   */
  public boolean hasNext() {
    return ! isEmpty();
  }

  /**
   * Returns the element in the queue with highe