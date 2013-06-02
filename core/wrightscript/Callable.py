class Callable(object):
    '''Classes implementing the Callable interface provide a __call__ method
    and are safe to call inside an AST.Call expression.'''
    def __call__(self, args, env):
        raise NotImplemented('Subclass Responsibility')
    
    def __name__(self):
        '''Returns the function's name, e.g. for error messages.'''
        return "<unnamed>"
