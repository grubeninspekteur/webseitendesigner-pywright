'''
Some helper functions for functional programming style.
'''

def forall(pred, iterable):
    '''
    (x => Boolean) Iterable(x) => Boolean
    
    Returns true if all elements of the iterable fulfill the
    given predicate. An empty iterable will yield true.
    '''
    for elem in iterable:
        if pred(elem) == False:
            return False
        
    return True

def exists(pred, iterable):
    '''
    (x => Boolean) Iterable(x) => Boolean
    
    Returns true if any element of the iterable fullfills the
    given predicate. An empty iterable will yield false.
    '''
    for elem in iterable:
        if pred(elem):
            return True
        
    return False