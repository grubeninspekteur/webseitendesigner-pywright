'''
The parser takes a string (presumely from a file) containing Wrightscript
and returns an abstract syntax tree (AST) of statements. It only performs
the syntactic analysis, so don't expect functions to be extracted or label
identifiers to be bound to positions in the StatementSequence. 
'''
from ..include.ply import yacc as yacc
from lexer import tokens
from AST import *

##
# RULES
#
# As PLY does only track line numbers of tokens, we return tuples of (node, lineno)
# for every statement we require a line number of and extract this information
# when adding the statement to the StatementSequence.

def p_start_emptyspace(p):
    'start : NEWLINE statements'
    p[0] = p[2]
    
def p_start(p):
    'start : statements'
    p[0] = p[1]

def p_statements_multiple(p):
    'statements : statements NEWLINE optspace statement'
    (node, lineno) = p[4]
    p[0] = p[1] # reuse statement sequence
    p[0].add(node, lineno)

def p_statements_single(p):
    'statements : statement'
    ss = StatementSequence()
    (node, lineno) = p[1]
    ss.add(node, lineno)
    p[0] = ss

def p_statement_expression(p):
    'statement : expression'
    p[0] = p[1]

def p_statement_label(p):
    'statement : LABEL IDENTIFIER'
    p[0] = (Label(Identifier(p[2])), p.lineno(1))

def p_expression_funcall(p):
    'expression : IDENTIFIER args'
    p[0] = (Call(Identifier(p[1]), p[2]), p.lineno(1))
    
def p_expression_implicittb(p):
    'expression : STRING'
    p[0] = (Call(Identifier('textbox'), [String(p[1])]), p.lineno(1))
    
def p_statement_resume(p):
    'statement : RESUME'
    p[0] = (Resume(), p.lineno(1))

def p_statement_goto(p):
    'statement : GOTO IDENTIFIER'
    p[0] = (Goto(Identifier(p[2])), p.lineno(1))
    
def p_expression_conditional(p):
    'statement : IS arg thenexpr elseexpr'
    p[0] = (Is(p[2], p[3], p[4]), p.lineno(1))
    
def p_expression_exit(p):
    'statement : EXIT'
    p[0] = (Exit(), p.lineno(1))
    
def p_statement_fundef(p):
    'statement : DEF IDENTIFIER params NEWLINE expressions NEWLINE ENDDEF'
    p[0] = (Function(Identifier(p[2]), p[3], p[5]), p.lineno(1))

def p_params_empty(p):
    'params : empty'
    p[0] = list()
    
def p_params(p):
    'params : params IDENTIFIER'
    paramlist = p[1]
    paramlist.append(Identifier(p[2]))
    p[0] = paramlist

def p_expressions_single(p):
    'expressions : optspace expression optspace'
    ss = StatementSequence()
    (node, lineno) = p[1]
    ss.add(node, lineno)
    p[0] = ss

def p_expressions_multiple(p):
    'expressions : expressions NEWLINE optspace expression'
    (node, lineno) = p[3]
    p[0] = p[1] # reuse statement sequence
    p[0].add(node, lineno)
    
def p_expressions_return_empty(p):
    'expressions : expressions NEWLINE RETURN'
    p[0] = (Return(None), p.lineno(2))
    
def p_expressions_return_value(p):
    'expressions : expressions NEWLINE RETURN arg'
    p[0] = (Return(p[4]), p.lineno(2))
    

def p_thenexpr(p):
    '''thenexpr : GOTO IDENTIFIER
                | funcall'''
    if p[1] == 'goto':
        p[0] = Goto(Identifier(p[2]))
    else:
        p[0] = p[1]

def p_elseexpr(p):
    '''elseexpr : ELSE thenexpr
                | empty'''
    if p[1] == 'else':
        p[0] = p[2]
    else:
        p[0] = None


# Doubled for efficient lineno counting of statements; see PLY documentation for details.
def p_funcall(p):
    'funcall : IDENTIFIER args'
    p[0] = Call(Identifier(p[1]), p[2])
    
def p_args_empty(p):
    'args : empty'
    p[0] = list()

def p_args_arg(p):
    'args : args arg'
    arglist = p[1]
    arglist.append(p[2])
    p[0] = arglist
    
def p_arg_identifier(p):
    'arg : IDENTIFIER'
    p[0] = Identifier(p[1])
    
def p_arg_string(p):
    'arg : STRING'
    p[0] = String(p[1])

def p_arg_number(p):
    'arg : NUMBER'
    p[0] = Number(p[1])

def p_arg_boolean(p):
    'arg : BOOLEAN'
    p[0] = Boolean(p[1])

def p_arg_funcall(p):
    'arg : LPAREN funcall RPAREN'
    p[0] = p[2]

def p_optspace(p):
    '''optspace : empty
                | NEWLINE'''
    pass

def p_empty(p):
    'empty :'
    pass

##
# Error handling.

class SyntaxError():
    def __init__(self, token):
        self._token = token
        
    def token(self):
        return self._token
    
    def __repr__(self):
        return 'Syntax Error: Unexpected ' + repr(self._token.type) + ' at line ' + repr(self._token.lineno)

errors = list()

def p_error(t):
    errors.append(SyntaxError(t))
    # Try reaching the next statement (see PLY documentation for yacc)
    while 1:
        tok = yacc.token()
        if not tok or tok.type == 'NEWLINE': break
    yacc.restart()
    
# Build the parser
_parser = yacc.yacc()

def resetErrors():
    errors = list()

def parse(script):
    '''String => StatementSequence
    
    Parses the given script and returns the
    resulting abstract syntax tree.'''
    resetErrors()
    return _parser.parse(script)