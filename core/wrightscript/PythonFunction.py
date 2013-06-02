'''
PythonFunctions are like an AST Function in the way that they can be the argument
of an Apply expression; however, instead of executing a StatementSequence of
Wrightscript, a Python function is called.

The Python function doesn't have to know anything about Wrightscript or the
AST Nodes. Instead, this knowledge is required when *creating* a PythonFunction
reference by stating the argument types with the P... AST nodes. The AST values
are then unpacked and converted to standard Python types, e.g. a Number to an
integer. However, this enforces static type checking. It is impossible to pass
a List to a PythonFunction that has it's parameter declared as a function.

Of course, the return type has also to bee specified, to repack the value
apropiately.

To implement language features nearer to the core, e.g. a function that
returns the template name of an entity, you are free to define those
as well. Just implement the Callable interface.
'''

from Values import NumberV, BooleanV, StringV, List, Entity, LiteralV
from AST import Function
from Callable import Callable
from RuntimeException import WrongArgumentNumberError
from itertools import izip, imap

def implicitUnpack(value, env):
    if isinstance(value, LiteralV):
        return value.value()
    if isinstance(value, List):
        return PList().unpack(value, env)
    if isinstance(value, Entity):
        return PEntity().unpack(value, env)
    if callable(value):
        return PFunction().unpack(value, env)
    if type(value) == None:
        return None
    else:
        raise TypeError("Invalid implicit conversion of type " + repr(type(value)))

def implicitPack(value, env):
    '''Used when the type is not known (e.g. in a list). Slower then real packers.'''
    if type(value) == str: # String is on the top, hoping that this is the most used data type of entities
        return PString().pack(value, env)
    elif type(value) == bool:
        return PBoolean().pack(value, env)
    elif type(value) == int:
        return PNumber().pack(value, env)
    elif type(value) == tuple or isinstance(value, PList.TupleView):
        return PList().pack(value, env)
    elif isinstance(value, PEntity.DictionaryView):
        return PEntity().pack(value, env)
    else:
        raise TypeError("Invalid implicit conversion of type " + repr(type(value)))

class Packer(object):
    def unpack(self, node, env):
        '''ASTNode, Environment -> any
        
        Converts the given AST node into a natural python type. Raises a
        TypeError when the Packer is not responsible for this AST node.'''
        raise NotImplementedError("SubclassResponsibility")
    
    def pack(self, value, env):
        '''any, Environment -> ASTNode
        
        Converts the given value into a AST node. Raises a TypeError
        when the Packer is not responsible for the value's type.'''
        raise NotImplementedError("SubclassResponsibility")
    
class NonePacker(object):
    def unpack(self, node, env):
        raise "This packer is only for packing None values, they are not real nodes."
    
    def pack(self, value, env):
        return None

class LiteralUnpacker(Packer):
    def __init__(self, ASTType, pythonType, strict=True):
        self.ASTType = ASTType
        self.pythonType = pythonType
        self.strict = strict
    
    def unpack(self, node, env):
        if self.strict:
            if not isinstance(node, self.ASTType):
                raise TypeError("Expected " + self.ASTType.__name__ + " as argument, got " + node.__class__.__name__)
        else:
            if not isinstance(node, LiteralV):
                raise TypeError("Expected Literal as argument, got " + node.__class__.__name__)
        return node.value()
    
    def pack(self, value, env):
        if self.strict and (type(value) != self.pythonType):
            raise TypeError("Expected " + repr(self.pythonType) + " as PythonFunction return, got " + repr(type(value)))
        return self.ASTType(self.pythonType(value))

def PNumber(strict=True):
    return LiteralUnpacker(NumberV, int, strict)

def PBoolean(strict=True):
    return LiteralUnpacker(BooleanV, bool, strict)

def PString(strict=True):
    return LiteralUnpacker(StringV, str, strict)

