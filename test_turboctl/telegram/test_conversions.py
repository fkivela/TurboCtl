"""Unit tests for the conversions module."""

import unittest
import math

from turboctl import (
    in_signed_range, 
    in_unsigned_range, 
    signed_to_unsigned_int, 
    unsigned_to_signed_int, 
    str_to_int, 
    int_to_str, 
    combine_ints, 
    split_int, 
    float_to_int, 
    int_to_float
)

class SignBase(unittest.TestCase):
    
    def setUp(self):
        
        # Test all possible 3 bit signed positive values.
        # The corresponding unsigned values are the same.
        self.signed_positives_3 = [0,1,2,3] 
                
        # For 8 bits, add the smallest value over 3 bits (4), 
        # a two-number 8 bit value (12) and the largest 8 bit 
        # value (127).
        self.signed_positives_8 = self.signed_positives_3 + [4, 12, 127]
        
        # For 16 bits, add the smallest value over 8 bits (128), 
        # a four-number 16 bit value (1234), 
        # and the largest 16 bit value (2**15-1).         
        self.signed_positives_16 \
            = self.signed_positives_8 + [128, 1234, 2**15-1]
        
        
        # Test all possible 3 bit signed negative values.
        # The second value in the tuple is the corresponding unsigned 
        # value.
        self.signed_negatives_3 = [(-1, 7),
                                   (-2, 6),
                                   (-3, 5),
                                   (-4, 4)]
        
        # For 8 and 16 bits, test the smallest and largest negative 
        # numbers and a few values in between them.
        self.signed_negatives_8 = [( -1,  255),
                              ( -2,  254),
                              (-12,  244),
                              (-128, 128)]
        
        self.signed_negatives_16 = [(    -1, 2**16 -   1),
                               (    -2, 2**16 -   2),
                               (   -12, 2**16 -  12),
                               (  -128, 2**16 - 128),
                               (-2**15, 2**15      )]
        

class TestSignedToUnsignedInt(SignBase):
    
    def test_positives_return_themselves(self):
                        
        for v in self.signed_positives_3:
            self.assertEqual(signed_to_unsigned_int(v, bits=3), v)
            
        for v in self.signed_positives_8:
            self.assertEqual(signed_to_unsigned_int(v, bits=8), v)
            
        for v in self.signed_positives_16:
            self.assertEqual(signed_to_unsigned_int(v, bits=16), v)

    def test_negatives_return_correct_values(self):
                
        for s, u in self.signed_negatives_3:
            self.assertEqual(signed_to_unsigned_int(s, bits=3), u)
            
        for s, u in self.signed_negatives_8:
            self.assertEqual(signed_to_unsigned_int(s, bits=8), u)
            
        for s, u in self.signed_negatives_16:
            self.assertEqual(signed_to_unsigned_int(s, bits=16), u)
            
    def test_too_large_positives_fail(self):
        
        # Test values that are 1 too large
        
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(4, 3) # 4 = 2**2
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(128, 8) # 128 = 2**7
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(2**15, 16)
            
        # Test values that are far too large
        
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(100, 3)
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(1000, 8)
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(100000, 16)
            
    def test_too_small_negatives_fail(self):
        
        # Test values that are 1 too small
        
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-5, 3) # -5 = -2**2 - 1
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-129, 8) # -129 = -2**7 - 1
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-2**15 - 1, 16)
            
        # Test values that are far too small

        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-100, 3)
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-1000, 8)
            
        with self.assertRaises(ValueError):
            signed_to_unsigned_int(-100000, 16)
            
            
class TestUnsignedToSignedInt(SignBase):
    
    def test_small_positives_return_themselves(self):
        
        for v in self.signed_positives_3:
            self.assertEqual(unsigned_to_signed_int(v, bits=3), v)
            
        for v in self.signed_positives_8:
            self.assertEqual(unsigned_to_signed_int(v, bits=8), v)
            
        for v in self.signed_positives_16:
            self.assertEqual(unsigned_to_signed_int(v, bits=16), v)
            
    def test_large_positives_return_negatives(self):
        
        # This is the same as 
        # TestSignedToUnsignedInt.test_negatives_return_correct_values
        # but in reverse.
        for s, u in self.signed_negatives_3:
            self.assertEqual(unsigned_to_signed_int(u, bits=3), s)
            
        for s, u in self.signed_negatives_8:
            self.assertEqual(unsigned_to_signed_int(u, bits=8), s)
            
        for s, u in self.signed_negatives_16:
            self.assertEqual(unsigned_to_signed_int(u, bits=16), s)
        
    def test_too_large_values_fail(self):
        
        # Test values that are 1 too large
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(8, 3) # 8 = 2**3
        
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(256, 8) # 256 = 2**8
                    
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(2**16, 16)
            
        # Test values that are far too large
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(100, 3) # 8 = 2**3
        
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(1000, 8) # 256 = 2**8
                    
        with self.assertRaises(ValueError):
            unsigned_to_signed_int(100000, 16)
            
    def test_negative_values_fail(self):
        
        for b in [3, 8, 16]:
            with self.assertRaises(ValueError):
                unsigned_to_signed_int(-1, b)
            with self.assertRaises(ValueError):
                unsigned_to_signed_int(-10, b)
                
                
