'''
Contains all exceptions and errors that may occur during interpretation
of a Wrightscript.
'''

class RuntimeException(Exception):
    '''A class of exceptions that will be thrown during runtime.'''
    pass

class UnboundNameError(RuntimeException):
    '''Raised when trying to access an unbound identifier.'''
    
    def __init__(self, name):
        '''name: String containing the name of the unbound identifier.'''
        self._name = name
        
    def __repr__(self):
        return "Runtime Exception: '" + self._name + "' is not defined"
    
class InvalidFieldAccessError(RuntimeException):
    '''Raised when trying to access a field of a non-entity.'''
    
    def __init(self, node, name):
        '''node: AST.Node The node that was not an Entity.
           name: String The name of the field.'''
        self._node = node
        self._name = name
        
    def __repr__(self):
        return "Runtime Exception: Non-Entity " + self._node.__class__.__name__ + " has no field '" + self._name + "'"
    
class AlreadyDefinedError(RuntimeException):
    '''Raised when an identifier bound to a label or function is being
    redifined.'''
    
    def __init__(self, name, definedAs):
        '''name: String
           definedAs: String'''
        self._name = name
        self._definedAs
        
    def __repr__(self):
        return "Runtime Exception: Can't change '" + self._name + "', already defined as " + self._definedAs