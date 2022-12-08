import random

 
def lev_del(word):
    r = random.randint(0, len(word) -1)
    w = word[:r] + word[r+1:]
    assert(len(w) == len(word) - 1)
    return w
    
def lev_add(word):
    l = chr(ord('a') + random.randint(0,25))
    r = random.randint(1, len(word) -1)
    w = word[:r] + l + word[r:]
    assert(len(w) == len(word) + 1)
    return w
    
def lev_subst(word):
    l = chr(ord('a') + random.randint(0,25))
    r = random.randint(1, len(word) -1)
    w = word[:r] + l + word[r+1:]  
    assert(len(w) == len(word))
    return w

def lev2(word):
    r = random.randint(0,2)
    if r == 0: 
        return lev_del(lev_del(word))
    elif r == 1: 
        return lev_add(lev_add