class StringsBase(unittest.TestCase):
    
    def setUp(self):
        
        self.strings = [('000', 0),
                        ('00000000', 0),
                        ('11111111', 255), 
                        (15*'0'+'1', 1),
                        ('01111011', 123),
                        ('0011000000111001', 12345)]
                
        
class TestStrToInt(StringsBase):
    
    def test_strings_are_correct(self):
        
        for string, num in self.strings:
            self.assertEqual(str_to_int(string), num)
                
    def test_nonbinary_strings_fail(self):
        
        with self.assertRaises(ValueError):
            str_to_int('11111112')
            
        with self.assertRaises(ValueError):
            str_to_int('000a0000')
        
    def test_empty_string_fails(self):
        
        with self.assertRaises(ValueError):
            str_to_int('')
        
        
class TestIntToStr(StringsBase):
            
    def test_string_value(self):
        
        for string, num in self.strings:
            self.assertEqual(int_to_str(num, len(string)), string)
                
    def test_too_large_values_fail(self):
        
        with self.assertRaises(ValueError):
            int_to_str(9, 3)
            
        with self.assertRaises(ValueError):
            int_to_str(256, 8)
            
        with self.assertRaises(ValueError):
            int_to_str(10**20, 16)
            
    def test_negative_values_fail(self):
        
        with self.assertRaises(ValueError):
            int_to_str(-1, 3)
            
        with self.assertRaises(ValueError):
            int_to_str(-1000, 8)
            
            
class CombinationsBase(unittest.TestCase):
    
    def setUp(self):
        
        self.numbers = [(0, 3), (1, 8), (10, 8), (10000, 16)]
        
        self.combinations = [
                # 001 + 010
                ([1,2], 3, 10), 
                # 001 + 011 + 101
                ([1,3,5], 3, 93), 
                # 00000101 + 00000010 + 00000110 + 00001000
                ([5,2,6,8], 8, 84018696),
                 # 0000010011010010 + 0001011000101110
                ([1234, 5678], 16, 80877102)
        ]
            
        
class TestCombineInts(CombinationsBase):
    
    def test_single_numbers_return_themselves(self):
        
        for num, bits in self.numbers:
            self.assertEqual(combine_ints([num], bits), num)
        
    def test_combinations(self):
        
        for numbers, bits, combined_number in self.combinations:
            self.assertEqual(combine_ints(numbers, bits), combined_number) 
        
    def test_too_large_values_fail(self):
        
        with self.assertRaises(ValueError):
            combine_ints([8], 3)
            
        with self.assertRaises(ValueError):
            combine_ints([1, 2, 256], 8)
            
    def test_negative_values_fail(self):
        
        with self.assertRaises(ValueError):
            combine_ints([-1], 3)
        
        with self.assertRaises(ValueError):
            combine_ints([1, 2, -10], 8)
            
            
class TestSplitInt(CombinationsBase):
    
    def test_splitting_to_one_returns_original_number(self):
        
        for num, bits in self.numbers:
            self.assertEqual(split_int(num, 1, bits), [num])
            
    def test_correct_number_of_return_values(self):
        
        for numbers, bits, combined_number in self.combinations:
            self.assertEqual(
                    split_int(combined_number, len(numbers), bits), numbers) 
                
    def test_splits(self):
        
        for numbers, bits, combined_number in self.combinations:
            self.assertEqual(
                    split_int(combined_number, len(numbers), bits), numbers) 

    def test_too_large_values_fail(self):
        
        # 8 is too large for 1*3 bits
        with self.assertRaises(ValueError):
            split_int(i=8, n_bytes=1, bytesize=3)
            
        # 2**16 is too large for 4*4 bits
        with self.assertRaises(ValueError):
            split_int(i=2**16, n_bytes=4, bytesize=4)
        
    def test_negative_values_fail(self):
        
        with self.assertRaises(ValueError):
            split_int(-1, 1, 3)
            
        with self.assertRaises(ValueError):
            split_int(-10, 2, 8)
            
    def test_splitting_to_zero_or_negative_parts_fails(self):
        
        with self.assertRaises(ValueError):
            split_int(1, 0, 8)
            
        with self.assertRaises(ValueError):
            split_int(10, -2, 8)
            
            
