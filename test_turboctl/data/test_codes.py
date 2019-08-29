"""Unit tests for the codes module. 

Since the codes module contains mostly data, these tests only make 
sure that the superclasses ValueAndDescription and IntAndDescription 
defined in that module work as intended.
"""

import unittest

from turboctl import ParameterAccess, ControlBits

class TestValueAndDescription(unittest.TestCase):
    
    def test_syntax(self):
        """Make sure enum members can be accessed using any valid 
        syntax.
        """
        self.assertEqual(ParameterAccess['NONE'], ParameterAccess.NONE)
        self.assertEqual(ParameterAccess('0000'), ParameterAccess.NONE)
        self.assertEqual(ParameterAccess(ParameterAccess.NONE), 
                         ParameterAccess.NONE)
        
    def test_fields(self):
        """Make sure both attributes can be accessed."""
        self.assertEqual(ParameterAccess.NONE.value, '0000')
        self.assertEqual(ParameterAccess.NONE.description, 'No access')
        
class TestIntAndDescription(unittest.TestCase):
    """Make sure members of IntAndDescription enums behave like 
    ints.
    """
        
    def test_set(self):
        """Make sure sets of enum members behave as they should."""
        bitnames = [    
            'ON', 'UNUSED1', 'UNUSED2', 'UNUSED3', 'UNUSED4', 'X201', 
            'SETPOINT', 'RESET_ERROR', 'STANDBY', 'UNUSED9', 'COMMAND', 
            'X1_ERROR', 'X1_WARNING', 'X1_NORMAL', 'X202', 'X203'
        ]
        self.maxDiff = None
        bits_in_order = [ControlBits[name] for name in bitnames]
        # Reverse bit order to test sorting.
        bits_reversed = bits_in_order[::-1]
        # list() automatically sorts a set of ints.
        bits_should_be_in_order = list(set(bits_reversed))
        
        # Make sure the bits are in the correct order and all of them 
        # are present (i.e. hashing works)
        self.assertEqual(bits_should_be_in_order, bits_in_order)
        self.assertEqual(bits_should_be_in_order, list(range(16)))
        
    def test_equal(self):
        """Make sure ControlBits are equal to ints."""
        self.assertEqual(ControlBits.ON, 0)
        self.assertEqual(ControlBits.COMMAND, 10)
        
    def test_add(self):
        """Make sure ControlBits are compatible with arithmetical 
        operations.
        """
        self.assertEqual(ControlBits.COMMAND + ControlBits.ON, 10)
    
    
if __name__ == '__main__':
    unittest.main()