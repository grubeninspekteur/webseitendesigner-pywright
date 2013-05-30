'''Exceptions that are thrown during the parsing step.'''

class SyntaxException(Exception):
    def __init__(self, cause):
        self._cause = cause
        
    def __repr__(self):
        return "Syntax Error: " + self._cause

class TokenError(SyntaxException):
    def __init__(self, token):
        self._token = token
        if token is None:
            self._cause = 'Unexpected end of file!'
        else:
            self._cause = 'Unexpected ' + str(token.type) + ' ' + repr(token.value) + ' at line ' + repr(token.lineno)
            
class FunctionDefinitionError(SyntaxException):
    def __init__(self, functionName, boundValue):
        self._cause = "Can't declare function '" + functionName + "', identifier already bound to an instance of " + boundValue.__class__.__name__
        
class LabelDefinitionError(SyntaxException):
    def __init__(self, labelName, boundValue):
        self._cause = "Can't declare label '" + labelName + "', identifier already bound to an instance of " + boundValue.__class__.__name__
        
class EntityDefinitionError(SyntaxException):
    def __init__(self, templateName, boundValue):
        self._cause = "Can't declare label '" + templateName + "', identifier already bound to an instance of " + boundValue.__class__.__name__