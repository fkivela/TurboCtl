"""Unit tests for the command_parser module."""

import unittest
from collections import namedtuple

from turboctl import Command, CommandParser, UIParseError, UICommandError

Output = namedtuple('Output', 'name, args, kwargs')

cmd_list = [
    Command(names=['test', 't'],
        function='test_method',
        args=[],
        description=''),
]


class DummyUI():
    def test_method(self, *args, **kwargs):
        return Output('test', args, kwargs)


class TestCommandParser(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.ui = DummyUI()
        self.parser = CommandParser(self.ui, cmd_list)
                
    def test_no_args(self):
        string = 'test'
        out = self.parser.parse(string, False)
        
        self.assertEqual(out.name, 'test')
        self.assertEqual(out.args, ())
        self.assertEqual(out.kwargs, {})
        
    def test_args_and_kwargs(self):
        string = 'test 1 kwarg1=3 2 kwarg2=4'
        out = self.parser.parse(string, False)
        
        self.assertEqual(out.name, 'test')
        self.assertEqual(out.args, (1, 2))
        self.assertEqual(out.kwargs, {'kwarg1': 3, 'kwarg2': 4})
        
    def test_alias(self):
        string = 't 1'
        out = self.parser.parse(string, False)
        
        self.assertEqual(out.name, 'test')
        self.assertEqual(out.args, (1,))
        self.assertEqual(out.kwargs, {})
        
    def test_data_types(self):
        string = "test 1 'str' also_str (1,2) [3,4] dict={5:6} 7,8,9 True"
        out = self.parser.parse(string, False)
        
        self.assertEqual(out.name, 'test')
        self.assertEqual(out.args, 
                         (1, 'str', 'also_str', (1,2), [3,4], (7,8,9), True)
                         )
        self.assertEqual(out.kwargs, {'dict': {5: 6}})
        
    def test_whitespace(self):
        string = "   test     line1\nline2      "
        out = self.parser.parse(string, False)
        
        self.assertEqual(out.name, 'test')
        self.assertEqual(out.args, ('line1\nline2',))
        self.assertEqual(out.kwargs, {})
        
    def test_empty(self):
        string = "   "
        out = self.parser.parse(string, False)
        self.assertFalse(out)
        
    def test_valid_and_invalid_keywords(self):
        invalid_args = ('1arg=1', 'arg*=1', 'ar#g=1', 'arg=arg=1')
        valid_args = ('arg1=1', '_arg_=1', 'ARG=1')
        
        for arg in invalid_args:
            with self.assertRaises(UIParseError):
                self.parser.parse(f'test {arg}', False)
                
        for arg in valid_args:
            out = self.parser.parse(f'test {arg}', False)
        
            self.assertEqual(out.name, 'test')
            self.assertEqual(out.args, ())
            self.assertEqual(set(out.kwargs.values()), set((1,)))
            
    def test_valid_and_invalid_values(self):
        valid_values = ('"', 'aa#aa', "'", '@$¤')
        
        with self.assertRaises(UIParseError):
            self.parser.parse(f'test 1==1', False)

        for v in valid_values:
            out = self.parser.parse(f'test {v}', False)
        
            self.assertEqual(out.name, 'test')
            self.assertEqual(out.args, (v,))
            self.assertEqual(out.kwargs, {})
            
    def test_invalid_commands(self):
        invalid_commands = ('test1', '#¤$', "'")
        
        for cmd in invalid_commands:
            with self.assertRaises(UICommandError):
                self.parser.parse(f'{cmd} 1', False)

    
if __name__ == '__main__':
    unittest.main()