class PList(Packer):
    class TupleView(object):
        '''Provides a tuple-like view on a List node.
        Automatically converts between types.'''
        def __init__(self, list, env):
            self.list = list
            self.env = env
            
        def __getitem__(self, index):
            if not type(index) == int:
                raise TypeError("Lists are indexed by integers")
            return implicitUnpack(self.list.value()[index], self.env)
        
        def __setitem__(self, index, value):
            if not type(index) == int:
                raise TypeError("Lists are indexed by integers")
            self.list.value()[index] = implicitPack(value, self.env)
            
        def __iter__(self):
            return imap(lambda x: implicitUnpack(x, self.env), self.list.value())
        
        def __add__(self, other):
            if type(other) == tuple:
                return PList.TupleView(List(self.list.value() + tuple(imap(lambda x: implicitPack(x, self.env), other))), self.env)
            elif isinstance(other, PList.TupleView):
                return PList.TupleView(List(self.list.value() + other.list.value()), self.env)
            else:
                raise TypeError("Can only append tuples or Wrightscript lists to Wrightscript lists")
            
        def __radd__(self, other):
            if type(other) == tuple:
                return PList.TupleView(List(map(implicitPack, other) + self.list.value()), self.env)
            else:
                raise TypeError("Can only prepend tuples to Wrightscript lists")
            
    def unpack(self, node, env):
        if not isinstance(node, List):
            raise TypeError("Expected List as argument, got " + node.__class__.__name__)
        
        return PList.TupleView(node, env)
    
    def pack(self, value, env):
        if isinstance(value, PList.TupleView):
            return value.list
        else:
            try:
                return List(map(lambda x: implicitPack(x, self.env), value))
            except TypeError:
                raise TypeError("Expected iterable as return, but got " + repr(type(value)))

class PEntity(Packer):
    class DictionaryView(object):
        '''Provides a dictionary-like view on an Entity.
        Also ensures that nothing other than literals is set to a dictionary's key
        and all values are converted appropriately.'''
        def __init__(self, entity, env):
            self.entity = entity
            self.env = env
        
        def __getitem__(self, index):
            if not type(index) == str:
                raise TypeError("Environment keys can only be strings")

            return implicitUnpack(self.entity.get(index), self.env)
        
        def __setitem__(self, index, value):
            if not type(index) == str:
                raise TypeError("Environment keys can only be strings")
            self.entity.set(index, implicitPack(value, self.env))
            
    
    def __init__(self, templateName):
        self.templateName = templateName
            
    def unpack(self, node, env):
        if not isinstance(node, Entity):
            raise TypeError("Expected Entity as argument, but got " + node.__class__.__name__)
        
        if not node.template() == self.templateName:
            raise TypeError("Expected Entity of type " + self.templateName + " but got " + node.template().name())
        
        return PEntity.DictionaryView(node, env)
    
    def pack(self, value, env):
        '''Not usable.
        
        As of know, we don't have a "anonymous" entity definition type, as every entity references it's template.
        You could argue that a simple name of "" would be valid, but that's not how entities are supposed to
        work.'''
        raise TypeError("Entities can't be created by PythonFunctions.")
    
class PFunction(Packer):
    
    def unpack(self, fun, env):
        if not callable(fun):
            raise TypeError("Expected callable as argument, but got " + fun.__class__.__name__)
        return lambda *args: (fun(map(lambda arg: implicitPack(arg, env), args), env)).value()
    
    def pack(self, value):
        raise RuntimeError("It is currently not possible to create functions on the Fly.")
    
class PythonFunction(Callable):
    '''Creates a new PythonFunction instance that is callable from AST.call. Use
    method chaining to add parameters and return types:
    
    "numMap" : PythonFunction(map).expects(PFunction(), PList()).returns(PNumber)'''
    
    def __init__(self, fun):
        self.fun = fun
        self.parameterPackers = list()
        self.returnPacker = NonePacker()
        
    def expects(self, *args):
        self.parameterPackers = args
        return self
        
    def returns(self, packer):
        self.returnPacker = packer
        return self
    
    def __call__(self, args, env):
        
        if len(args) != len(self.parameterPackers):
            raise WrongArgumentNumberError(self, len(self.parameterPackers), len(args))
        
        return self.returnPacker.pack(
                   self.fun(*(map(lambda (packer, param): packer.unpack(param, env),
                                  izip(self.parameterPackers, args))
                               )), env
               )
    
    def __name__(self):
        return self.fun.__name__      