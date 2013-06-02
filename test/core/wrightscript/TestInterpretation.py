'''
Tests the interpretation of Wrightscript statements.
'''
import unittest

from TestParserSyntax import getScriptFromFile
from core.wrightscript.parser import Parser
from core.wrightscript.Environment import Environment
from core.wrightscript.PythonFunction import PythonFunction, PString, PNumber, PBoolean
from core.wrightscript.Values import NumberV

class Test(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()
        self.eventList = []
        self.env = Environment()
        self.env.addFunction(PythonFunction(lambda x: self.eventList.append("TB: " + x)).expects(PString()), "textbox")
        self.env.addFunction(PythonFunction(lambda x, y: x > y).expects(PNumber(), PNumber()).returns(PBoolean()), ">")
        self.env.addFunction(PythonFunction(lambda x, y: x - y).expects(PNumber(), PNumber()).returns(PNumber()), "-")

    def _parsed(self, scriptname):
        return self.parser.parse(getScriptFromFile(scriptname), self.env)

    def testLabels(self):
        program = self._parsed("labels")
        self.assertFalse(self.parser.hasErrors())
        program.interp(self.env)
        self.assertEqual(self.eventList, ["TB: Hello from label main!", "TB: Count: 1", "TB: Count: 2", "TB: Count: 3", "TB: FIN"])
        
    def testStackoverflow(self):
        program = self._parsed("stackoverflow")
        self.assertFalse(self.parser.hasErrors())
        result = program.interp(self.env)
        self.assertEqual(result, NumberV(0))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()