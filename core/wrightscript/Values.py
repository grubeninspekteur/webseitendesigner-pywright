'''
When creating certain objects in Wrightscript or when targeting
a label, an instance of one of the classes defined here will be
created and stored inside the environment. 
'''
from core.wrightscript.RuntimeException import UnknownFieldError

class Value(object):
    def interp(self, env):
        raise "Internal State Error: Values should not be interpreted"
        return self
    
    def value(self):
        raise NotImplementedError("SubclassResponsibility")
    
    def __eq__(self, other):
        # As "case classes", derived nodes must have the same class to be equal
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__

class NilV(Value):
    def value(self):
        return None

class LiteralV(Value):
    pass

class BooleanV(LiteralV):
    
    ##
    # @param value Boolean
    def __init__(self, value):
        self._value = bool(value)
    
    def value(self):
        return self._value
    
    def __nonzero__(self):
        return self._value
    
    def __str__(self):
        return str(self._value)
    
    def __int__(self):
        return int(self._value)    
    
    def __repr__(self):
        return repr(self._value)

class NumberV(LiteralV):
    
    ##
    # @param value A positive Integer
    def __init__(self, value):
        assert(value >= 0)
        self._value = int(value)
    
    def value(self):
        return self._value
    
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

class StringV(LiteralV):
    ##
    # @param value A string
    def __init__(self, value):
        self._value = str(value)
    
    def value(self):
        return self._value
    
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
    '''A List created by the CreateList expression. Lists in Wrightscript are immutable.'''
    
    def __init__(self, theList):
        '''Creates a new list from theList iterable.'''
        self._value = tuple(theList)
        
    def value(self):
        return self._value
    
    def __repr__(self):
        return '[' + ', '.join(str(elem) for elem in self._value) + ']'
    
class Entity(Value):
    '''An Entity created by the CreateEntity expression.'''
    def __init__(self, template, entityDictionary):
        '''Creates a new Entity Definition.
        
        template: str Name of the definition used
        entityDictionary: str->Value pairs'''
        
        self._value = entityDictionary
        self._template = template
        
    def template(self):
        return self._template
    
    def value(self):
        return self._value
    
    def get(self, index):
        if not self._value.has_key(index):
            raise UnknownFieldError(self, index)
        return self._value[index]
    
    def set(self, index, value):
        if not self._value.has_key(index):
            raise UnknownFieldError(self, index)
        self._value[index] = value

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
    
    def value(self):
        return (self._lineNo, self._statementSequence)
    
    def __repr__(self):
        return repr(self._lineNo)
