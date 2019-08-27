"""Unit tests for the Types module."""

import unittest

from turboctl import Types

class TestToType(unittest.TestCase):
            
    def test_uint(self):
        self.assertEqual(Types.to_type('123', Types.UINT), 123)
        
    def test_sint(self):
        self.assertEqual(Types.to_type('-123', Types.SINT), -123)
        
    def test_str(self):
        self.assertEqual(Types.to_type(123, Types.STR), '123')
        
    def test_float(self):
        self.assertEqual(Types.to_type('1.23E2', Types.FLOAT), 123.0)
        
    def test_int_to_float(self):
        self.assertAlmostEqual(Types.to_type(123, Types.FLOAT), 123.00, 5)
        
    def test_float_to_sint(self):
        self.assertEqual(Types.to_type(-123.456, Types.SINT), -123)
        
    def test_negative_int_to_uint_fails(self):
        with self.assertRaises(ValueError):
            Types.to_type(-1, Types.UINT)
        
    def test_invalid_type_fails(self):
        with self.assertRaises(TypeError):
            Types.to_type(123, int)
            
    def test_invalid_value_fails(self):
        with self.assertRaises(ValueError):
            Types.to_type('test', Types.UINT)
        
        
class TestTypeOf(unittest.TestCase):
    
    def test_uint(self):
        self.assertEqual(Types.type_of(123), Types.UINT)
        
    def test_sint(self):
        self.assertEqual(Types.type_of(-123), Types.SINT)
        
    def test_str(self):
        self.assertEqual(Types.type_of('123'), Types.STR)
        
    def test_float(self):
        self.assertEqual(Types.type_of(1.23E2), Types.FLOAT)
        
    def test_other_fails(self):
        with self.assertRaises(TypeError):
            Types.type_of([123])
        
        
class TestIsType(unittest.TestCase):
    
    def test_uint_is_uint(self):
        self.assertTrue(Types.is_type(123, Types.UINT))
        
    def test_sint_is_sint(self):
        self.assertTrue(Types.is_type(-123, Types.SINT))
        
    def test_str_is_str(self):
        self.assertTrue(Types.is_type('123', Types.STR))
        
    def test_float_is_float(self):
        self.assertTrue(Types.is_type(1.23E2, Types.FLOAT))
    
    
    def test_uint_is_sint(self):
        self.assertTrue(Types.is_type(123, Types.SINT))
    
    def test_uint_is_not_str(self):
        self.assertFalse(Types.is_type(123, Types.STR))
        
    def test_uint_is_not_float(self):
        self.assertFalse(Types.is_type(123, Types.FLOAT))
        
    def test_uint_is_not_int(self):
        self.assertFalse(Types.is_type(123, int))
    
    
    def test_sint_is_not_uint(self):
        self.assertFalse(Types.is_type(-123, Types.UINT))
        
    def test_sint_is_not_str(self):
        self.assertFalse(Types.is_type(-123, Types.STR))
        
    def test_sint_is_not_float(self):
        self.assertFalse(Types.is_type(-123, Types.FLOAT))
        
    def test_sint_is_not_int(self):
        self.assertFalse(Types.is_type(-123, int))
        
    
    def test_str_is_not_uint(self):
        self.assertFalse(Types.is_type('123', Types.UINT))
        
    def test_str_is_not_sint(self):
        self.assertFalse(Types.is_type('123', Types.SINT))
        
    def test_str_is_not_float(self):
        self.assertFalse(Types.is_type('123', Types.FLOAT))
        
    def test_str_is_not_built_in_str(self):
        self.assertFalse(Types.is_type('123', str))
        
        
    def test_float_is_not_uint(self):
        self.assertFalse(Types.is_type(1.23E2, Types.UINT))
        
    def test_float_is_not_sint(self):
        self.assertFalse(Types.is_type(1.23E2, Types.SINT))
        
    def test_float_is_not_str(self):
        self.assertFalse(Types.is_type(1.23E2, Types.STR))
        
    def test_float_is_not_built_in_float(self):
        self.assertFalse(Types.is_type(1.23E2, float))
        

if __name__ == '__main__':
    unittest.main()