'''
This is the lexer for the Wrightscript language. It uses PLY to
parse a given script into tokens. Comments will also be removed
in this step.

Please see http://www.dabeaz.com/ply/ply.html for a documentation
on using PLY.

For using the lexer, try:

from core.wrightscript.lexer import lexer
lexer.input(somedata)

for toc in lexer: ...
'''

from ..include.ply import lex as lex

class ParseException:
    def __init__(self, line, character):
        self.line = line
        self.character = character
        
    def __repr__(self):
        return "Unexpected character '" + str(self.character) + "' in line " + repr(self.line)

# reserved words
reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   'label' : 'LABEL',
   'goto' : 'GOTO',
   'resume' : 'RESUME',
   'exit' : 'EXIT',
   'def' : 'DEF',
   'enddef' : 'ENDDEF',
   'entity' : 'ENTITY',
   'endentity' : 'ENDENTITY',
   'return' : 'RETURN'
}

# Available tokens of Wrightscript
tokens = [
    'NUMBER',
    'STRING',
    'BOOLEAN',
    'IDENTIFIER',
    'NEWLINE',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'PERIOD',
    'LBRACE',
    'RBRACE',
    'COMMA',
    'ASSIGN',
    'COMMENT',
    'MULTCOMMENT'
          ] + list(reserved.values())



# Simple regular expressions
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_PERIOD = r'\.'
t_COMMA = r','
t_ASSIGN = r':='

def t_COMMENT(t):
    r'(\s*)\#.*'
    t.lexer.lineno += t.value.count('\n')

def t_MULTCOMMENT(t):
    r'(\s*)/\*(.|[\r\n])*?\*/'
    t.lexer.lineno += t.value.count('\n')
    # No return value. Token discarded

def t_STRING(t):
    r'"(\\.|[^\"])*"'
    # count line numbers
    # TODO the lexer should be able to do this for me - we shouldn't parse the string twice!
    t.lexer.lineno += t.value.count('\n')
    # TODO regexp should be able to cut the quotes and replace the escape chars - but how? 
    t.value = t.value[1:-1].replace(r'\"', r'"')
    return t

def t_BOOLEAN(t):
    r'true|false'
    if (t.value == 'true'):
        t.value = True
    else:
        t.value = False
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER') # as in PLY example - reduces regExpressions
    return t

def t_NUMBER(t):
    r'\d+(?!\w)'
    # Regexpr searches for a number not folowed by letter or _ to reject invalid identifiers
    t.value = int(t.value)
    return t

# NEWLINEs separate statements
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    
    raise ParseException(t.lexer.lineno, t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
