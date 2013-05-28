'''
Tests the syntactical aspect of the parser that creates an Abstract Syntax
Tree from Wrightscript.
'''
import unittest
import os
from core.wrightscript.parser import Parser, SyntaxError
from core.wrightscript.AST import *
from core.functional import forall

class TestParserSyntax(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def _getScriptFromFile(self, scriptname):
        '''Helper function that retrieves a testfile from the samples directory.'''
        f = open(os.path.dirname(os.path.abspath(__file__)) + '/samples/' + scriptname + '.ws', 'r')
        str = f.read()
        f.close()
        return str
    
    def _parsed(self, scriptname):
        return self.parser.parse(self._getScriptFromFile(scriptname))
    
    def _textbox(self, string):
        return Call(Identifier('textbox'), [String(string)])
    
    def _label(self, string):
        return Label(Identifier(string))
    
    def _goto(self, string):
        return Goto(Identifier(string))
    
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
        
        self.assertEqual(self._parsed("labels"), ss)
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
        
        funstatements.add(Return(Call(Identifier('add'), [Number(1), Identifier('x')])))
        
        self.assertEqual(self._parsed("fundef"), ss)
        
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
        
        self.assertFalse(self.parser.hasErrors())
        self.assertEqual(parsed, ss)
        
    def testFailReturnOutsideFundef(self):
        '''A return statement should only be allowed inside a function definition.'''
        
        self._parsed("fail_return_outside_fundef")
        
        self.assertTrue(self.parser.hasErrors())
        self.assertTrue(self.parser.errors())
        self.assertTrue(forall(lambda x: isinstance(x, SyntaxError), self.parser.errors()))
        
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
        
        parserA.parse(self._getScriptFromFile("fail_return_outside_fundef"))
        parserB.parse(self._getScriptFromFile("labels"))
        
        self.assertTrue(parserA.hasErrors())
        self.assertFalse(parserB.hasErrors())
    
    def testLabelGoto(self):
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
        ss.add(Call(Identifier("fun"), [CreateList(tuple())]))
        self.assertEqual(self.parser.parse("fun [\n]"),ss)
        
    def testListFuncall(self):
        '''Tests a list with one element, a funcall.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("fun"), [CreateList(tuple([Call(Identifier("fun2"), [Number(42)])]))]))
        self.assertEqual(self.parser.parse("fun [ \n\n(fun2 42)]"), ss)
        
    def testListInAList(self):
        '''A list in a list.'''
        ss = StatementSequence()
        ss.add(Call(Identifier("fun"), [CreateList(tuple([CreateList(tuple([String("Hello"), String("World")])), String("!")]))]))
        self.assertEqual(self.parser.parse('fun [["Hello","World"], "!",]'), ss)
    
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
        self.assertEqual(self.parser.parse('var := 5'), ss)
        
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
        
        
        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()