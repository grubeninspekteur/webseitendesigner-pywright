'''
Checks that the environment passed to the parser is filled correctly.
'''
import unittest
from TestParserSyntax import getScriptFromFile
from core.wrightscript.parser import Parser
from core.wrightscript.Environment import Environment
from core.wrightscript.Values import JumpPosition
from core.wrightscript.AST import *
from core.wrightscript.RuntimeException import UnboundNameError


class TestEnvironmentParsing(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.env = Environment()

    def _parsed(self, scriptname):
        return self.parser.parse(getScriptFromFile(scriptname), self.env)
    
    def _assertLabel(self, name, lineNo, statementSequence):
        self.assertEqual(self.env.get(name), JumpPosition(lineNo, statementSequence))

    def testEmpty(self):
        '''Ensures that parsing no definitions nor labels won't change the environment.'''
        self.parser.parse('"Hello World"\nadd 1 2')
        self.assertFalse(bool(self.env))
    
    def testLabels(self):
        '''Tests that labels are bound correctly.'''
        statementSequence = self._parsed('labels').inner()
        self._assertLabel("pre", 9, statementSequence)
        self._assertLabel("main", 15, statementSequence)
        self._assertLabel("a", 18, statementSequence)
        
    def testFunction(self):
        '''Tests that functions are bound correctly.'''
        self._parsed('fundef')
        
        funstatements = StatementSequence()
        funstatements.add(Return(Call(Identifier('+'), [Number(1), Identifier('x')])))
        
        function = Function(
               Identifier('addone'),
               [Identifier('x')],
               funstatements
               )
        
        self.assertEqual(self.env.get('addone'), function)
        
    def testEntityDefinition(self):
        '''Tests that EntityDefinitions are bound correctly.'''
        self._parsed('entity')
        entity = EntityDefinition(Identifier("Character"),
                                {Identifier("name") : String("???"),
                                 Identifier("blipsound") : EntityDefinition.NoDefaultValue()})
        
        self.assertEqual(self.env.get('Character'), entity)
        
    def testDefaultEnvironmentReset(self):
        '''Tests that the default environment is created on any subsequent parse.'''
        self.parser.parse(getScriptFromFile('entity'))
        self.parser.parse(getScriptFromFile('labels'))
        self.assertRaises(UnboundNameError, self.parser.env.get, 'Character')
        
    def testBinOpDefinition(self):
        '''Tests that a Binop function will be defined.'''
        
        self._parsed("binary_ops")
        self.assertFalse(self.parser.hasErrors())
        self.assertTrue(isinstance(self.env.get(":+"), Function))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()