'''
Collections of exceptions used for control flow.
'''

class ControlFlowEvent():
    pass

class ResumeEvent(ControlFlowEvent):
    def __repr__(self):
        return "Uncaught ResumeEvent"

class GotoEvent(ControlFlowEvent):
    def __init__(self, jumpPosition):
        self._jumpPosition = jumpPosition
    
    def jumpPosition(self):
        return self._jumpPosition
    
    def __repr__(self):
        return "Uncaught GotoEvent to line " + repr(self._jumpPosition) + " of some Statement Sequence"

class ExitEvent(ControlFlowEvent):
    def __repr__(self):
        return "Uncaught ExitEvent"
    
class ReturnEvent(ControlFlowEvent):
    def __init__(self, returnValue):
        self._value = returnValue
        
    def value(self):
        return self._value
    
    def __repr__(self):
        return "Uncaught ReturnEvent returning " + repr(self._value)