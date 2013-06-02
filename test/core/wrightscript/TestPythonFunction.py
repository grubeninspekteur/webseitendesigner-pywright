'''
Tests the PythonFunction mechanism which hides the AST node syntax behind
an abstraction, so normal python functions can be used and provided to
Wrightscript via the Environment.
'''
import unittest
from core.wrightscript.PythonFunction import PythonFunction, PString, PNumber,\
    PEntity, PList, PFunction
from core.wrightscript.Values import StringV, NumberV, Entity, List
from core.wrightscript.Environment import Environment

def factorial(x):
    if x == 0:
        return 1
    return x * factorial(x - 1)

def capitalizeName(entity):
    entity['name'] = entity['name'].capitalize()

def append(aList, value):
    return aList + (value,)

class Test(unittest.TestCase):

    def testNoArgs(self):
        '''A simple function that returns Hello World.'''
        fun = PythonFunction(lambda: "Hello World").returns(PString())
        self.assertEqual(fun(list(), Environment()), StringV("Hello World"))
        
    def testFactorial(self):
        '''Tests the classical factorial recursive function.'''
        fun = PythonFunction(factorial).expects(PNumber()).returns(PNumber())
        self.assertEqual(fun([NumberV(5)], Environment()), NumberV(120))
        
    def testEntity(self):
        '''Tests entity manipulation.'''
        fun = PythonFunction(capitalizeName).expects(PEntity('Character'))
        
        entity = Entity('Character', {'name' : StringV('phoenix')})
        fun([entity], Environment())
        self.assertEqual(entity.get('name'), StringV('Phoenix'))
    
    def testList(self):
        '''Tests list arguments.'''
        fun = PythonFunction(append).expects(PList(), PString(False)).returns(PList())
        
        self.assertEqual(List([NumberV(1), NumberV(2)]), fun([List([NumberV(1)]), NumberV(2)], Environment()))
        
    def testBuiltinPythonFunction(self):
        '''Tests using a built-in python function.'''
        fun = PythonFunction(sum).expects(PList()).returns(PNumber())
        
        self.assertEqual(NumberV(6), fun([List([NumberV(1), NumberV(2), NumberV(3)])], Environment()))
    
    def testFunction(self):
        '''Tests using a Function as an argument.'''
        addone = lambda args, env: NumberV(1 + args[0].value())
        fun = PythonFunction(lambda fun: fun(1) / 2).expects(PFunction()).returns(PNumber())
        self.assertEqual(NumberV(1), fun([addone], Environment()))
    # TODO test function when function evaluation is possible
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()