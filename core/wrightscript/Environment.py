from RuntimeException import UnboundNameError, InvalidFieldAccessError, AlreadyDefinedError
from Values import Value, Entity, LineNumber
from AST import Function, Label, EntityDefinition
from SyntaxException import FunctionDefinitionError, LabelDefinitionError, EntityDefinitionError


class Environment(object):
    '''
    An Environment captures the actual state of the program, including
    variables, function definitions and labels.
    '''

    def __init__(self, env=None):
        '''The optional environment given will be asked whenever a
        binding was not found. This is useful for realizing scoping,
        as variables may be defined inside a function which will not
        propagate to the lower level.'''
        assert(env is None or isinstance(env, Environment))
        
        self._bindings = dict()
        self._parent = env
        
    def get(self, name):
        '''String -> AST.Node
        
        Receives a string containing the identifier's name (e.g. "x") and
        returns the AST Node saved behind it, which may be everything, from
        a literal value to a label binding. Raises an UnboundNameException
        if the name could not be resolved.'''
        
        if "." in name:
            (entityName, fieldName) = name.split(".", 1)
            entity = self.get(self, entityName)
            return self.getField(entity, fieldName)
        
        value = self._bindings.get(name, None)
        
        if value is None:
            if self._parent is None:
                raise UnboundNameError(name)
            else:
                return self._parent.get(name)
            
        return value
    
    def getField(self, entity, fieldName):
        '''Entity, String -> AST.Node
        
        Returns the value of a field of an entity. Unlike a direct entity.get(),
        this function takes care of nested entity dereferencing.'''
        if not isinstance(entity, Entity):
            raise InvalidFieldAccessError(entity, fieldName)
        
        # Check for nested entity dereferencing (e.g. Ema.mad.filename)
        parts = fieldName.split(".", 1)
        
        fieldValue = entity.get(parts[0])
        
        if len(parts) > 1:
            return self.getField(fieldValue, parts[1])
        else:
            return fieldValue
        
    def isBound(self, name):
        '''String -> Boolean
        
           Returns whether the given identifier name is bound to any
           value in this or a parent environment.'''
        
        if self._bindings.has_key(name):
            return True
        
        if self._parent is None:
            return False
        else:
            return self._parent.isBound(name)
        
    def set(self, name, value, local=False):
        '''Sets the given variable name to the given value. Raises an error
           if the name is bound to a Function or Label.
           
           This methods should only be used with instances of Value.
           For function and label bindings, use the specialized
           methods addFunction, add EntityDefinition and addLabel. They will take care
           that the name is not taken by anything, including variables.
           
           If local is True, an already set variable of a higher scope will not be modified
           and will be shadowed.
           This is the expected setting for parameter bindings of function calls.'''
        
        assert(value is Value)
        self._bind(name, value, local)
        
    def _bind(self, name, value, local=False):
        '''Helper function for set, addFunction and addLabel. Binds the
        given name to the given value.
        
        Raises an InvalidRedeclarationError if the name has already been
        bound to a function or label.'''
        
        if self.isBound(name):
            boundValue = self.get(name)
            
            if isinstance(boundValue, LineNumber):
                raise AlreadyDefinedError(name, "Label")
            if isinstance(boundValue, Function):
                raise AlreadyDefinedError(name, "Function")
            
            # If binding is global, propagate binding one step down
            if not local and not self._bindings.has_key(name):
                self._parent._bind(self, name, value)
            # else: bind locally, as done below for the case of a previously unbound name
            
        self._bindings[name] = value        
        
    def addFunction(self, function):
        '''Adds the given Function instance to the environment.
        
        Raises an FunctionDefinitionError when the name has already been defined (as a variable or otherwise).'''
        assert(isinstance(function, Function))
        
        functionName = function.name().name()
        
        if self.isBound(functionName):
            raise FunctionDefinitionError(functionName, self.get(functionName))
        
        self._bindings[functionName] = function
        
    def addEntityDefinition(self, entityDefinition):
        '''Adds the given Entity definition instance to the environment.
        
        Raises an EntityDefinitionError when the name has already been defined (as a variable or otherwise).'''
        assert(isinstance(entityDefinition, EntityDefinition))
        
        definitionName = entityDefinition.name().name()
        
        if self.isBound(definitionName):
            raise EntityDefinitionError(definitionName, self.get(definitionName))
        
        self._bindings[definitionName] = entityDefinition
        
    def addLabel(self, label, lineNo):
        '''Adds a binding of the given label's identifier to it's LineNumber.
        
        Raises an LabelDefinitionError when the name has already been defined (as a variable or otherwise).'''
        assert(isinstance(label, Label))
        
        labelName = label.name().name()
        
        if self.isBound(labelName):
            raise LabelDefinitionError(labelName, self.get(labelName))
        
        self._bindings[labelName] = LineNumber(int(lineNo))
        
    def __nonzero__(self):
        '''Answers whether the environment contains any bindings.'''
        return bool(self._bindings) or bool(self._parent)
        
        