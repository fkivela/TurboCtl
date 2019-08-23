"""Unit test for the table module."""
import unittest

from test_turboctl import dummy_parameter
from turboctl import array, table, Types

class Test(unittest.TestCase):
    
    def setUp(self):
        
        # Print long strings when a test fails.
        self.maxDiff = None
        
        p1 = dummy_parameter(
            number=1, 
            name='Parameter 1', 
            indices=range(0), 
            min_=0, 
            max_=65535, 
            default=0, 
            unit='s', 
            writable=True, 
            type_=Types.UINT, 
            size=16, 
            description = 'This is test parameter #1.')
            
        self.row1 = [
            'NUMBER\n1', 
            'NAME\nParameter 1', 
            'INDICES\n-',
            'MIN\n0',
            'MAX\n65535',
            'DEFAULT\n0',
            'UNIT\ns',
            'WRITABLE\nTrue',
            'TYPE\nUnsigned integer',
            'SIZE\n16',
            'DESCRIPTION\nThis is test parameter #1.',
            ]
        self.row1 = [s + '\n\n' for s in self.row1]
            
        p2 = dummy_parameter(
            number=2, 
            name='Parameter 2', 
            indices=range(1,6), 
            min_=-10, 
            max_=10, 
            default=0, 
            unit='Hz', 
            writable=False, 
            type_=Types.SINT, 
            size=32, 
            description = 'This is test parameter #2.')
            
        self.row2 = [
            'NUMBER\n2', 
            'NAME\nParameter 2', 
            'INDICES\n1...5',
            'MIN\n-10',
            'MAX\n10',
            'DEFAULT\n0',
            'UNIT\nHz',
            'WRITABLE\nFalse',
            'TYPE\nSigned integer',
            'SIZE\n32',
            'DESCRIPTION\nThis is test parameter #2.',
            ]
        self.row2 = [s + '\n\n' for s in self.row2]

        self.parameters = {1: p1, 2: p2}
                
    def compare_arrays(self, arr1, arr2):
        for i in range(len(arr2)):
            with self.subTest(i=i):
                for j in range(len(arr2[0])):
                    with self.subTest(i=j):
                        self.assertEqual(arr1[i][j], arr2[i][j])   
        
    def test_all(self):
        arr = array(self.parameters, 'all', {})
        correct_arr = [self.row1, self.row2]
        self.compare_arrays(arr, correct_arr)
        
    def test_numbers(self):
        arr = array(self.parameters, [2,1], {})
        correct_arr = [self.row2, self.row1]
        self.compare_arrays(arr, correct_arr)
        
    def test_print(self):
        string = table(self.parameters, 'all', {})
        correct_string = (
"""
NUMBER  NAME         INDICES  MIN  MAX    DEFAULT  UNIT  WRITABLE  TYPE              SIZE  DESCRIPTION
1       Parameter 1  -        0    65535  0        s     True      Unsigned integer  16    This is test parameter #1.

NUMBER  NAME         INDICES  MIN  MAX    DEFAULT  UNIT  WRITABLE  TYPE              SIZE  DESCRIPTION
2       Parameter 2  1...5    -10  10     0        Hz    False     Signed integer    32    This is test parameter #2.
"""[1:] # Ignore the fiest '\n'.
)
        self.assertEqual(string, correct_string)
        
    def test_line_wrapping(self):
        description = (
            'This is a long string intended to test line wrapping. '
            'This is the secong sentence.\n'
            'This string also contains a manually instered line break. '
            'That is needed to make sure that the line wrapping function '
            'works correctly with existing line breaks.')
        parameter = dummy_parameter(description=description)
        parameters = {1: parameter}
        arr = array(parameters, [1], {'description':35})
        
        string = (
"""DESCRIPTION
This is a long string intended to
test line wrapping. This is the
secong sentence.
This string also contains a
manually instered line break. That
is needed to make sure that the
line wrapping function works
correctly with existing line
breaks.

"""
)     
        self.assertEqual(arr[0][-1], string)
        
        
if __name__ == '__main__':
    unittest.main()