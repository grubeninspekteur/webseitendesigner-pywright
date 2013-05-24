'''
The parser takes a string (presumely from a file) containing Wrightscript
and outputs an abstract syntax tree (AST) of statements.
'''
from ..include.ply import yacc as yacc
from AST import *

# TODO make rules

# note: parse implicit text box as Function('wrightscript', [content])

parser = yacc.yacc()
