"""Unit tests for the numtypes module."""

import unittest

from test_turboctl import GenericTests
from turboctl import TurboNum, Uint, Sint, Float, Bin

class TestTurboNum(GenericTests):
    
    def test_init(self):
        args = {(123      ,): Uint(123),
                (-123     ,): Sint(-123),
                (123.456  ,): Float(123.456),
                ('1111011',): Bin('1111011')}
        def to_type(*args):
            return TurboNum(*args)     
        self._test_args(to_type, args)
        
    def test_invalid_args(self):
        args = {(256   ,  ): ValueError,
                (-129  ,  ): ValueError,
                (1E40  ,  ): ValueError,
                ('1111', 3): ValueError}
        def to_type(*args):
            return TurboNum(*args)     
        self._test_args(to_type, args)
        
    def test_to(self):
        self.assertEqual(Uint(123).to(Bin), Bin('1111011', 8))
        self.assertEqual(Float(123.456).to(Uint), Uint(1123477881, 32))

class TestUint(GenericTests):
    
    def test_init(self):
        args = {(      1,   ):       1,
                (    255,   ):     255,
                (2**16-1, 16): 2**16-1,
                (    '5',   ):       5,
                (    1.2,   ):       1}        
        self._test_args(Uint, args)
        
    def test_type(self):
        self.assertIsInstance(Uint(1), Uint)
        self.assertIsInstance(Uint.from_bytes(bytes([1])), Uint)
    
    def test_inheritance(self):
        x = Uint(5)
        self.assertEqual(x, 5)
        self.assertEqual(x + 1, 6)
        self.assertEqual(x**2, 25)

    def test_bits(self):
        self.assertEqual(Uint(5).bits, 8)
        self.assertEqual(Uint(100, 10).bits, 10)
        
    def test_invalid_args(self):
        args = {(   -1,   ): ValueError,
                (  256,   ): ValueError,
                (2**16, 16): ValueError}
        self._test_args(Uint, args)

    def test_to_bytes(self):
        # 500 = 00000001 11110100
        # Uints with sizes that are not multiples of 8 are padded 
        # with zeroes.
        args = {(  5,   ): bytes([5]),
                (500, 16): bytes([1, 244]),
                (500,  9): bytes([1, 244])}        
        def to_bytes(*args):
            return Uint(*args).to_bytes()        
        self._test_args(to_bytes, args)

    def test_from_bytes(self):
        args = {(bytes([5]     ),): Uint(  5,  8),
                (bytes([1, 244]),): Uint(500, 16)}        
        self._test_args(Uint.from_bytes, args)
        
    def test_to_builtin(self):
        i = Uint(5).to_builtin()
        self.assertEqual(i, 5)
        self.assertIsInstance(i, int)
        self.assertNotIsInstance(i, Uint)
        

class TestSint(GenericTests):
    
    def test_init(self):
        args = {(  -128,   ):   -128,
                (   127,   ):    127,
                (-2**15, 16): -2**15,
                (  '-5',   ):     -5,
                (  -1.2,   ):     -1}        
        self._test_args(Sint, args)
        
    def test_type(self):
        self.assertIsInstance(Sint(-1), Sint)
        self.assertIsInstance(Sint.from_bytes(bytes([255])), Sint)
        
    def test_inheritance(self):
        x = Sint(-5)
        self.assertEqual(x, -5)
        self.assertEqual(x + 1, -4)
        self.assertEqual(x**2, 25)
                
    def test_bits(self):
        self.assertEqual(Sint(-5).bits, 8)
        self.assertEqual(Sint(-100, 10).bits, 10)
        
    def test_invalid_args(self):
        args = {( -129,   ): ValueError,
                (  128,   ): ValueError,
                (2**15, 16): ValueError}
        self._test_args(Sint, args)
        
    def test_to_bytes(self):
        # -5 = 11111011
        # -500 = 11111110 00001100
        args = {(  -5,   ): bytes([251]),
                (-500, 16): bytes([254, 12]),
                (-500, 10): bytes([254, 12])}        
        def to_bytes(*args):
            return Sint(*args).to_bytes()        
        self._test_args(to_bytes, args)
        
    def test_from_bytes(self):
        args = {(bytes([251]    ),): Sint(  -5,  8),
                (bytes([254, 12]),): Sint(-500, 16),
                (bytes([2, 12]  ),): Sint( 524, 16)}        
        self._test_args(Sint.from_bytes, args)
        
    def test_to_builtin(self):
        i = Sint(-5).to_builtin()
        self.assertEqual(i, -5)
        self.assertIsInstance(i, int)
        self.assertNotIsInstance(i, Sint)
        
        
