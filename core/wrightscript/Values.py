'''
When creating certain objects in Wrightscript or when targeting
a label, an instance of one of the classes defined here will be
created and stored inside the environment. 
'''

from AST import Node

class Value(Node):
    def eval(self):
        # TODO consider raising an error, as normally values should not be evaluated
        return self

class BooleanV(Value):
    ##
    # @param value Boolean
    def __init__(self, value):
        self._value = bool(value)
    
    def __nonzero__(self):
        return self._value
    
    def __str__(self):
        return str(self._value)
    
    def __int__(self):
        return int(self._value)    
    
    def __repr__(self):
        return repr(self._value)

class NumberV(Value):
    
    ##
    # @param value A positive Integer
    def __init__(self, value):
        assert(value >= 0)
        self._value = int(value)
    
    def __nonzero__(self):
        return bool(self._value)
    
    def __str__(self):
        return str(self._value)
    
    def __int__(self):
        return self._value
    
    def __hash__(self):
        return hash(self._value)
    
    def __repr__(self):
        return repr(self._value)

class StringV(Value):
    ##
    # @param value A string
    def __init__(self, value):
        self._value = str(value)
        
    def __nonzero__(self):
        return bool(self._value)
    
    def __str__(self):
        return self._value
    
    def __int__(self):
        return int(self._value)
    
    def __repr__(self):
        return self._value
    
    def __hash__(self):
        return hash(self._value)

class List(Value):
    '''A List created by the CreateList expression.'''
    pass # TODO

class Entity(Value):
    '''An Entity created by the CreateEntity expression.'''
    pass # TODO

class LineNumber(Value):
    '''A line number, usually bound to a label identifier.'''
    def __init__(self, lineNo):
        self._lineNo = lineNo
        
    def value(self):
        return self._lineNo
    
    def __repr__(self):
        return repr(self._lineNo)
