'''
These classes are used for building an abstract syntax tree of Wrightscript.
'''
from core.functional import forall
from Callable import Callable
from ControlFlowEvent import *
from itertools import imap, izip
from core.wrightscript.RuntimeException import NotAnEntityDefinitionError,\
    MissingFieldDeclerationError, FunctionAsRightValueError,\
    WrongArgumentNumberError, NotAFunctionError, RuntimeException, Traceback

'''ATTENTION: More imports at the bottom of this file.'''

class Node():
    def __eq__(self, other):
        # As "case classes", derived nodes must have the same class to be equal
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__
    
    def interp(self, env):
        '''Evaluates this node with the given Environment env and returns the result of this evaluation.'''
        raise NotImplementedError("Subclass Responsibility")

# Exceptions
class StatementNoOutOfBoundsException(Exception):
    def __init__(self, no):
        self._no = no
        
    def __str__(self):
        return "Statement " + repr(self._no) + " does not exist" 

##
# A named entity.
class Identifier(Node):
    def __init__(self, name):
        self._name = name
    
    def name(self):
        return self._name
    
    def __repr__(self):
        return self._name
    
    def __hash__(self):
        return hash(self._name)
    
    def interp(self, env):
        return env.get(self._name)

class Literal(Node):
    pass

##
# A Boolean value (true or false).
class Boolean(Literal):
    ##
    # @param value Boolean
    def __init__(self, value):
        self._value = bool(value)
    
    def __repr__(self):
        return 'Boolean(' + str(self._value) + ')'
    
    def interp(self, env):
        return BooleanV(self._value)

##
# A Number. Currently only positive integers are allowed.
class Number(Literal):
    ##
    # @param value A positive Integer
    def __init__(self, value):
        assert(value >= 0)
        self._value = int(value)
    
    def __repr__(self):
        return 'Number(' + str(self._value) + ')'
    
    def __hash__(self):
        return hash(self._value)
    
    def interp(self, env):
        return NumberV(self._value)


##
# The AST representation of a String.
class String(Literal):
    ##
    # @param value A string
    def __init__(self, value):
        self._value = str(value)
    
    def __repr__(self):
        return 'String("' + self._value + '")'
    
    def __hash__(self):
        return hash(self._value)
    
    def interp(self, env):
        return StringV(self._value)
    
##
# Holds the statement sequence as a list.
# 
class StatementSequence(Node):

    def __init__(self):
        self._statements = []
        self._lineNoToPos = dict()
        self._pos = -1
        self._resumeAdress = None
        self._resumeSequence = None
        
    ##
    # Adds a statement to the sequence.
    # @param node The AST node to add to the sequence.
    # @param lineno The line number. May be omitted for testing purpose.
    def add(self, node, lineno=-1):
        self._statements.append((node, lineno))
        self._lineNoToPos[lineno] = len(self._statements) - 1
        
    ##
    # Rewinds the internal statement pointer.
    def rewind(self):
        self._pos = -1
        
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
            return self._statements[self._pos]
    
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
    
    def gotoLine(self, lineNo, resumeSequence, resumeAdress):
        self.goto(self._lineNoToPos[lineNo])
        self._resumeSequence = resumeSequence
        self._resumeAdress = resumeAdress
        
    def resume(self, resumeAdress):
        self.goto(resumeAdress)
    ##
    # Returns a dictionary of the statements. It contains
    # tuples of (statement, lineno).
    def asList(self):
        return self._statements
        
    def __repr__(self):
        min_lineno_width = len(str(max(lineno for (_, lineno) in self._statements)))
        fmt = "%" + str(min_lineno_width) + "d"
        return "\n" + '\n'.join((fmt % lineno) + ': ' + repr(stmt) for (stmt, lineno) in self._statements)
    
    def __eq__(self, other):
        if isinstance(other, StatementSequence) == False:
            return False
        
        my_statements = [statement for (statement, _) in self._statements]
        other_statements = [statement for (statement, _) in other.asList()]
        
        return my_statements == other_statements
    
    def interp(self, env):
        stmt = self.next()
        
        lastValue = NilV()
        
        # TODO the current goto implementation uses recursion, which may cause a StackOverflow, as
        # python has no tail call recursion.
        # Maybe propagate it to a higher level of interpretation?
        # or have a look at some of the articles about this in python. Is this even possible with try...except?
        # or disallow cross-statement jumps (so no jump to included scripts)
        # or evaluate includes at parse time and rather bind the jumps to the pos than the lineNumber
        try:
            while not stmt is None:
                (node, lineno) = stmt
                try:
                    lastValue = node.interp(env)
                except RuntimeException, e:
                    raise Traceback(e, lineno)
                
                stmt = self.next()
        except ResumeEvent, e:
            if self._resumeSequence is None:
                # no Resume available, just proceed with execution
                return self.interp(self, env)
            else:
                self._resumeSequence.resume(self._resumeAdress)
                return self._resumeSequence.interp(env)
        
        except GotoEvent, e:
            (lineNo, ss) = e.jumpPosition().value()
            ss.gotoLine(lineNo, self, self._pos)
            return self.interp(env)
        
        return lastValue
        
            

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
    
    def __hash__(self):
        return hash(self._name)
    
    def interp(self, env):
        return self

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
    
    def interp(self, env):
        raise ResumeEvent()

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
    
    def interp(self, env):
        raise GotoEvent(env.get(self._target.name()))

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
    
    def interp(self, env):
        if bool(self._testExpr.interp(env)):
            return self._thenExpr.interp(env)
        elif self.hasElseExpr():
            return self._elseExpr.interp(env)
        
        return NilV()

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
    
    def interp(self, env):
        fun = self._funExpr.interp(env)
        
        if not callable(fun):
            raise NotAFunctionError(self._funExpr)
        
        return fun(map(lambda arg: arg.interp(env), self._args), env)

