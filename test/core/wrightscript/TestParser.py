'''
Tests the syntactical parser that creates an Abstract Syntax Tree
from Wrightscript.
'''
import unittest
from core.wrightscript.parser import Parser, SyntaxError
from core.wrightscript.AST import *
from core.functional import forall

class TestParser(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def _getScriptFromFile(self, scriptname):
        '''Helper function that retrieves a testfile from the samples directory.'''
        f = open('samples/' + scriptname + '.ws', 'r')
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
        
        
        
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()