class TestFloat(GenericTests):
    
    def test_init(self):
        args = {( 123.456,   ): 123.456,
                (-123.456, 32): -123.456,
                (   1.2E3,   ): 1.2E3,
                ('123.456',  ): 123.456,
                ('1E5',    32): 1E5,
                ('inf',      ): float('inf')}        
        self._test_args(Float, args)
        
    def test_type(self):
        self.assertIsInstance(Float(0.0), Float)
        self.assertIsInstance(Float.from_bytes(bytes([0,0,0,0])), Float)
        
    def test_inheritance(self):
        x = Float(123.456)
        self.assertAlmostEqual(x,     123.456,      delta=1E-5)
        self.assertAlmostEqual(x + 1, 124.456,      delta=1E-5)
        self.assertAlmostEqual(x**2,  15241.383936, delta=1E-2)
        
    def test_bits(self):
        self.assertEqual(Float(1.0).bits, 32)
        self.assertEqual(Float(1E30).bits, 32)
        
    def test_invalid_args(self):
        args = {( 1E50,   ): ValueError,
                (-1E50,   ): ValueError,
                (  0.0, 16): ValueError}
        self._test_args(Float, args)
        
    def test_to_bytes(self):
        # 123.456 = 01000010 11110110 11101001 01111001
        # = [66, 246, 233, 121]
        args = {(123.456,): bytes([66, 246, 233, 121])}        
        def to_bytes(*args):
            return Float(*args).to_bytes()        
        self._test_args(to_bytes, args)
        
    def test_from_bytes(self):
        args = {(bytes([66, 246, 233, 121]),): Float(123.456)}        
        self._test_args(Float.from_bytes, args)
        
    def test_to_builtin(self):
        x = Float(123.456).to_builtin()
        self.assertAlmostEqual(x, 123.456, 5)
        self.assertIsInstance(x, float)
        self.assertNotIsInstance(x, Float)
        
        
class TestBin(GenericTests):
    
    def test_init(self):
        args = {(    '10111101',   ):         '10111101',
                ('111100001111', 16): '0000111100001111',
                (          101 ,   ):              '101',
                (          101 ,  5):            '00101'}        
        self._test_args(Bin, args)
        
    def test_type(self):
        self.assertIsInstance(Bin('1'), Bin)
        self.assertIsInstance(Bin.from_bytes(bytes([1])), Bin)
        
    def test_inheritance(self):
        x = Bin('10111101')
        self.assertEqual(x[0:2], '10')
        self.assertEqual(x + 'X', '10111101X')
        self.assertTrue('1' in x)
        
    def test_addition(self):
        s1 = Bin('000')
        s2 = Bin('111')
        self.assertEqual(s1 + s2, '000111')
        self.assertIsInstance(s1 + s2, Bin)
        s1 += s2
        self.assertEqual(s1, '000111')
        self.assertIsInstance(s1, Bin)
        
    def test_indexing(self):
        s = Bin('1001')
        self.assertEqual(s[0], '1')
        self.assertIsInstance(s[0], Bin)
        self.assertEqual(s[1:3], '00')
        self.assertIsInstance(s[1:3], Bin)
        
    def test_bits(self):
        self.assertEqual(Bin(8*'1').bits, 8)
        self.assertEqual(Bin(16*'1').bits, 16)
        self.assertEqual(Bin('1', 5).bits, 5)
        
    def test_invalid_args(self):
        args = {('102',  ): ValueError,
                (9*'1', 8): ValueError}
        self._test_args(Bin, args)
        
    def test_to_bytes(self):
        # 123.456 = 01000010 11110110 11101001 01111001
        # = [66, 246, 233, 121]
        args = {('10111101' + '00111100', 16): bytes([189, 60]),
                ('100111100'           ,   9): bytes([1, 60])}        
        def to_bytes(*args):
            return Bin(*args).to_bytes()        
        self._test_args(to_bytes, args)
        
    def test_from_bytes(self):
        args = {(bytes([189, 60]),): Bin('10111101' + '00111100', 16),
                (bytes([1, 60]  ),): Bin('00000001' + '00111100', 16)}        
        self._test_args(Bin.from_bytes, args)
        
    def test_to_builtin(self):
        s = Bin('10111101').to_builtin()
        self.assertAlmostEqual(s, '10111101')
        self.assertIsInstance(s, str)
        self.assertNotIsInstance(s, Bin)


if __name__ == '__main__':
    unittest.main()