##
# A function definition consists of a name, a list of
# parameter identifiers and a StatementSequence.
# Parameters will shadow variables outside
# of the function's scope. 
class Function(Node, Callable):
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
    
    def interp(self, env):
        return self
    
    def __name__(self):
        return self._name.name()
    
    def __call__(self, args, env):
        if len(args) != len(self._parameters):
            raise WrongArgumentNumberError(self, len(self._parameters), args)
        
        funEnv = Environment(env)
        for boundId, arg in izip(self._parameters, args):
            funEnv.set(boundId.name(), arg, local=True)
        
        try:
            return self._body.interp(funEnv)
        except ReturnEvent, e:
            return e.value()

##
# Stops execution of the current Script.
class Exit(Node):
    def __repr__(self):
        return 'EXIT'
    
    def interp(self, env):
        raise ExitEvent()
    
##
# Jumps out of a function.
class Return(Node):
    def __init__(self, value):
        self._value = value
    
    def value(self):
        return self._value
    
    def __repr__(self):
        return 'RETURN ' + repr(self._value)
    
    def interp(self, env):
        if self._value is None:
            raise ReturnEvent(None)
        else:
            raise ReturnEvent(self._value.interp(env))
    
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
    
    def interp(self, env):
        return List(imap(lambda elem: elem.interp(env), self._value))
    
##
# An assignment assigns a variable a new value, e.g.
#
# x := (add x 1)
#
class Assignment(Node):
    ##
    # @param lhs An Identifier representing the
    #                   variable to assign the value to
    # @param value Node The (unevaluated) value       
    def __init__(self, identifier, value):
        self._lhs = identifier
        self._rhs = value
        
    def leftHandSide(self):
        return self._lhs
    
    def rightHandSide(self):
        return self._rhs
    
    def __repr__(self):
        return repr(self._lhs) + ' := ' + repr(self._rhs)
    
    def interp(self, env):
        rhsV = self._rhs.interp(env)
        if callable(rhsV):
            raise FunctionAsRightValueError(rhsV.__name__)
        env.set(self._lhs.name(), rhsV)
        
        return rhsV

##
# An assignment where the left hand side is the
# field of an entity, e.g.
#
# Box.color := Blue
#
class FieldAssignment(Assignment):
    ##
    # @param fieldname The complete field identifier (including all dots)
    # @param value Node the (unevaluated) value
    def __init__(self, fieldname, value):
        self._lhs = fieldname
        self._rhs = value

