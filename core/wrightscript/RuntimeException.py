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
        
    def __str__(self):
        return "'" + self._name + "' is not defined"
    
class InvalidFieldAccessError(RuntimeException):
    '''Raised when trying to access a field of a non-entity.'''
    
    def __init__(self, node, name):
        '''node: AST.Node The node that was not an Entity.
           name: String The name of the field.'''
        self._node = node
        self._name = name
        
    def __str__(self):
        return "Non-Entity " + self._node.__class__.__name__ + " has no field '" + self._name + "'"

class UnknownFieldError(RuntimeException):
    '''Raised when accessing an unknown field of an entity.'''
    
    def __init__(self, entity, field):
        self._entity = entity
        self._field = field
        
    def __str__(self):
        return "Entity from template " + self._entity.template() + " has no field " + self._field
        

class AlreadyDefinedError(RuntimeException):
    '''Raised when an identifier bound to a label or function is being
    redifined.'''
    
    def __init__(self, name, definedAs):
        '''name: String
           definedAs: String'''
        self._name = name
        self._definedAs = definedAs
        
    def __str__(self):
        return "Can't change '" + self._name + "', already defined as " + self._definedAs
    
class WrongArgumentNumberError(RuntimeException):
    '''Raised when a function is called with the wrong number of
    arguments.'''
    
    def __init__(self, callable, expected, passed):
        try:
            self.functionName = callable.__name__
        except AttributeError:
            self.functionName = "<unknown>"
        self.callable = callable
        self.expected = expected
        self.passed = passed
    
    def __str__(self):
        try:
            return "Function " + self.functionName + " has exactly " + str(self.expected) + " parameters (" + str(self.passed) + " given)"
        except Exception, e:
            print e
            
class NotAnEntityDefinitionError(RuntimeException):
    def __str__(self):
        return "Invalid instantiation of non-entity"
    
class MissingFieldDeclerationError(RuntimeException):
    def __init__(self, templateName, keysMissing):
        self._templateName = templateName
        self._keysMissing = keysMissing
        
    def __str__(self):
        return self._templateName + " requires the following fields to be set: " + repr(self._keysMissing)
    
class FunctionAsRightValueError(RuntimeException):
    '''Raised when a function is being assigned to a variable. This
    is prevented as this variable could never be set again (the Environment
    would think of it as a Function defined at parsing step).'''
    def __init__(self, funName):
        self._funName = funName
        
    def __str__(self):
        return "Can't assign function " + repr(self._funName)  + " to a field or variable"
    
class NotAFunctionError(RuntimeException):
    '''Raised when a non-function is called.'''
    
    def __init__(self, nonFunction):
        self._nonFunction = nonFunction
    
    def __str__(self):
        return "Invalid call to non function " + repr(self._nonFunction)
    
class Traceback(RuntimeException):
    def __init__(self, exception, lineNo):
        self._exception = exception
        self._lineNo = lineNo
        
    def __str__(self):
        return str(self._exception) + " at line " + repr(self._lineNo)