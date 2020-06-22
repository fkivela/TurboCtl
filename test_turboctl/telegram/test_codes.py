"""Unit tests for the codes module. 

Since the codes module contains mostly data, these tests only make 
sure that the superclasses ValueAndDescription and IntAndDescription 
defined in that module work as intended.
"""
import random
import unittest

from turboctl.telegram.codes import (ParameterAccess, ParameterResponse, 
                                     get_parameter_code, get_parameter_mode,
                                     WrongNumError, ParameterError,
                                     ControlBits ,StatusBits)


class TestParameterCode(unittest.TestCase):
    
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
        self.assertEqual(ParameterAccess.NONE.mode, 'none')
        self.assertEqual(ParameterAccess.NONE.indexed, ...)
        self.assertEqual(ParameterAccess.NONE.bits, ...)
        self.assertEqual(ParameterAccess.NONE.description, 'No access')


class TestGetParameterCode(unittest.TestCase):
    
    def test_examples(self):
        code = get_parameter_code('query', 'none', False, 16)
        self.assertEqual(code, ParameterAccess.NONE)
        
        code = get_parameter_code('reply', 'none', False, 16)
        self.assertEqual(code, ParameterResponse.NONE)

        code = get_parameter_code('query', 'write', False, 16)
        self.assertEqual(code, ParameterAccess.W16)
        
        code = get_parameter_code('reply', 'response', True, 32)
        self.assertEqual(code, ParameterResponse.S32F)

        code = get_parameter_code('reply', 'error', False, 16)
        self.assertEqual(code, ParameterResponse.ERROR)

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            get_parameter_code('qery', 'none', False, 16)
        
    def test_no_matches(self):
        with self.assertRaises(ValueError):
            get_parameter_code('query', 'response', False, 16)

        
class TestCustomIntEnums(unittest.TestCase):
    """Make sure inheriting CustomInt makes enum members behave like ints."""
        
    def test_set(self):
        """Make sure sets of enum members behave as they should."""
        
        # Names of enum members in the correct order.
        bitnames = [
            'ON', 'UNUSED1', 'UNUSED2', 'UNUSED3', 'UNUSED4', 'X201', 
            'SETPOINT', 'RESET_ERROR', 'STANDBY', 'UNUSED9', 'COMMAND', 
            'X1_ERROR', 'X1_WARNING', 'X1_NORMAL', 'X202', 'X203'
        ]
        # Numbers of enum members in order.
        bits_in_order = [ControlBits[name] for name in bitnames]

        # Print long error messages so that the order of all bits can be seen.  
        self.maxDiff = None
        
        # Unsort the bits by reversing their order.
        bits_reversed = bits_in_order[::-1]
        # list() automatically sorts a set of ints.
        bits_should_be_in_order = list(set(bits_reversed))
        
        # Make sure the bits are in the correct order and all of them 
        # are present (i.e. hashing works)
        self.assertEqual(bits_should_be_in_order, bits_in_order)
        self.assertEqual(bits_should_be_in_order, list(range(16)))
        
    def test_equal(self):
        """Make sure enum members are equal to ints."""
        self.assertEqual(ControlBits.ON, 0)
        self.assertEqual(ControlBits.COMMAND, 10)
        
    def test_add(self):
        """Make sure enum members are compatible with arithmetical 
        operations.
        """
        self.assertEqual(ControlBits.COMMAND + ControlBits.ON, 10)


class TestCustomIntEnumFields(unittest.TestCase):
    """Make sure ParameterError, ControlBits an FlagBits members function and
    have the fields they should have.
    """
    
    def test_parameter_error(self):
        member = ParameterError.WRONG_NUM
        self.assertEqual(member, 0)
        self.assertEqual(member.value, 0)
        self.assertEqual(member.description, 'Invalid parameter number')
        with self.assertRaises(WrongNumError):
            raise member.exception('Test')
            
    def test_control_bits(self):
        member = ControlBits.ON
        self.assertEqual(member, 0)
        self.assertEqual(member.value, 0)
        self.assertEqual(member.description, 'Turn or keep the pump on')

    def test_status_bits(self):
        member = StatusBits.READY
        self.assertEqual(member, 0)
        self.assertEqual(member.value, 0)
        self.assertEqual(member.description, 'Ready for operation')

        
if __name__ == '__main__':
    unittest.main()