##
# Defines an entity. An entity is like a struct from c++. It
# is a closed container with mutable entries. All fields
# defined in this statement must be present when instantiating
# an entity, however default values are allowed.
class EntityDefinition(Node):
    
    ##
    # Class that represents a field that has no default value.
    class NoDefaultValue():
        def __repr__(self):
            return 'Nil'
        
        def __eq__(self, other):
            return isinstance(other, EntityDefinition.NoDefaultValue)

    ##
    # @param name Identifier containing the entity's name.
    # @param dictionaryOfFields A dictionary mapping Identifiers to Literals
    #                           or NoDefault nodes.
    def __init__(self, name, dictionaryOfFields):
        self._name = name
        self._fields = dictionaryOfFields
    
    ##
    # @return Identifier name of the entity definition
    def name(self):
        return self._name
    
    def fields(self):
        return self._fields
    
    def __repr__(self):
        str = 'ENTITY ' + repr(self._name) + ' {\n' + repr(self._fields) + '\n}'
        return str
    
    ##
    # Returns whether the given list of field Identifiers, representing
    # the fields that are set during instantiation of an entity, is valid
    # for this Entity definition.
    #
    # A entity instantiation is valid if and only if all fields without
    # default values are set.
    def isValidInstantiation(self, listOfFieldsToSet):
        fieldsToSet = set(listOfFieldsToSet)
        fieldsDeclared = set(self._fields.keys())
        
        unsetFields = fieldsDeclared.difference(fieldsToSet)
        
        return forall(lambda field: not isinstance(self._fields[field], EntityDefinition.NoDefaultValue), unsetFields)
    
    def getMissingFields(self, listOfFieldsToSet):
        '''Returns a list of missing fields.'''
        fieldsToSet = set(listOfFieldsToSet)
        fieldsDeclared = set(self._fields.keys())
        
        unsetFields = fieldsDeclared.difference(fieldsToSet)
        
        return filter(lambda field: isinstance(self._fields[field], EntityDefinition.NoDefaultValue), unsetFields)
        
    def interp(self, env):
        return self

##
# Creates an entity.
class CreateEntity(Node):
        ##
        # @param template The EntityDefinition (or an identifier referring to it)
        # @param dictionaryOfAssignments A dictionary mapping Identifiers to (unevaluated) values
        def __init__(self, template, dictionaryOfAssignments):
            self._template = template
            self._assignments = dictionaryOfAssignments
            
        def template(self):
            return self._template
        
        def assignments(self):
            return self._assignments
        
        def __repr__(self):
            return repr(self._template) + "{" + repr(self._assignments) + "}"
        
        def interp(self, env):
            '''Creates an Entity from the dictionary within plus required defaults of
            the definition.
            
            Note that the order in which the values are interpreted depends on
            the underlying Python implementation. It is not wise to rely on the order, e.g.
            SomeEntity {(fun1), (fun2)} may or may not call fun2 first. You should therefore
            keep functions with side effects outside of an entity instantiation statement.'''
            
            entityDefinition = self._template.interp(env)
            
            if not isinstance(entityDefinition, EntityDefinition):
                raise NotAnEntityDefinitionError()
            
            if not entityDefinition.isValidInstantiation(self._assignments.keys()):
                raise MissingFieldDeclerationError(entityDefinition.name().name(),
                                              entityDefinition.getMissingFields(self._assignments.keys()))
            
            fields = dict()
            requiredDefaults = set(self._assignments.keys()).difference(set(entityDefinition.fields().keys()))
            
            for key in requiredDefaults:
                fields[key.name()] = entityDefinition.fields()[key].interp(env)
            
            for identifier, value in self._assignments:
                rhs = value.interp(env)
                if callable(rhs):
                    raise FunctionAsRightValueError(rhs.__name__)
                fields[identifier.name()] = rhs 
            
            return Entity(fields)

# Delayed import due to cyclic dependency          
from Values import *
from core.wrightscript.Environment import Environment