class FloatBase(unittest.TestCase):
    
    def setUp(self):
        
        # The first bit in a float is a sign bit,
        # and so 0.0 and -0.0 have different binary
        # representations.
        self.numbers = [(123.456, 1123477881), 
                        (78.90E30, 1954084586), 
                        (12.34E-40, 880612), 
                        (0.0, 0),
                        (-0.0, 2**31)
                        ]
        
        # Infinities (exponent 255, significand 0)
        self.plusinf = str_to_int('01111111100000000000000000000000')
        self.minusinf = str_to_int('11111111100000000000000000000000')
        # NaNs (exponent 255, significand nonzero)
        self.plusnan = str_to_int('01111111100000000000000000000001')
        self.minusnan = str_to_int('11111111100000000000000000000001')
        
        
class TestFloatToInt(FloatBase):
    
    def test_numbers(self):
        
        for x, i in self.numbers:
            self.assertEqual(float_to_int(x), i)
            
    def test_nans(self):
        
        self.assertTrue(float_to_int(self.plusnan) > 2*255)
        self.assertTrue(float_to_int(self.minusnan) > 2*255)
                    
    def test_infs(self):
        
        self.assertEqual(float_to_int(float('inf')), self.plusinf)
        self.assertEqual(float_to_int(-float('inf')), self.minusinf)
           
    def test_numbers_very_close_to_zero_count_as_zero(self):
       
        # 1E-50 behaves as 0.0
        self.assertEqual(float_to_int(1E-50), 0)
        
        # -1E-50 behaves as -0.0
        self.assertEqual(float_to_int(-1E-50), 2**31)
           
    def test_too_large_values_fail(self):
       
        with self.assertRaises(ValueError):
            float_to_int(1E40)
        
        
class TestIntToFloat(FloatBase):
    
    def test_numbers(self):
        
        for x, i in self.numbers:
            self.assertAlmostEqual(int_to_float(i), x, delta=(1E-5 * x))
            
    def test_nans(self):
                
        # There should be no difference between +nan and -nan
        self.assertTrue(math.isnan(int_to_float(self.plusnan)))
        self.assertTrue(math.isnan(int_to_float(self.minusnan)))
            
    def test_infs(self):
                
        self.assertEqual(int_to_float(self.plusinf), float('inf'))
        self.assertEqual(int_to_float(self.minusinf), -float('inf'))
            
    def test_too_large_values_fail(self):
        
         with self.assertRaises(ValueError):
            int_to_float(2**32)
            
    def test_negative_values_fail(self):
        
         with self.assertRaises(ValueError):
            int_to_float(-1)
            
            
class TestInverses(unittest.TestCase):
    
    @staticmethod
    def sint_to_sint(i, bits):
        return unsigned_to_signed_int(
                signed_to_unsigned_int(i, bits), bits)
    
    @staticmethod
    def uint_to_uint(i, bits):
        return signed_to_unsigned_int(
                unsigned_to_signed_int(i, bits), bits)
    @staticmethod 
    def str_to_str(s, bits):
        return int_to_str(str_to_int(s), bits)
    
    @staticmethod
    def int_to_str_to_int(i, bits):
        return str_to_int(int_to_str(i, bits))
    
    @staticmethod
    def split_combined_ints(ints, bits):
        return split_int(combine_ints(ints, bits), len(ints), bits)
    
    @staticmethod     
    def combine_split_int(i, n_ints, bits):
        return combine_ints(split_int(i, n_ints, bits), bits)
    
    @staticmethod     
    def float_to_float(x):
        return int_to_float(float_to_int(x))
    
    @staticmethod
    def int_to_float_to_int(i):
        return float_to_int(int_to_float(i))
    
    def test_sint_to_sint(self):
        bits = 8
        self.assertEqual(self.sint_to_sint(-123, bits), -123)
        
    def test_uint_to_uint(self):
        bits = 8
        self.assertEqual(self.uint_to_uint(123, bits), 123)    
        
    def test_str_to_str(self):
        bits = 8
        self.assertEqual(self.str_to_str('11000011', bits), '11000011')    
        
    def test_int_to_str_to_int(self):
        bits = 8
        self.assertEqual(self.int_to_str_to_int(123, bits), 123)    
        
    def test_split_combined_ints(self):
        bits = 8
        self.assertEqual(
                self.split_combined_ints([1,2,3,4,5], bits), [1,2,3,4,5])
        
    def test_combine_split_int(self):
        n_bytes = 5
        bits = 8
        self.assertEqual(
                self.combine_split_int(1234567890, n_bytes, bits), 1234567890)    
        
    def test_float_to_float(self):
        self.assertAlmostEqual(self.float_to_float(3.14159), 3.14159, 6)    
        
    def test_int_to_float_to_int(self):
        self.assertEqual(self.int_to_float_to_int(1234567890), 1234567890)
        
if __name__ == '__main__':
    unittest.main()
