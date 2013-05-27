'''
Tests the lexer.
'''
import unittest
from core.wrightscript.lexer import lexer, ParseException

class Test(unittest.TestCase):

    def parseAsTypeList(self, string):
        lexer.input(string)
        return [token.type for token in lexer]
    
    def parseAsValueList(self, string):
        lexer.input(string)
        return [token.value for token in lexer]

    def testReservedWords(self):
        """Tests that reserved words are recognized and all other words are identifiers."""
        input = '''
        label
        resume
        if else
        goto
        exit
        def
        enddef
        return
        exits
        labeled
        '''
        self.assertEqual(self.parseAsTypeList(input), [
                     'NEWLINE',
                     'LABEL',
                     'NEWLINE',
                     'RESUME',
                     'NEWLINE',
                     'IF',
                     'ELSE',
                     'NEWLINE',
                     'GOTO',
                     'NEWLINE',
                     'EXIT',
                     'NEWLINE',
                     'DEF',
                     'NEWLINE',
                     'ENDDEF',
                     'NEWLINE',
                     'RETURN',
                     'NEWLINE',
                     'IDENTIFIER',
                     'NEWLINE',
                     'IDENTIFIER',
                     'NEWLINE'])
        
    def testStrings(self):
        """Tests that strings are parsed correctly."""
        input = '\n"Something"'
        self.assertEqual(self.parseAsTypeList(input), ['NEWLINE', 'STRING'])
        input = '"Hello World!"'
        self.assertEqual(self.parseAsValueList(input), ['Hello World!'])
        input = '"Line\nBreak"'
        self.assertEqual(self.parseAsValueList(input), ['Line\nBreak'])
        input = '"Ignore return or label"'
        self.assertEqual(self.parseAsValueList(input), ['Ignore return or label'])
    
    def testSubsequentStrings(self):
        """Checks that the parser is no greedy with strings, so that
        two strings following each other are parsed as two different strings."""
        input = '"Hello" "World"'
        self.assertEquals(self.parseAsTypeList(input), ['STRING', 'STRING'])
        
    def testStringEscape(self):
        """Checks that string sequences can have escaped quotes."""
        self.assertEquals(self.parseAsValueList(r'"What do you mean by \"accident\"?"'), ['What do you mean by "accident"?'])
        pass
    
    def testNumbers(self):
        """Tests that numbers are parsed correctly and converted to integers."""
        input = '\n300'
        self.assertEqual(self.parseAsTypeList(input), ['NEWLINE', 'NUMBER'])
        input = '42 100'
        self.assertEqual(self.parseAsValueList(input), [42, 100])
        
        try:
            input = "-42"
            self.parseAsTypeList(input)
        except ParseException:
            pass
        else:
            self.fail("Negative values are currently not supported and should raise a ParseException")
        
        try:
            input = "42.0"
            self.parseAsTypeList(input)
        except ParseException:
            pass
        else:
            self.fail("Floats are currently not supported and should raise a ParseException")
    
    def testBooleans(self):
        """Tests that boolean literals are parsed correctly."""
        input='true false'
        self.assertEqual(self.parseAsTypeList(input), ['BOOLEAN', 'BOOLEAN'])
        self.assertEqual(self.parseAsValueList(input), [True, False])
        
    def testInvalidIdentifier(self):
        """Tests some invalid Identifier names."""
        self.assertRaises(ParseException, self.parseAsTypeList, "42_invalid")
        self.assertRaises(ParseException, self.parseAsTypeList, "..dotty")
        
    def testIdentifier(self):
        """Tests some valid Identifier names."""
        self.assertEqual(self.parseAsTypeList('sub.part valid_name __init__ double..'), ['IDENTIFIER' for _ in range(0, 4)])
        
    def testParenthesis(self):
        """A call to print with the result of a math expression."""
        input = 'print (add 5 5)'
        self.assertEqual(self.parseAsTypeList(input), ['IDENTIFIER', 'LPAREN', 'IDENTIFIER', 'NUMBER', 'NUMBER', 'RPAREN'])
        
    def testIgnoreComments(self):
        """Checks that single line and multiline comments are ignored. Also all line breaks shall be reduced to one."""
        input = '''
        # This is a single line comment
        foo
        
        /* Multiline
        Comment */
        bar'''
        self.assertEqual(self.parseAsTypeList(input), ['NEWLINE', 'IDENTIFIER', 'NEWLINE', 'IDENTIFIER'])

    def testLineNumbers(self):
        """Checks that line numbers are reset by the lexer for new input.
        See Bug https://code.google.com/p/ply/issues/detail?id=20"""
        lexer.input('a')
        tokens = [token for token in lexer]
        self.assertEquals(tokens[0].lineno, 1)
        lexer.input('a')
        tokens = [token for token in lexer]
        self.assertEquals(tokens[0].lineno, 1)
        
    def testCommentNewline(self):
        """Ensures that a comment with a newline leaves the newline intact."""
        input = 'test #comment\n 5'
        self.assertEqual(self.parseAsTypeList(input), ['IDENTIFIER', 'NEWLINE', 'NUMBER'])
        
    def testLists(self):
        """Tests support for list syntax."""
        input = '[test, "test"]'
        self.assertEqual(self.parseAsTypeList(input), ['LBRACKET', 'IDENTIFIER', 'COMMA', 'STRING', 'RBRACKET'])
        
    def testAssignment(self):
        """Tests a simple assignment syntax."""
        input1 = 'var := 5'
        input2 = 'var:=5'
        typeList = ['IDENTIFIER', 'ASSIGN', 'NUMBER']
        self.assertEqual(self.parseAsTypeList(input1), typeList)
        self.assertEqual(self.parseAsTypeList(input2), typeList)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()