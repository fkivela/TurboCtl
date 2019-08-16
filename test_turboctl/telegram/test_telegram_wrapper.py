"""Unit tests for the Telegram_Wrapper class of the 
telegram_wrapper module.
"""
import unittest

from turboctl import Types, Telegram, TelegramWrapper
from test_turboctl import dummy_parameter

class TestInit(unittest.TestCase):
    
    def setUp(self):
        self.data = Telegram(current=1).data
        self.telegram = Telegram(self.data)
        TelegramWrapper.parameters = {1: dummy_parameter(type_=Types.SINT)}
    
    def test_from_data(self):
        tw = TelegramWrapper(self.data)
        self.assertEqual(tw, self.telegram)
        
    def test_from_kwargs(self):
        tw = TelegramWrapper(current=1)
        self.assertEqual(tw, self.telegram)
        
    def test_setting_both_ata_and_kwargs_fails(self):
        with self.assertRaises(TypeError):
            TelegramWrapper(self.data, current=1)
            
    def test_parameter_number_kwarg_is_applied_first(self):
        # *parameter_number* must be set before *parameter_value*, 
        # because the value -1 can't be set if *parameter_type* is 
        # the default Types.UINT.
        tw = TelegramWrapper(parameter_value=-1, parameter_number=1)
        self.assertEqual(tw.parameter_number, 1)
        self.assertEqual(tw.parameter_type, Types.SINT)
        self.assertEqual(tw.parameter_value, -1)
        
    def test_invalid_parameter_number(self):
        tw = TelegramWrapper(parameter_number=0)
        self.assertEqual(tw.parameter_number, 0)
        
        
class Base(unittest.TestCase):
    
    def setUp(self):
        TelegramWrapper.parameters = {
            1: dummy_parameter(type_=Types.UINT, unit='0.1 °C'),
            2: dummy_parameter(type_=Types.SINT, indices=range(5)),
            3: dummy_parameter(type_=Types.FLOAT, size=32)}
        
        self.tw_invalid = TelegramWrapper(parameter_number=0)
        self.tw = TelegramWrapper(parameter_number=1)
        self.tw_sint = TelegramWrapper(parameter_number=2)
        self.tw_float = TelegramWrapper(parameter_number=3)

        
class TestParameterNumber(Base):
    
    def test_setter_fails_after_init_with_kwargs(self):
        with self.assertRaises(RuntimeError):
            self.tw.parameter_number=2
            
    def test_setter_fails_after_default_init(self):
        tw = TelegramWrapper()
        with self.assertRaises(RuntimeError):
            tw.parameter_number=2
            
    def test_setter_fails_after_init_from_data(self):
        data = Telegram(parameter_number=2).data
        tw = TelegramWrapper(data)
        
        with self.assertRaises(RuntimeError):
            tw.parameter_number=2
        
    def test_getter(self):
        self.assertEqual(self.tw.parameter_number, 1)
        self.assertEqual(self.tw_invalid.parameter_number, 0)
        
            
class TestParameterValue(Base):
                
    def test_as_kwarg(self):
        tw = TelegramWrapper(parameter_number=1, parameter_value=10)
        self.assertEqual(tw.parameter_value, 10)
        
    def test_uint(self):
        self.tw.parameter_value = 123
        # Make sure the same value is returned.
        self.assertEqual(self.tw.parameter_value, 123)
        # Make sure the value is actually saved in the correct 
        # format by using the already-tested Telegram.parameter_value 
        # function.
        self.assertEqual(Telegram.parameter_value.fget(self.tw), 123)
        
    def test_sint(self):
        
        self.tw_sint.parameter_value = -123
        self.assertEqual(self.tw_sint.parameter_value, -123)
        self.assertEqual(
            Telegram.get_parameter_value(self.tw_sint, Types.SINT), -123)
        
    def test_float(self):
        
        self.tw_float.parameter_value = 123.456
        self.assertAlmostEqual(self.tw_float.parameter_value, 123.456, 5)
        self.assertAlmostEqual(
            Telegram.get_parameter_value(self.tw_float, Types.FLOAT), 
            123.456, 5)
        
    def test_int_to_float(self):
        # Float parameters can be given int values and vice versa.
        # In this case the value is converted to the correct type.
        self.tw_float.parameter_value = 123
        self.assertAlmostEqual(self.tw_float.parameter_value, 123.000, 5)
        
    def test_float_to_int(self):
        self.tw.parameter_value = 123.456
        self.assertEqual(self.tw.parameter_value, 123)
        
    def test_invalid_type_fails(self):
        # Types other than int or float should fail.
        with self.assertRaises(TypeError):
            self.tw.parameter_value = [1]
            
    def test_invalid_value_fails(self):
        # A negative sint cannot be converted to an uint.
        with self.assertRaises(ValueError):
            self.tw.parameter_value = -1


class TestReadOnlyProperties(Base):
            
    def test_parameter_type(self):
        self.assertEqual(self.tw.parameter_type, Types.UINT)
        self.assertEqual(self.tw_sint.parameter_type, Types.SINT)
        self.assertEqual(self.tw_float.parameter_type, Types.FLOAT)
        self.assertEqual(self.tw_invalid.parameter_type, Types.UINT)
            
    def test_parameter_size(self):
        self.assertEqual(self.tw.parameter_size, 16)
        self.assertEqual(self.tw_float.parameter_size, 32)
        self.assertEqual(self.tw_invalid.parameter_size, 0)
    
    def test_parameter_unit(self):
        self.assertEqual(self.tw.parameter_unit, '0.1 °C')
        self.assertEqual(self.tw_invalid.parameter_unit, '')
    
    def test_parameter_indexed(self):
        tw_indexed = TelegramWrapper(parameter_number=2)
        
        self.assertTrue(tw_indexed.parameter_indexed)
        self.assertFalse(self.tw.parameter_indexed)
        self.assertFalse(self.tw_invalid.parameter_indexed)
        
            
if __name__ == '__main__':
    unittest.main()