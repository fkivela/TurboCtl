"""Unit tests for the byteholder module."""
import unittest
import itertools

from turboctl import ByteHolder

class TestInit(unittest.TestCase):
    
    def setUp(self):
        
        self.zeros = 5*[0]
        self.empty_bhs = [ByteHolder(5), 
                          ByteHolder(self.zeros), 
                          ByteHolder(bytes(self.zeros)), 
                          ByteHolder(bytearray(self.zeros))]
        
        self.nums = [1,2,3,4,5]
        self.full_bhs = [ByteHolder(self.nums),
                         ByteHolder(bytes(self.nums)),
                         ByteHolder(bytearray(self.nums))]

    def test_empty_byteholders_equal(self):
        
        for bh1, bh2 in itertools.combinations(self.empty_bhs,2):
            self.assertEqual(bh1, bh2)
            
    def test_empty_byteholders_not_same_object(self):
        
        for bh1, bh2 in itertools.combinations(self.empty_bhs,2):
            self.assertTrue(bh1 is not bh2)
            
    def test_empty_contents_correct(self):
        
        for bh in self.empty_bhs:
            self.assertEqual(bh.data, bytearray(self.zeros))
            
    def test_empty_contents_not_same_onject(self):
        
        for bh1, bh2 in itertools.combinations(self.empty_bhs,2):
            self.assertTrue(bh1.data is not bh2.data)
            
    def test_full_bhs_equal(self):
        
        for bh1, bh2 in itertools.combinations(self.full_bhs,2):
            self.assertEqual(bh1, bh2) 
                             
    def test_full_bhs_not_same(self):
    
        for bh1, bh2 in itertools.combinations(self.full_bhs,2):
            self.assertTrue(bh1 is not bh2) 
                                
    def test_full_contents_correct(self): 
        for bh in self.full_bhs:
            self.assertEqual(bh.data, bytearray(self.nums))
        
    def test_full_contents_not_same(self):

        for bh1, bh2 in itertools.combinations(self.full_bhs,2):
            self.assertTrue(bh1.data is not bh2.data)
        
        
class TestSetter(unittest.TestCase):
    
    def setUp(self):
        self.bh = ByteHolder([1,2,3,4,5,6,7,8])
                
    def test_single_index(self):
        bh = self.bh
        
        bh[0] = 0
        bh[4] = 123
        bh[7] = 255
        
        self.assertEqual(bh, ByteHolder([0,2,3,4,123,6,7,255]))
        
    def test_slice(self):
        bh = self.bh
        
        bh[0:2] = 1234
        bh[2:5] = 567890
        bh[-2:] = 90
        # 1234 dec = 100 11010010 bin = 4, 210 dec
        # 567890 dec = 1000 10101010 01010010 bin = 8, 170, 82 dec
        
        self.assertEqual(bh, ByteHolder([4, 210, 8, 170, 82, 6, 0, 90]))
                    
    def test_too_large_fails(self):
        bh = self.bh
        
        with self.assertRaises(ValueError):
            bh[0] = 256
            
        with self.assertRaises(ValueError):
            bh[0:2] = 2**16
                        
    def test_bad_values_fail(self):
        bh = self.bh
        
        with self.assertRaises(ValueError):
            bh[0] = -1
            
        with self.assertRaises(TypeError):
            bh[0] = '1'
            
        with self.assertRaises(TypeError):
            bh[0] = 1.0
            
    def test_bad_indices_fail(self):
        bh = self.bh
        
        with self.assertRaises(IndexError):
            bh[1000] = 0
        
        with self.assertRaises(TypeError):
            bh['1'] = 0
            
        with self.assertRaises(TypeError):
            bh[1.0] = 0
            
            
class TestGetter(unittest.TestCase):
    
    def setUp(self):        
        list_ = [0, 123, 255, 133]
        self.bh = ByteHolder(list_)
            
    def test_single_index(self):
        bh = self.bh
        
        self.assertEqual(bh[0], 0)
        self.assertEqual(bh[1], 123)
        self.assertEqual(bh[2], 255)
        self.assertEqual(bh[3], 133)

    def test_slice(self):
        bh = self.bh
        
        self.assertEqual(bh[0:2], 123)
        
        # 123, 255 dec = 01111011 11111111 bin = 31743 dec
        self.assertEqual(bh[1:3], 31743)
        
        # 0, 123, 255, 133 dec 
        # = 00000000 01111011 11111111 10000101 bin
        # = 8126341 dec
        self.assertEqual(bh[:], 8126341)
        
    def test_bad_indices_fail(self):
        bh = self.bh

        with self.assertRaises(IndexError):
            bh[1000] = 0
        
        with self.assertRaises(TypeError):
            bh['1'] = 0
            
        with self.assertRaises(TypeError):
            bh[1.0] = 0
            
            
class TestUtils(unittest.TestCase):
            
    def test_str(self):
        bh = ByteHolder([0,1,55,123,255])
        str_ = ('ByteHolder([0, 1, 55, 123, 255])')    
        self.assertEqual(str(bh), str_)
        
    def test_repr(self):
        bh = ByteHolder([0,1,55,123,255])
        new_bh = eval(repr(bh))
        self.assertEqual(new_bh, bh)
        self.assertFalse(new_bh is bh)
        
    def test_eq(self):
        
        bh1 = ByteHolder([1,2,3,4])
        bh2 = ByteHolder([1,2,3,4])
        bh3 = ByteHolder([1,2,3,5])
        
        self.assertEqual(bh1, bh1)
        self.assertEqual(bh1, bh2)
        self.assertNotEqual(bh1, bh3)
        # Make sure comparison with a non-ByteHolder object doesn't
        # raise errors
        self.assertNotEqual(bh1, 1)
        
    def test_len(self):
        bh = ByteHolder(15)
        self.assertEqual(len(bh), 15)

        
if __name__ == '__main__':
    unittest.main()        