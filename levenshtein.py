import random

 
def lev_del(word):
    r = random.randint(0, len(word) -1)
    w = word[:r] + word[r+1:]
    assert(len(w) == len(word) - 1)
    return w
    
def lev_add(word):
   