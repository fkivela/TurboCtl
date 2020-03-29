"""Unit tests for the conversions module."""

import unittest

from test_turboctl import GenericTests
from turboctl import conversions as c

class TestUintsAndSints(GenericTests):
    
    def setUp(self):
        
        self.uint_to_sint_base_8 = {
            (  0, 8):    0,
            (  1, 8):    1,
            ( 10, 8):   10,
            (127, 8):  127,
            (128, 8): -128,
            (200, 8):  -56,
            (255, 8):   -1,
        }
        
        self.sint_to_uint_base_8 = {
            (out, base): num 
            for args, out in self.uint_to_sint_base_8.items()
            for num, base in [args]
            }
        
        self.uint_to_sint_base_16 = {
            (      0, 16):       0,
            (2**15-1, 16): 2**15-1,
            (  2**15, 16):  -2**15,
            (2**16-1, 16):      -1,
        }
        self.sint_to_uint_base_16 = {
            (out, base): num 
            for args, out in self.uint_to_sint_base_16.items()
            for num, base in [args]
            }
        
        self.invalid_uints = {
            (   -1,  8): ValueError,
            (  256,  8): ValueError,
            (   -1, 16): ValueError,
            (2**16, 16): ValueError,
        }
        
        self.invalid_sints = {
            (    -129,  8): ValueError,
            (     128,  8): ValueError,
            (-2**15-1, 16): ValueError,
            (   2**15, 16): ValueError,
        }

    def test_uint_to_sint_base_8(self):
        self._test_args(c.uint_to_sint, self.uint_to_sint_base_8)
        
    def test_uint_to_sint_base_16(self):
        self._test_args(c.uint_to_sint, self.uint_to_sint_base_16)
        
    def test_uint_to_sint_invalid_values(self):
        self._test_args(c.uint_to_sint, self.invalid_uints)

    def test_sint_to_uint_base_8(self):
        self._test_args(c.sint_to_uint, self.sint_to_uint_base_8)

    def test_sint_to_uint_base_16(self):
        self._test_args(c.sint_to_uint, self.sint_to_uint_base_16)
        
    def test_sint_to_uint_invalid_values(self):
        self._test_args(c.sint_to_uint, self.invalid_sints)
    

class TestStrings(GenericTests):
    
    def setUp(self):
        self.int_to_str = {
            (    1,  1):                '1',
            (    0,  8):         '00000000',
            (    1,  8):         '00000001',
            (  123,  8):         '01111011',
            (12345, 16): '0011000000111001',
        }
        self.str_to_int = {
            (string,): num 
            for args, string in self.int_to_str.items()
            for num, base in [args]
        }
        self.invalid_ints = {
            ( -1,  8): ValueError,
            (256,  8): ValueError,
        }
        self.invalid_strs = {
            (    '',): ValueError,
            ('0112',): ValueError,
        }
        
    def test_int_to_str(self):
        self._test_args(c.int_to_str, self.int_to_str)
        
    def test_int_to_str_invalid_values(self):
        self._test_args(c.int_to_str, self.invalid_ints)
        
    def test_str_to_int(self):
        self._test_args(c.str_to_int, self.str_to_int)
        
    def test_str_to_int_invalid_values(self):
        self._test_args(c.str_to_int, self.invalid_strs)
        
        
class TestSplittingAndCombining(GenericTests):
    
    def setUp(self):
        # A tuple is used instead of a dict, because lists are 
        # unhashable.
        self.combine = (
            # ints bits result
            [([0], 8), 0],
            [([10], 8), 10],
            # 001 + 010
            [([1,2], 3), 10],
            # 001 + 011 + 101
            [([1,3,5], 3), 93],
            # 00000101 + 00000010 + 00000110 + 00001000
            [([5,2,6,8], 8), 84018696],
            # 0000010011010010 + 0001011000101110
            [([1234, 5678], 16), 80877102],
        )
        self.split = (
            [(out, len(ints), base), ints] 
            for args, out in self.combine
            for ints, base in [args]
        )
        self.invalid_combine = (
            [(   [-1, 1], 8), ValueError],
            [(  [256, 0], 8), ValueError],
        )
        self.invalid_split = (
            # i, n_bytes, bytesize
            # 2**16 is too large for 2*8 bits
            [(2**16, 2, 8), ValueError],
            [(-1, 1, 8), ValueError],
            [(1, 0, 8), ValueError],
            [(1, -1, 8), ValueError],
        )
        
    def test_combine_ints(self):
        self._test_args(c.combine_ints, self.combine)
        
    def test_combine_ints_invalid_values(self):
        self._test_args(c.combine_ints, self.invalid_combine)
        
    def test_split_int(self):
        self._test_args(c.split_int, self.split)
        
    def test_split_int_invalid_values(self):
        self._test_args(c.split_int, self.invalid_split)
        
    
class TestFloats(GenericTests):
    
    def setUp(self):
        # A tuple is used instead of a dict, because 0.0 and -0.0 have 
        # the same hash values.
        self.floats = (
            [(123.456,   ), 1123477881],
            [( 78.90E30, ), 1954084586],
            [( 12.34E-40,),     880612], 
            [(  0.0,     ),          0],
            [( -0.0,     ),      2**31],
            [(  1.0E-50, ),          0],
            [( -1.0E-50, ),      2**31],
        )
        self.invalid_floats = (
            [(1E40,), ValueError],
        )
        self.ints = ([(i,), f[0]] for f, i in self.floats)
        
        self.invalid_ints = (
            [(-1,), ValueError],
            [(2**32,), ValueError],
        )

        self.infs_and_nans = (    
            # Infinities (exponent 255, significand 0)
            [(c.str_to_int('0' + 8*'1' + 23*'0'),), float('inf')],
            [(c.str_to_int('1' + 8*'1' + 23*'0'),), -float('inf')],
            # NaNs (exponent 255, significand nonzero)
            [(c.str_to_int('0' + 8*'1' + 22*'0' + '1'),), float('nan')], 
            [(c.str_to_int('1' + 8*'1' + 22*'0' + '1'),), -float('nan')],
        )

    def test_float_to_int(self):
        self._test_args(c.float_to_int, self.floats)
        
    def test_float_to_int_invalid_values(self):
        self._test_args(c.float_to_int, self.invalid_floats)
        
    def test_int_to_float(self):
        self._test_args(c.int_to_float, self.ints)
        
    def test_int_to_float_invalid_args(self):
        self._test_args(c.int_to_float, self.invalid_ints)
        
    def test_infs_and_nans(self):
        self._test_args(c.int_to_float, self.infs_and_nans)
            
        
if __name__ == '__main__':
    unittest.main()