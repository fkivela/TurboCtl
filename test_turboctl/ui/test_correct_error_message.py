"""This module contains unit tests for the correct_error_message 
module.
"""
import unittest

from turboctl.ui.correct_error_message import correct_error_message

class TestTooManyArguments(unittest.TestCase):
        
    def test_no_arguments(self):
        string = "cmd_read() takes 1 positional argument but 2 were given"
        new_string = "'read' takes 0 positional arguments but 1 was given"
        self.assertEqual(correct_error_message(string), new_string)
        
    def test_one_argument(self):
        string = "cmd_read() takes 2 positional argument but 3 were given"
        new_string = "'read' takes 1 positional argument but 2 were given"
        self.assertEqual(correct_error_message(string), new_string)
        
    def test_multiple_arguments(self):
        string = "cmd_read() takes 100 positional arguments but 101 were given"
        new_string = ("'read' takes 99 positional arguments "
                      "but 100 were given")
        self.assertEqual(correct_error_message(string), new_string)
        
    def test_variable_number_of_arguments(self):
        string = ("cmd_read() takes from 2 to 3 positional arguments "
                  "but 6 were given")
        new_string = ("'read' takes from 1 to 2 positional "
                      "arguments but 5 were given")
        self.assertEqual(correct_error_message(string), new_string)

class TestOther(unittest.TestCase):

    def test_missing_argument(self):
        
        string = (
            "cmd_read() missing 1 required positional argument: 'number'")
        new_string = (
            """'read' missing 1 required positional argument: 'number'""")
        self.assertEqual(correct_error_message(string), new_string)
        
    def test_unexpected_keyword_argument(self):
        
        string = ("cmd_read() got an unexpected keyword argument 'test'")
        new_string = ("""'read' got an unexpected keyword argument 'test'""")
        self.assertEqual(correct_error_message(string), new_string)
        
    def test_multiple_values_for_same_argument(self):
        
        string = ("cmd_read() got multiple values for argument 'number'")
        new_string = ("""'read' got multiple values for argument 'number'""")
        self.assertEqual(correct_error_message(string), new_string)
    
    
if __name__ == '__main__':
    unittest.main()