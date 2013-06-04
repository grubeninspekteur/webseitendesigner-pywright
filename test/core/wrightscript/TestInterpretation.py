'''
Tests the interpretation of Wrightscript statements.
'''
import unittest
import os

from TestParserSyntax import getScriptFromFile
from core.wrightscript.parser import Parser
from core.wrightscript.Environment import Environment
from core.wrightscript.PythonFunction import PythonFunction, PString, PNumber, PBoolean,\
    PList
from core.wrightscript.Values import NumberV, BooleanV, NilV, List
from core.wrightscript.RuntimeException import WrightscriptAssertionError,\
    RuntimeException

def printer(x):
    print x

def appendTuple(x, y):
    return x + y

class Test(unittest.TestCase):
    def asserter(self, testVal):
        self.assertions += 1
        if not testVal:
            raise WrightscriptAssertionError()
        return None
    
    def setUp(self):
        self.parser = Parser()
        self.eventList = []
        self.assertions = 0
        self.env = Environment()
        self.env.addFunction(PythonFunction(lambda x: self.eventList.append("TB: " + x)).expects(PString()), "textbox")
        self.env.addFunction(PythonFunction(lambda x, y: x > y).expects(PNumber(), PNumber()).returns(PBoolean()), ">")
        self.env.addFunction(PythonFunction(lambda x, y: x - y).expects(PNumber(), PNumber()).returns(PNumber()), "-")
        self.env.addFunction(PythonFunction(lambda x, y: x + y).expects(PNumber(), PNumber()).returns(PNumber()), "+")
        self.env.addFunction(PythonFunction(lambda x, y: x * y).expects(PNumber(), PNumber()).returns(PNumber()), "*")
        self.env.addFunction(PythonFunction(lambda x, y: int(x / y)).expects(PNumber(), PNumber()).returns(PNumber()), "/")
        self.env.addFunction(PythonFunction(lambda s1, s2: str(s1) + str(s2)).expects(PString(strict=False), PString(strict=False)).returns(PString()), "concat")
        self.env.addFunction(PythonFunction(lambda x: not x).expects(PBoolean()).returns(PBoolean()), "not")
        
        # List functions just for testing purposes
        self.env.addFunction(PythonFunction(appendTuple).expects(PList(), PList()).returns(PList()), "::")
        
        
        self.env = Environment(self.env) # separate predefined functions from userspace
        def first(args, env):
            tuple = args[0].value()
            return tuple[0]
            
        def rest(args, env):
            tuple = args[0].value()
            return List(tuple[1:])
            
        def isEmpty(args, env):
            if not args[0].value():
                return BooleanV(True)
            else:
                return BooleanV(False)
            
        self.env.addFunction(first, "first")
        self.env.addFunction(rest, "rest")
        self.env.addFunction(isEmpty, "isEmpty")
        
        # Assertions
        self.env.addFunction(PythonFunction(self.asserter).expects(PBoolean()), "assert")
        
        self.env.addFunction(lambda args, env: BooleanV(args[0] == args[1]), "=")
        
        #Debug
        self.env.addFunction(PythonFunction(printer).expects(PString()), "print")
        self.env.addFunction(PythonFunction(lambda l: str(l)).expects(PList()).returns(PString()), "listToStr")
        #self.env.set("DEBUG", BooleanV(True))

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
        
    def testConditional(self):
        program = self._parsed("conditional")
        self.assertFalse(self.parser.hasErrors())
        program.interp(self.env)
        self.assertEqual(self.eventList, ["TB: Success"])
    
    def testFundef(self):
        program = self._parsed("fundef")
        self.assertFalse(self.parser.hasErrors())
        program.interp(self.env)
        self.assertEqual(self.eventList, ["TB: Meaning of Life: 42"])
        
    def testWSUnitTests(self):
        for scriptname in [dirpath[:- len("samples/unittests/")] + '/unittests/' + filename[:-3] for (dirpath, _, filenames) in os.walk("samples/unittests/") for filename in filenames if filename.endswith('.ws')]:
            program = self._parsed(scriptname)
            self.assertFalse(self.parser.hasErrors(), "Errors in script " + scriptname + ": " + repr(self.parser.errors()))
            try:
                program.interp(self.env)
            except RuntimeException, e:
                raise AssertionError("File " + scriptname + ": " + str(e))
            print "Wrightscript assertions:", "<" + scriptname + ">", self.assertions
            self.setUp()
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()