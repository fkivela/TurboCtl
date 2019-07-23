import unittest

from turboctl import TypedBytes, Types

class TestUtils(unittest.TestCase):
            
    def test_repr(self):
        tb = TypedBytes([0,1,55,123,255])
        new_tb = eval(repr(tb))
        self.assertEqual(new_tb, tb)
        self.assertFalse(new_tb is tb)


class TestSetter(unittest.TestCase):
    
    def test_ints(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        tb[0] = 0
        tb[1] = 255
        tb[2:4] = 2**16-1
        tb[4:6] = 32769
        self.assertEqual(tb, TypedBytes([0, 255, 255, 255, 128, 1, 7, 8]))
        
    def test_signed_ints(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        tb[0] = 0
        tb[1] = 123
        tb[2] = -123
        tb[3] = -128
        tb[4] = -1
        tb[5:7] = -1234
        self.assertEqual(tb, TypedBytes([0, 123, 133, 128, 255, 251, 46, 8]))
        
    def test_too_large_ints_fail(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0] = 256
            
        with self.assertRaises(ValueError):
            tb[0:2] = 2**16
            
    def test_too_small_ints_fail(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0] = -129
            
        with self.assertRaises(ValueError):
            tb[0:2] = -2**15 - 1
            
    def test_strings(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        tb[0] = '0'
        tb[1] = '1111011'
        tb[2:4] = '11111111'
        tb[4:6] = '1000000000000001'
        self.assertEqual(tb, TypedBytes([0, 123, 0, 255, 128, 1, 7, 8]))
        
    def test_too_long_strings_fail(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0] = '1' + 8*'0'
            
        with self.assertRaises(ValueError):
            tb[0:2] = 17 * '1'
            
    def test_empty_string_fails(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0] = ''
                    
    def test_floats(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8,9,10,11,12])
        
        tb[0:4] = 123.456 # [66, 246, 233, 121]
        tb[4:8] = -0.00789 # [188, 1, 69, 15]
        tb[8:12] = 1.0 # [63, 128, 0, 0]
        
        self.assertEqual(tb, TypedBytes([66, 246, 233, 121, 
                                         188, 1, 69, 15,
                                         63, 128, 0, 0,]))
        
    def test_floats_fail_when_index_size_is_not_4(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0] = 1.0
            
        with self.assertRaises(ValueError):
            tb[0:2] = 1.0
            
        with self.assertRaises(ValueError):
            tb[0:3] = 1.0
            
        with self.assertRaises(ValueError):
            tb[0:5] = 1.0
                        
    def test_too_large_floats_fail(self):
        
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        with self.assertRaises(ValueError):
            tb[0:4] = 10**50
            
    def test_negative_indices_(self):
        tb = TypedBytes([1,2,3,4])
        tb[-1] = 1
        tb[-2:-1] = 2
        tb[0:-2] = 1027
        self.assertEqual(tb, TypedBytes([4,3,2,1]))
            
        
class TestGetter(unittest.TestCase):
    
    def test_ints(self):
        tb = TypedBytes([0, 1, 123, 255])
        self.assertEqual(tb[0], 0)
        self.assertEqual(tb[0:2], 1)
        self.assertEqual(tb[3], 255)
        self.assertEqual(tb[:], 97279)
        
    def test_signed_ints(self):
        tb = TypedBytes([0, 1, 123, 128, 255, 12])
        self.assertEqual(tb[0, Types.SINT], 0)
        self.assertEqual(tb[0:2, Types.SINT], 1)
        self.assertEqual(tb[2, Types.SINT], 123)
        self.assertEqual(tb[3, Types.SINT], -128)
        self.assertEqual(tb[4, Types.SINT], -1)
        self.assertEqual(tb[4:6, Types.SINT], -244)
        
    def test_strings(self):
        tb = TypedBytes([0, 1, 123, 255])
        self.assertEqual(tb[0, Types.STR], '00000000')
        self.assertEqual(tb[0:2, Types.STR], '0000000000000001')
        self.assertEqual(tb[2, Types.STR], '01111011')
        self.assertEqual(tb[3, Types.STR], '11111111')
        self.assertEqual(tb[:, Types.STR], ('00000000'
                                            '00000001'
                                            '01111011'
                                            '11111111'))
    def test_floats(self):
        bh = TypedBytes([66, 246, 233, 121, # 123.456
                         188, 1, 69, 15, # -0.00789
                         63, 128, 0, 0]) # [0 0 1.0]

        self.assertAlmostEqual(bh[0:4, Types.FLOAT], 123.456, 5)
        self.assertAlmostEqual(bh[4:8, Types.FLOAT], -0.00789)
        self.assertAlmostEqual(bh[8:12, Types.FLOAT], 1.0)      
        
    def test_floats_fail_when_index_size_is_not_4(self):
        tb = TypedBytes([1,2,3,4,5,6,7,8])
        
        with self.assertRaises(ValueError):
            tb[0, Types.FLOAT]
            
        with self.assertRaises(ValueError):
            tb[0:2, Types.FLOAT]
            
        with self.assertRaises(ValueError):
            tb[0:3, Types.FLOAT]
            
        with self.assertRaises(ValueError):
            tb[0:5, Types.FLOAT]
            
    def test_default_uint_type(self):
        # Values must be over 127 to distinguish between signed 
        # and unsigned integers.
        tb = TypedBytes([201,202,203])
        self.assertEqual(tb[0], 201)
        self.assertEqual(tb[1:3], 51915)
        
    def test_explicit_uint_type(self):
        tb = TypedBytes([201,202,203])
        self.assertEqual(tb[0, Types.UINT], 201)
        self.assertEqual(tb[1:3, Types.UINT], 51915)
                
    def test_negative_indices_(self):
        tb = TypedBytes([1,2,3,4])
        self.assertEqual(tb[-1], 4)
        self.assertEqual(tb[-2:-1], 3)
        self.assertEqual(tb[0:-2], 258)
            
        
if __name__ == '__main__':
    unittest.main()