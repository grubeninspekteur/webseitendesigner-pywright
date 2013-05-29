'''
The parser takes a string (presumely from a file) containing Wrightscript
and returns an abstract syntax tree (AST) of statements. It only performs
the syntactic analysis, so don't expect functions to be extracted or label
identifiers to be bound to positions in the StatementSequence.

TODO actually it is wiser to do the semantic analysis (label and function
extraction) in this step as well. I can basically see no harm in doing so,
as all the information required is already present. So a call to Parser::parse
requires an Environment (defaulting to empty).

Also, the AST shouldn't stay an abstract syntax tree but hold the evaluate
code as well, saving a lot of if instanceof(...) clauses in the interp()
function and relying completely on object delegation. However, while this
makes the actual interp() really small, it will blow up the AST objects,
violating seperation of concern (representing the syntax and self-evaluation).

TODO+1 define error symbols as explained in PLY documentation to provide more
information to the user than "Syntax error: Unexpected token on line I don't know"
'''
from ..include.ply import yacc as yacc
from lexer import tokens
from AST import *
import os
from core.wrightscript.AST import CreateEntity

class Parser():
    ##
    # Instance variables:
    # _errors List(SyntaxError) A list of errors
    # PARSETAB_DIR String Where to put the parsetab.py
    # _parser The actual yacc parser
    
    def __init__(self):
        self._errors = list()
        self.PARSETAB_DIR = os.path.dirname(os.path.abspath(__file__))
        self.buildParser()
    
    def resetErrors(self):
        self._errors = list()
        
    def errors(self):
        return self._errors
    
    def hasErrors(self):
        return bool(self._errors)

    def parse(self, script, debug=False):
        '''String => StatementSequence
        
        Parses the given script and returns the
        resulting abstract syntax tree.'''
        self.resetErrors()
        return self._parser.parse(script, debug=debug)

    def buildParser(self):
        ##
        # RULES
        #
        # As PLY does only track line numbers of tokens, we return tuples of (node, lineno)
        # for every statement we require a line number of and extract this information
        # when adding the statement to the StatementSequence.
        
        def p_start_emptyspace(p):
            'start : NEWLINE statements optspace'
            p[0] = p[2]
            
        def p_start(p):
            'start : statements optspace'
            p[0] = p[1]
        
        def p_statements_multiple(p):
            'statements : statements NEWLINE statement'
            (node, lineno) = p[3]
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
            
        def p_expression_assignment(p):
            'expression : IDENTIFIER ASSIGN arg'
            p[0] = (Assignment(Identifier(p[1]), p[3]), p.lineno(1))
            
        def p_expression_assignment_field(p):
            'expression : field_access ASSIGN arg'
            p[0] = (FieldAssignment(p[1], p[3]), p.lineno(2))
            
        def p_expression_conditional(p):
            'expression : IF arg thenexpr elseexpr'
            p[0] = (If(p[2], p[3], p[4]), p.lineno(1))
            
        def p_expression_exit(p):
            'expression : EXIT'
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
            
        def p_statement_entitydef(p):
            'statement : ENTITY IDENTIFIER NEWLINE entity_field_definitions NEWLINE ENDENTITY'
            p[0] = (EntityDefinition(Identifier(p[2]), p[4]), p.lineno(1))
        
        def p_entity_field_definitions_single(p):
            'entity_field_definitions : entity_field_definition'
            p[0] = {p[1][0] : p[1][1]}
            
        def p_entity_field_definitions_multiple(p):
            'entity_field_definitions : entity_field_definitions NEWLINE entity_field_definition'
            p[0] = p[1] # reuse already defined dictionary
            key, value = p[3][0], p[3][1]
            if p[0].has_key(key):
                raise SyntaxError("Invalid redeclaration of entity field " + repr(key))
            p[0][key] = value
            
        def p_entity_field_definition_nodefault(p):
            'entity_field_definition : IDENTIFIER'
            p[0] = (Identifier(p[1]), EntityDefinition.NoDefaultValue())
            
        def p_entity_field_defintion_default(p):
            'entity_field_definition : IDENTIFIER ASSIGN literal'
            p[0] = (Identifier(p[1]), p[3])
        
        def p_expressions_multiple(p):
            '''expressions : expressions NEWLINE expression
                           | expressions NEWLINE returner'''
            (node, lineno) = p[3]
            p[0] = p[1] # reuse statement sequence
            p[0].add(node, lineno)
        
        def p_expressions_single(p):
            '''expressions : expression
                           | returner'''
            ss = StatementSequence()
            (node, lineno) = p[1]
            ss.add(node, lineno)
            p[0] = ss
            
        def p_returner_empty(p):
            'returner : RETURN'
            p[0] = (Return(None), p.lineno(1))
            
        def p_returner_value(p):
            'returner : RETURN arg'
            p[0] = (Return(p[2]), p.lineno(1))
            
        
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
            
        def p_arg_list(p):
            'arg : list'
            p[0] = p[1]
        
        def p_arg_entity_creation(p):
            'arg : entity_creation'
            p[0] = p[1]
            
        def p_arg_literal(p):
            'arg : literal'
            p[0] = p[1]
            
        def p_arg_field_access(p):
            'arg : field_access'
            p[0] = p[1]
            
        def p_field_access_single(p):
            'field_access : IDENTIFIER PERIOD IDENTIFIER'
            p[0] = Identifier(p[1] + '.' + p[3])
            
        def p_field_access_nested(p):
            'field_access : field_access PERIOD IDENTIFIER'
            p[0] = Identifier(p[1].name() + '.' + p[3])
        
        def p_literal_string(p):
            'literal : STRING'
            p[0] = String(p[1])
        
        def p_literal_number(p):
            'literal : NUMBER'
            p[0] = Number(p[1])
        
        def p_literal_boolean(p):
            'literal : BOOLEAN'
            p[0] = Boolean(p[1])
        
        def p_arg_funcall(p):
            'arg : LPAREN funcall RPAREN'
            p[0] = p[2]
        
        def p_list_containing(p):
            '''list : LBRACKET optspace listelems optspace RBRACKET
                    | LBRACKET optspace listelems optspace COMMA RBRACKET'''
            p[0] = CreateList(tuple(p[3]))
        
        def p_list_empty(p):
            'list : LBRACKET optspace RBRACKET'
            p[0] = CreateList(tuple())
            
        def p_listelems_single(p):
            'listelems : arg'
            p[0] = [p[1]]
            
        def p_listelems_listelem(p):
            'listelems : listelems optspace COMMA optspace arg'
            listelems = p[1]
            listelems.append(p[5])
            p[0] = listelems
            
        def p_entity_creation(p):
            'entity_creation : arg LBRACE optspace field_assignments optspace RBRACE'
            'entity_creation : arg LBRACE optspace field_assignments optspace COMMA RBRACE'
            p[0] = CreateEntity(p[1], p[4])
            
        def p_entity_creation_empty(p):
            'entity_creation : arg LBRACE optspace RBRACE'
            p[0] = CreateEntity(p[1], dict())
            
        def p_field_assignments_single(p):
            'field_assignments : IDENTIFIER ASSIGN arg'
            p[0] = {Identifier(p[1]) : p[3]}
            
        def p_field_assignments_multiple(p):
            'field_assignments : field_assignments optspace COMMA optspace IDENTIFIER ASSIGN arg'
            p[0] = p[1]
            key, value = Identifier(p[5]), p[7]
            if p[0].has_key(key):
                raise SyntaxError("Invalid double set of entity field " + repr(key))
            
            p[0][key] = value
        
        def p_optspace(p):
            '''optspace : empty
                        | NEWLINE'''
            pass
        
        def p_empty(p):
            'empty :'
            pass
        
        ##
        # Error handling.
        def p_error(t):
            self._errors.append(TokenError(t))
            # Try reaching the next statement (see PLY documentation for yacc)
            while 1:
                tok = yacc.token()
                if not tok or tok.type == 'NEWLINE': break
            yacc.restart()
        
        self._parser = yacc.yacc(picklefile= self.PARSETAB_DIR + "/parsetab.pickle")

class SyntaxError():
    def __init__(self, cause):
        self._cause = cause
        
    def __repr__(self):
        return "Syntax Error: " + self._cause

class TokenError(SyntaxError):
    def __init__(self, token):
        self._token = token
            
    def token(self):
        return self._token
        
    def __repr__(self):
        if self._token is None:
            return 'Unexpected end of file!'
        else:
            return 'Syntax Error: Unexpected ' + str(self._token.type) + ' ' + repr(self._token.value) + ' at line ' + repr(self._token.lineno)