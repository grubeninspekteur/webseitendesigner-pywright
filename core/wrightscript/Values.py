'''
When creating certain objects in Wrightscript or when targeting
a label, an instance of one of the classes defined here will be
created and stored inside the environment. 
'''

from AST import Node

class Value(Node):
    def eval(self):
        raise "Internal State Error: Values should not be evaluated"
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

class JumpPosition(Value):
    '''A line number and the associated StatementSequence, usually bound to a label identifier.
    
    The StatementSequence is being recorded to support jumps between included scripts.'''
    
    def __init__(self, lineNo, statementSequence):
        self._lineNo = lineNo
        self._statementSequence = statementSequence
        
    def lineNumber(self):
        return self._lineNo
    
    def statementSequence(self):
        return self._statementSequence
    
    def __repr__(self):
        return repr(self._lineNo)
