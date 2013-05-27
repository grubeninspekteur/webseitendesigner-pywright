'''
These classes are used for building an abstract syntax tree of Wrightscript.
'''


# Exceptions
class StatementNoOutOfBoundsException:
    def __init__(self, no):
        self._no = no
        
    def __repr__(self):
        return "Statement " + self._no + " does not exist" 

class Node():
    def __eq__(self, other):
        if isinstance(other, Node) == False: return False
        return self.__dict__ == other.__dict__

##
# A named entity.
class Identifier(Node):
    def __init__(self, name):
        self._name = name
    
    def name(self):
        return self._name
    
    def __repr__(self):
        return self._name

##
# The literal types are also defined as nodes as we may want to
# redefine the type conversion rules. For now, type conversion
# follows Python's rules.
##

class Literal(Node):
    pass

##
# A Boolean value (true or false).
class Boolean(Literal):
    ##
    # @param value Boolean
    def __init__(self, value):
        self._value = bool(value)
    
    def __bool__(self):
        return self._value
    
    def __str__(self):
        return str(self._value)
    
    def __int__(self):
        return int(self._value)
    
    def __repr__(self):
        return 'Boolean(' + str(self._value) + ')'

##
# A Number. Currently only positive integers are allowed.
class Number(Literal):
    ##
    # @param value A positive Integer
    def __init__(self, value):
        assert(value >= 0)
        self._value = int(value)
        
    def __bool__(self):
        return bool(self._value)
    
    def __str__(self):
        return str(self._value)
    
    def __int__(self):
        return self._value
    
    def __repr__(self):
        return 'Number(' + str(self._value) + ')'


##
# The AST representation of a String.
class String(Literal):
    ##
    # @param value A string
    def __init__(self, value):
        self._value = str(value)
        
    def __bool__(self):
        return bool(self._value)
    
    def __str__(self):
        return self._value
    
    def __int__(self):
        return int(self._value)
    
    def __repr__(self):
        return 'String("' + self._value + '")'
    
##
# Holds the statement sequence as a list.
# 
class StatementSequence(Node):

    def __init__(self):
        self._statements = []
        self._pos = -1
        
    ##
    # Adds a statement to the sequence.
    # @param node The AST node to add to the sequence.
    # @param lineno The line number. May be omitted for testing purpose.
    def add(self, node, lineno=-1):
        self._statements.append((node, lineno))
        
    ##
    # Rewinds the internal statement pointer.
    def rewind(self):
        self._pos = 0
        
    ##
    # Returns the next sequence and increases
    # the instruction counter.
    #
    # @return A tuple (statement, lineno)
    def next(self):
        self._pos = self._pos + 1
        if self._pos >= len(self._statements):
            return None
        else:
            return self._statements(self._pos)
    
    ##
    # Returns the current statement. The usage
    # of this is discouraged, better use next.
    #
    # @return A tuple (statement, lineno)
    def current(self):
        if self._pos >= len(self._statements):
            return None
        else:
            return self._statements(self._pos)    
    ##
    # Returns the current position of the instruction counter,
    # that is, the position of the statement returned by next.
    def pos(self):
        return self._pos
    
    ##
    # Moves the instruction pointer to the given position. Does not
    # return the next statement. Note that when executing next, the
    # statement immediately following the given position is returned.
    # As goto statements usually point
    # @param The position to go to. Must be positive and inside the sequence bounds. 
    def goto(self, pos):
        if pos < 0 or pos >= len(self._statements):
            raise StatementNoOutOfBoundsException(pos)
        self._pos = pos
    
    ##
    # Returns a dictionary of the statements. It contains
    # tuples of (statement, lineno).
    def asList(self):
        return self._statements
        
    def __repr__(self):
        min_lineno_width = len(str(max(lineno for (_, lineno) in self._statements)))
        fmt = "%" + str(min_lineno_width) + "d"
        return '\n'.join((fmt % lineno) + ': ' + repr(stmt) for (stmt, lineno) in self._statements)
    
    def __eq__(self, other):
        if isinstance(other, StatementSequence) == False:
            return False
        
        my_statements = [statement for (statement, _) in self._statements]
        other_statements = [statement for (statement, _) in other.asList()]
        
        return my_statements == other_statements
        
        
            

