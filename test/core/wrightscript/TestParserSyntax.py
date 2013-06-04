'''
Tests the syntactical aspect of the parser that creates an Abstract Syntax
Tree from Wrightscript.
'''
import unittest
import os
from core.wrightscript.parser import Parser
from core.wrightscript.SyntaxException import SyntaxException
from core.wrightscript.AST import *
from core.functional import forall

def getScriptFromFile(scriptname):
    '''Helper function that retrieves a testfile from the samples directory.'''
    f = open(os.path.dirname(os.path.abspath(__file__)) + '/samples/' + scriptname + '.ws', 'r')
    str = f.read()
    f.close()
    return str

class TestParserSyntax(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        
    
    def _parsed(self, scriptname):
        return self.parser.parse(getScriptFromFile(scriptname))
    
    def _textbox(self, string):
        return Call(Identifier('textbox'), [String(string)])
    
    def _label(self, string):
        return Label(Identifier(string))
    
    def _goto(self, string):
        return Goto(Identifier(string))
    
    def _expectErrors(self, stringToParse, message=""):
        self.parser.parse(stringToParse)
        self.assertTrue(self.parser.hasErrors(), message)
        
    def assertNoParseErrors(self):
        self.assertFalse(self.parser.hasErrors(), self.parser.errors())
        
    def testOneLiner(self):
        '''Tests that a single line statement is recognized.'''
        ss = StatementSequence()
        ss.add(self._label('test'))
        
        input = 'label test'
        
        self.assertEqual(self.parser.parse(input), Root(ss))
    
    def testLabels(self):
        '''Tests some simple label, resume and goto expresssions.'''
        ss = StatementSequence()
        ss.add(self._goto('main'))
        ss.add(self._label('pre'))
        ss.add(self._textbox("Count: 2"))
        ss.add(Resume())
        ss.add(self._textbox("This should never be displayed."))
        ss.add(self._label('main'))
        ss.add(self._textbox("Hello from label main!"))
        ss.add(self._label("a"))
        ss.add(self._textbox("Count: 1"))
        ss.add(self._goto("pre"))
        ss.add(self._textbox("Count: 3"))
        ss.add(self._textbox("FIN"))
        
        self.assertEqual(self._parsed("labels"), Root(ss))

        self.assertFalse(self.parser.hasErrors())
        
    def testFundef(self):
        '''Tests function definition with return statement.'''
        funstatements = StatementSequence()
        
        ss = StatementSequence()
        ss.add(Call(Identifier('textbox'), [Call(Identifier('concat'), [String("Meaning of Life: "), Call(Identifier('addone'), [Number(41)])])]))
        ss.add(Function(
               Identifier('addone'),
               [Identifier('x')],
               funstatements
               ))
        
        funstatements.add(Return(Call(Identifier('+'), [Number(1), Identifier('x')])))
        
        self.assertEqual(self._parsed("fundef"), Root(ss))
        
    def testConditionals(self):
        '''Tests several conditional expressions.'''
        ss = StatementSequence()
        ss.add(If(Boolean(True), self._goto("step1"), None))
        ss.add(self._textbox("This should never be displayed"))
        ss.add(self._label("step1"))
        ss.add(If(Boolean(False),
                  Call(Identifier("noop"), []),
                  self._goto("step2")))
        ss.add(self._textbox("This should never be displayed"))
        ss.add(self._label("step2"))
        ss.add(If(Boolean(False), Goto(Identifier("fail")), None))
        ss.add(self._goto("success"))
        ss.add(self._label("fail"))
        ss.add(self._textbox("This should never be displayed"))
        ss.add(self._label("success"))
        ss.add(self._textbox("Success"))
        
        parsed = self._parsed("conditional")
        
        self.assertNoParseErrors()
        self.assertEqual(parsed, Root(ss))
    
    def testConditionalAssignment(self):
        '''Tests an assignment as then or else expr.'''
        
        input = "if true a := 1 else a := 0"
        
        ss = StatementSequence()
        ss.add(If(Boolean(True), Assignment(Identifier("a"), Number(1)), Assignment(Identifier("a"), Number(0))))
        
        parsed = self.parser.parse(input)
        self.assertNoParseErrors()
        self.assertEqual(parsed, Root(ss))
        
    def testConditionalReturn(self):
        '''Tests a conditional return inside a function definition.'''
        funss = StatementSequence()
        funss.add(If(Boolean(True), Return(Boolean(True)), Return(Boolean(False))))
        
        ss = StatementSequence()
        ss.add(Function(Identifier("fun"), [], funss))
        
        input = '''def fun
        if true return true else return false
        enddef'''
        
        parsed = self.parser.parse(input)
        self.assertNoParseErrors()
        self.assertEqual(parsed, Root(ss))
        
    def testFailConditionalReturnOutsideFunction(self):
        '''Tests that a return outside of a function definition is not allowed.'''
        
        input = "if true return true else return false"
        
        self.parser.parse(input)
        self.assertTrue(self.parser.hasErrors())
        
    def testFailReturnOutsideFundef(self):
        '''A return statement should only be allowed inside a function definition.'''
        
        self._parsed("fail_return_outside_fundef")
        
        self.assertTrue(self.parser.hasErrors())
        self.assertTrue(self.parser.errors())
        self.assertTrue(forall(lambda x: isinstance(x, SyntaxException), self.parser.errors()))
        
    def testResetErrors(self):
        '''The errors should be reset between parses.'''
        
        self._parsed("fail_return_outside_fundef")
        self._parsed("labels")
        
        self.assertFalse(self.parser.hasErrors())
        self.assertFalse(self.parser.errors())
    
    def testParserIndependency(self):
        '''Two parser instances should have different error states.'''
        
        parserA = Parser()
        parserB = Parser()
        
        parserA.parse(getScriptFromFile("fail_return_outside_fundef"))
        parserB.parse(getScriptFromFile("labels"))
        
        self.assertTrue(parserA.hasErrors())
        self.assertFalse(parserB.hasErrors())
        
    def testFailLabelGotoInsideFunction(self):
        '''A label or goto statement inside a function is not allowed.'''
        
        self._parsed("fail_label_inside_function")
        self.assertTrue(self.parser.hasErrors())
        self._parsed("fail_goto_inside_function")
        self.assertTrue(self.parser.hasErrors())
         
    def testIncompleteSyntax(self):
        '''Tests several syntactic incomplete scripts.'''
        self.parser.parse("label\ngoto a")
        self.assertTrue(self.parser.hasErrors(), "Label with no identifier")
        
        self.parser.parse('fun (a 9\n"Hello"')
        self.assertTrue(self.parser.hasErrors(), "Incomplete parenthesis")
        
        self.parser.parse('def x\n"Hello"')
        self.assertTrue(self.parser.hasErrors(), "def with no enddef")
        
        self.parser.parse("true 5")
        self.assertTrue(self.parser.hasErrors(), "Call to a literal")
    
    def testListEmpty(self):
        '''Tests the empty list with some optional space.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("fun"), [CreateList([])]))
        self.assertEqual(self.parser.parse("fun [\n]"), Root(ss))
        
    def testListFuncall(self):
        '''Tests a list with one element, a funcall.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("fun"), [CreateList([Call(Identifier("fun2"), [Number(42)])])]))
        self.assertEqual(self.parser.parse("fun [ \n\n(fun2 42)]"), Root(ss))
        
    def testListInAList(self):
        '''A list in a list.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("fun"), [CreateList([CreateList([String("Hello"), String("World")]), String("!")])]))
        self.assertEqual(self.parser.parse('fun [["Hello","World"], "!",]'), Root(ss))
    
    def testFailList(self):
        '''Tests several wrong list statements.'''
        self.parser.parse('fun ["hello" identifier]')
        self.assertTrue(self.parser.hasErrors(), "List without comma")
        
        self.parser.parse('fun ["hello"')
        self.assertTrue(self.parser.hasErrors(), "List without ending square bracket")
        
        self.parser.parse('fun ["hello", , "world"]')
        self.assertTrue(self.parser.hasErrors(), "List with double comma")
        
        self.parser.parse('fun [is (lower a b) a]')
        self.assertTrue(self.parser.hasErrors(), "Conditionals are not allowed inside lists")
        
    def testAssignment(self):
        '''Tests a simple assignment operation.'''
        ss = StatementSequence()
        ss.add(Assignment(Identifier('var'), Number(5)))
        self.assertEqual(self.parser.parse('var := 5'), Root(ss))
        
    def testFailAssignment(self):
        '''Tests several failing assignments.'''
        self.parser.parse('5 := 5')
        self.assertTrue(self.parser.hasErrors(), "Assignment to literal")
        self.parser.parse('var :=')
        self.assertTrue(self.parser.hasErrors(), "Missing right hand side")
        self.parser.parse('var :=\n5')
        self.assertTrue(self.parser.hasErrors(), "Newline not supported")
        self.parser.parse('var := fundef lambda x\nreturn x\nenddef')
        self.assertTrue(self.parser.hasErrors(), "We currently do not support first class functions")
        
    def testEntityDefinition(self):
        '''Tests a simple entity definition.'''
        ss = StatementSequence()
        ss.add(EntityDefinition(Identifier("Character"),
                                {Identifier("name") : String("???"),
                                 Identifier("blipsound") : EntityDefinition.NoDefaultValue()}))
        ss.add(Assignment(Identifier("Apollo"),
                          CreateEntity(Identifier("Character"), {Identifier("name") : String("Apollo"),
                                                                 Identifier("blipsound") : String("male")})))
        ss.add(Call(Identifier("speaker"), [Identifier("Apollo")]))
        ss.add(self._textbox("I have Chords of Steel!"))
        ss.add(Call(Identifier("speaker"), [CreateEntity(Identifier("Character"), {Identifier("name") : String(""),
                                                                 Identifier("blipsound") : String("typewriter")})]))
        ss.add(self._textbox("March 22"))
        ss.add(FieldAssignment(Identifier("Apollo.blipsound"), String("silent")))
        ss.add(Call(Identifier("speaker"), [Identifier("Apollo")]))
        ss.add(self._textbox("What happened to my voice?"))
        
        self.assertEqual(self._parsed("entity"), Root(ss))
        
    def testDoubleFieldAccess(self):
        '''Tests accessing a field of an entity inside a field of an entity; also fields as arguments of fuctions.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("print"), [Identifier("Ema.mad.filename")]))
        
        self.assertEqual(self.parser.parse("print Ema.mad.filename"), Root(ss))
        
    def testFailEntity(self):
        '''Tests failing entity definitions and field accessing.'''
        self._expectErrors('entity Empty\nendentity', "An entity defintion may not be empty.")
        self._expectErrors('entity Bad\nfoo := bar\nendentity', "Entities can only have literals as default values.")
        self.assertRaises(SyntaxException, self.parser.parse, "entity Double\na\na\nendentity")
    
    def testBinaryOperation(self):
        '''Tests simple binary operations.'''
        funss = StatementSequence()
        funss.add(Return(Call(Identifier("::"), [Identifier("list"), CreateList([Identifier("elem")])])))
        
        ss = StatementSequence()
        ss.add(Assignment(Identifier("a"), Call(Identifier("+"), [Number(5), Number(5)])))
        ss.add(Assignment(Identifier("a"), Call(Identifier("-"), [Number(10), Call(Identifier("*"), [Number(2), Number(3)])])))
        ss.add(Assignment(Identifier("a"), Call(Identifier("*"), [Call(Identifier("-"), [Number(10), Number(2)]), Number(3)])))
        ss.add(Assignment(Identifier("a"), Call(Identifier("*"), [Call(Identifier("-"), [Number(10), Number(2)]), Number(3)])))
        ss.add(If(Call(Identifier("="), [Number(5), Number(5)]), Call(Identifier("fun"), []), None))
        ss.add(Call(Identifier("fun2"), [Call(Identifier(":+"), [CreateList([Number(1), Number(2), Number(3)]), Number(5)])]))
        ss.add(Call(Identifier("fun3"), [Call(Identifier(":+"), [CreateList([Number(1), Number(2), Number(3)]), Number(5)]), String("more")]))
        ss.add(Call(Identifier("fun4"), [Call(Identifier("+"), [Number(5), Number(5)]), Call(Identifier("fun"), [])]))
        ss.add(Function(Identifier(":+"), [Identifier("list"), Identifier("elem")], funss))
        
        self.assertEqual(self._parsed("binary_ops"), Root(ss))
        
    def testRootUnequality(self):
        '''Just a quick test that roots are uneqal if they don't contain the same values.'''
        self.assertNotEqual(Root(Number(3)), Root(Number(4)))
        
    def testExcessiveWhitespace(self):
        '''Tests the use of excessive whitespace.'''
        self._parsed("whitespace")
        self.assertFalse(self.parser.hasErrors(), self.parser.errors())

#TODO write excessive whitespace test (optional indentation + newline at random positions) 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()