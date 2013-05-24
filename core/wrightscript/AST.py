'''
These classes are used for building an abstract syntax tree of Wrightscript.
'''

# Exceptions
class StatementNoOutOfBoundsException:
    def __init__(self, no):
        self._no = no
        
    def __repr__(self):
        return "Statement " + self._no + " does not exist" 

class Node(): pass

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
    # @param lineno The line number.
    def add(self, node, lineno):
        self._statements.add((node, lineno))
        
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
    # Returns the current position of the instruction counter.
    def pos(self):
        return self._pos
    
    ##
    # Moves the instruction pointer to the given position. Does not
    # return the next statement.
    # @param The position to go to. Must be positive and inside the sequence bounds. 
    def goto(self, pos):
        if pos < 0 or pos >= len(self._statements):
            raise StatementNoOutOfBoundsException(pos)
        self._pos = pos

##
# A label is a named position in the code. They can be jumped to
# in goto expressions. The label identifier should be bound to
# the position in the StatementSequence during the semantic parsing
# step. When interpreted, a label does nothing.
class Label(Node):
    
    ##
    # @param identifier String
    def __init__(self, identifier):
        self._name = identifier
    
    ##
    # Returns the identifier of this label as a string.
    def name(self):
            return self._name

##
# Resume jumps to the last position before a goto statement.
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
# will result in an infinite loop.
class Resume(Node): pass