##
# A label is a named position in the code. They can be jumped to
# in goto expressions. The label identifier should be bound to
# the label's position in the StatementSequence during the semantic
# parsing step. When interpreted, a label does nothing.
class Label(Node):
    
    ##
    # @param identifier Identifier of this label
    def __init__(self, identifier):
        self._name = identifier
    
    ##
    # Returns the identifier of this label.
    def name(self):
            return self._name
        
    def __repr__(self):
        return 'LABEL ' + repr(self._name)

##
# Resume jumps to the last position of a goto statement.
# Unlike functions, gotos can't be stacked, e.g.
#
# goto c
# label a
# resume
# label b
# goto a
# resume
# label c
# goto b
# 
# will result in an infinite loop (the resume under label b will jump to itself).
#
# You should jump with StatementSequence::goto to the goto's
# position, because StatementSequence::next will return the
# statement immediately following it.
class Resume(Node):
    def __repr__(self):
        return 'RESUME'

##
# Goto points to a label identifier. When executed, the return
# adress, used for resume statements, should be set to the goto
# statement's position. Then the instruction counter of StatementSequence
# shall be set to the value of the label's identifier.
class Goto(Node):
    
    ##
    # @param indentifier Identifier The target Identifier
    def __init__(self, identifier):
        self._target = identifier
    
    ##
    # Returns the target identifier of the goto statement.
    # @return Identifier
    def target(self):
        return self._target
    
    def __repr__(self):
        return 'GOTO ' + repr(self._target)

##
# If tests an argument (which may be the result of a function call)
# and executes thenExpr if it is true, otherwise elseExpr.
class If(Node):
    
    ##
    # @param testExpr The Node that should be tested for it's boolean value.
    # @param thenExpr The Node that will be executed if testExpr evaluates to true.
    # @param elseExpr The Node that will be executed if testExpr evaluates to false. May be None.
    def __init__(self, testExpr, thenExpr, elseExpr):
        self._testExpr = testExpr
        self._thenExpr = thenExpr
        self._elseExpr = elseExpr
        
    def testExpr(self):
        return self._testExpr
    
    def thenExpr(self):
        return self._thenExpr
    
    def elseExpr(self):
        return self._elseExpr
    
    def hasElseExpr(self):
        return self._elseExpr != None
    
    def __repr__(self):
        str = 'IF ' + repr(self._testExpr) + ' THEN ' + repr(self._thenExpr)
        if self.hasElseExpr():
            str = str + ' ELSE ' + repr(self._elseExpr)
        return str

##
# A Call calls a function with the given arguments.  
class Call(Node):
    ##
    # @param funExpr Function expression or Identifier of it
    # @param args A list of function arguments
    def __init__(self, funExpr, args=[]):
        self._funExpr = funExpr
        self._args = args
        
    def funExpr(self):
        return self._funExpr
    
    def args(self):
        return self._args
    
    def __repr__(self):
        return repr(self._funExpr) + '(' + ', '.join(repr(arg) for arg in self._args) + ')'

##
# A function definition consists of a name, a list of
# parameter identifiers and a StatementSequence.
# Parameters will shadow variables outside
# of the function's scope. 
class Function(Node):
    ##
    # @param name Identifier
    # @param parameters Listof(Identifier)
    # @param body StatementSequence
    def __init__(self, name, parameters, body):
        self._name = name
        self._parameters = parameters
        self._body = body
        
    def name(self):
        return self._name
    
    def parameters(self):
        return self._parameters
    
    def body(self):
        return self._body
    
    def __repr__(self):
        return 'DEF ' + repr(self._name) + '(' + ', '.join(repr(param) for param in self._parameters) + ') {\n' + repr(self._body) + '\n}'

##
# Stops execution of the current Script.
class Exit(Node):
    def __repr__(self):
        return 'EXIT'
    
##
# Jumps out of a function.
class Return(Node):
    def __init__(self, value):
        self._value = value
    
    def value(self):
        return self._value
    
    def __repr__(self):
        return 'RETURN ' + repr(self._value)
    
##
# A list over several (unevaluated) nodes. On interpretation, the list elements
# should be evaluated immediately (like for function arguments), so
# the following:
#
# x := 42
# l := [x]
# x := 0
#
# print x
#
# prints 42.
class CreateList(Node):
    def __init__(self, listOfNodes):
        self._value = listOfNodes
        
    def list(self):
        return self._value
    
    def __repr__(self):
        return repr(self._value)