"""Unit tests for the datatypes module."""

import math
import unittest
from hypothesis import given, assume, strategies as st

from turboctl.telegram.datatypes import maxuint, maxsint, minsint, Data, Uint, Sint, Float, Bin

# Testing with large numbers has no benefit and slows the tests
# down considerably.
MAX_BITS = 64
MAX_UINT = maxuint(MAX_BITS)
MAX_SINT = maxsint(MAX_BITS)
MIN_SINT = minsint(MAX_BITS)


### Hypothesis strategies ###


@st.composite
def values_and_bits(draw, class_, min_bits=0, max_bits=MAX_BITS):
    """Generate tuples of valid arguments for initializing Data
    objects.
    """
    bits = draw(st.integers(min_value=min_bits, max_value=max_bits))
    
    if class_ == Uint:
        value = draw(st.integers(min_value=0, max_value=maxuint(bits)))
    
    elif class_ == Sint:
        value = draw(st.integers(min_value=minsint(bits),
                                 max_value=maxsint(bits)))
    elif class_ == Float:
        bits = 32
        value = draw(st.floats(width=bits))
    
    elif class_ == Bin:
        value = draw(st.from_regex(f'\A[01]{{{bits}}}\Z'))
        
    return value, bits


@st.composite
def data_types(draw, classes=(Uint, Sint, Float, Bin)):
    """Generate Data subclasses."""
    maxi = len(classes) - 1
    i = draw(st.integers(min_value=0, max_value=maxi))
    return classes[i]


@st.composite
def data_objects(draw, classes=(Uint, Sint, Float, Bin), **kwargs):
    """Generate instances of Data subclasses."""
    class_ = draw(data_types(classes))
    args = draw(values_and_bits(class_, **kwargs))
    return class_(*args)


@st.composite
def data_objects_and_slices(draw, **kwargs):
    """Generate references to all four Data subclasses."""
    obj = draw(data_objects(**kwargs))
    slice_ = draw(st.slices(obj.bits))
    return obj, slice_


class TestAttributes(unittest.TestCase):
    
    # value
    
    @given(data_objects())
    def test_value_is_readable_but_not_writable(self, obj):
        value = obj.value
        with self.assertRaises(AttributeError):
            obj.value = value
            
    @given(data_objects([Uint]))
    def test_uint_value_is_builtin_int(self, obj):
        self.assertIsInstance(obj.value, int)
        
    @given(data_objects([Sint]))
    def test_sint_value_is_builtin_int(self, obj):
        self.assertIsInstance(obj.value, int)
        
    @given(data_objects([Float]))
    def test_float_value_is_builtin_float(self, obj):
        self.assertIsInstance(obj.value, float)
        
    @given(data_objects([Bin]))
    def test_bin_value_is_binary_str(self, obj):
        self.assertIsInstance(obj.value, str)
        self.assertEqual(obj.value.strip('01'), '')
           
    # bits
            
    @given(data_objects())
    def test_bits_is_readable_but_not_writable(self, obj):
        bits = obj.value
        with self.assertRaises(AttributeError):
            obj.bits = bits
          
    @given(data_objects([Uint]))
    def test_uint_has_correct_bits(self, obj):
        value = obj.value
        bits = obj.bits
        self.assertTrue(0 <= value <= maxuint(bits))
        
    @given(data_objects([Sint]))
    def test_sint_has_correct_bits(self, obj):
        value = obj.value
        bits = obj.bits
        self.assertTrue(minsint(bits) <= value <= maxsint(bits))
        
    @given(data_objects([Float]))
    def test_float_has_32_bits(self, obj):
        self.assertEqual(obj.bits, 32)
        
    @given(data_objects([Bin]))
    def test_bin_has_correct_bits(self, obj):
        value = obj.value
        bits = obj.bits
        self.assertEqual(len(value), bits)
            
    # n_bytes

    @given(data_objects())
    def test_n_bytes_is_readable_but_not_writable(self, obj):
        n_bytes = obj.n_bytes
        with self.assertRaises(AttributeError):
            obj.n_bytes = n_bytes
            
    @given(data_objects())
    def test_padding_is_between_0_and_7_bits(self, obj):
        bits = obj.bits
        n_bytes = obj.n_bytes
        padding = 8*n_bytes - bits
        self.assertTrue(0 <= padding <= 7)
            

class TestMagicMethods(unittest.TestCase):
    
    # __bytes__
            
    @given(data_objects())
    def test_bytes_returns_a_bytes_object(self, obj):
        self.assertIsInstance(bytes(obj), bytes)
    
    @given(data_objects())
    def test_bytes_objects_have_a_len_of_n_bytes(self, obj):
        bytes_ = bytes(obj)
        self.assertEqual(len(bytes_), obj.n_bytes)
        
    @given(data_objects(),
           data_types(classes=(Uint, Sint, Bin)))
    def test_nested_bytes_when_class_is_not_float(self, obj, class_):
        bytes1 = bytes(obj)
        bytes2 = bytes(class_(bytes(obj)))
        self.assertEqual(bytes1, bytes2)
        
    @given(data_objects(min_bits=32, max_bits=32))
    def test_nested_bytes_when_class_is_float(self, obj):
        float_obj = Float(bytes(obj))
        # NaN has several different binary representations.
        assume(not math.isnan(float_obj.value))
        bytes1 = bytes(obj)
        bytes2 = bytes(float_obj)
        self.assertEqual(bytes1, bytes2)
        
    # __add__
        
    @given(data_objects(), data_objects())
    def test_bits_of_sum_is_sum_of_bits(self, obj1, obj2):
        sum_ = obj1 + obj2
        sum_of_bits = obj1.bits + obj2.bits
        self.assertEqual(sum_.bits, sum_of_bits)
        
    @given(data_objects(), data_objects())
    def test_add_concatenates_binary_representations(self, obj1, obj2):
        sum_ = obj1 + obj2
        sum_of_bins = Bin(obj1) + Bin(obj2)
        self.assertEqual(Bin(sum_), sum_of_bins)
                
    # __eq__
        
    @given(data_objects())
    def test_equality_is_reflexive(self, obj):
        self.assertEqual(obj, obj)
        
    @given(data_objects())
    def test_copy_is_equal_to_original(self, obj):        
        class_ = type(obj)
        other = class_(obj.value, obj.bits)
        self.assertEqual(obj, other)
        
    # __eq__ should work also against non-Data objects,
    # which is why this is tested with a few integers.
    @given(data_objects(), 
           st.one_of(data_objects(), 
                     st.integers(min_value=-10, max_value=10)))
    def test_different_type_value_or_bits_breaks_equality(self, obj1, obj2):
        try:
            both_values_nan = math.isnan(obj1.value) and math.isnan(obj2.value)
        except (TypeError, AttributeError):
            both_values_nan = False
        
        assume(
            type(obj1) != type(obj2)
            or ((obj1.value != obj2.value) and not both_values_nan)
            or obj1.bits != obj2.bits
        )
        self.assertNotEqual(obj1, obj2)
        
    # __repr__

    @given(data_objects())
    def test_eval_repr_returns_copy_except_for_inf_and_nan(self, obj):
        names = {**globals(), 'inf': float('inf'), 'nan': float('nan')}
        copy = eval(repr(obj), names)
        self.assertEqual(obj, copy)

    # __getitem__
        
    @given(data_objects([Bin]), st.slices(MAX_BITS))
    def test_getitem_slices_value_for_bin_objects(self,  obj, slice_):
        class_ = type(obj)
        self.assertEqual(obj[slice_], class_(obj.value[slice_]))
        
    @given(data_objects(), st.slices(MAX_BITS))
    def test_getitem_slices_binary_value(self, obj, slice_):
        self.assertEqual(Bin(obj[slice_]), Bin(obj)[slice_])
        

class TestInit(unittest.TestCase):
    
    @given(data_objects(), data_types())
    def test_type_conversions_preserve_bits_and_bytes(self, obj, class_):
        # Non-32 bit objects can't be cast to Float.
        if class_ == Float:
            assume(obj.bits==32)
        
        other = class_(obj)
        self.assertEqual(bytes(obj), bytes(other))
        self.assertEqual(obj.bits, other.bits)
    
    @given(values_and_bits(Uint))
    def test_init_from_int_sets_attributes_correctly(self, i_and_bits):
        i, bits = i_and_bits
        uint = Uint(i, bits)
        self.assertEqual(uint.value, i)
        self.assertEqual(uint.bits, bits)
        

        
        
        
        
        
        
        
        
        
        
        
        

# class TestUint(GenericTests):
    
#     def test_init(self):
#         args = {(      1,   ):       1,
#                 (    255,   ):     255,
#                 (2**16-1, 16): 2**16-1,
#                 (    '5',   ):       5,
#                 (    1.2,   ):       1}        
#         self._test_args(Uint, args)
        
#     def test_type(self):
#         self.assertIsInstance(Uint(1), Uint)
#         self.assertIsInstance(Uint.from_bytes(bytes([1])), Uint)
    
#     def test_inheritance(self):
#         x = Uint(5)
#         self.assertEqual(x, 5)
#         self.assertEqual(x + 1, 6)
#         self.assertEqual(x**2, 25)

#     def test_bits(self):
#         self.assertEqual(Uint(5).bits, 8)
#         self.assertEqual(Uint(100, 10).bits, 10)
        
#     def test_invalid_args(self):
#         args = {(   -1,   ): ValueError,
#                 (  256,   ): ValueError,
#                 (2**16, 16): ValueError}
#         self._test_args(Uint, args)

#     def test_to_bytes(self):
#         # 500 = 00000001 11110100
#         # Uints with sizes that are not multiples of 8 are padded 
#         # with zeroes.
#         args = {(  5,   ): bytes([5]),
#                 (500, 16): bytes([1, 244]),
#                 (500,  9): bytes([1, 244])}        
#         def to_bytes(*args):
#             return Uint(*args).to_bytes()        
#         self._test_args(to_bytes, args)

#     def test_from_bytes(self):
#         args = {(bytes([5]     ),): Uint(  5,  8),
#                 (bytes([1, 244]),): Uint(500, 16)}        
#         self._test_args(Uint.from_bytes, args)
        
#     def test_to_builtin(self):
#         i = Uint(5).to_builtin()
#         self.assertEqual(i, 5)
#         self.assertIsInstance(i, int)
#         self.assertNotIsInstance(i, Uint)



# class TestTurboNum(GenericTests):
    
#     def test_init(self):
#         args = {(123      ,): Uint(123),
#                 (-123     ,): Sint(-123),
#                 (123.456  ,): Float(123.456),
#                 ('1111011',): Bin('1111011')}
#         def to_type(*args):
#             return TurboNum(*args)     
#         self._test_args(to_type, args)
        
#     def test_invalid_args(self):
#         args = {(256   ,  ): ValueError,
#                 (-129  ,  ): ValueError,
#                 (1E40  ,  ): ValueError,
#                 ('1111', 3): ValueError}
#         def to_type(*args):
#             return TurboNum(*args)     
#         self._test_args(to_type, args)
        
#     def test_to(self):
#         self.assertEqual(Uint(123).to(Bin), Bin('1111011', 8))
#         self.assertEqual(Float(123.456).to(Uint), Uint(1123477881, 32))

        

# class TestSint(GenericTests):
    
#     def test_init(self):
#         args = {(  -128,   ):   -128,
#                 (   127,   ):    127,
#                 (-2**15, 16): -2**15,
#                 (  '-5',   ):     -5,
#                 (  -1.2,   ):     -1}        
#         self._test_args(Sint, args)
        
#     def test_type(self):
#         self.assertIsInstance(Sint(-1), Sint)
#         self.assertIsInstance(Sint.from_bytes(bytes([255])), Sint)
        
#     def test_inheritance(self):
#         x = Sint(-5)
#         self.assertEqual(x, -5)
#         self.assertEqual(x + 1, -4)
#         self.assertEqual(x**2, 25)
                
#     def test_bits(self):
#         self.assertEqual(Sint(-5).bits, 8)
#         self.assertEqual(Sint(-100, 10).bits, 10)
        
#     def test_invalid_args(self):
#         args = {( -129,   ): ValueError,
#                 (  128,   ): ValueError,
#                 (2**15, 16): ValueError}
#         self._test_args(Sint, args)
        
#     def test_to_bytes(self):
#         # -5 = 11111011
#         # -500 = 11111110 00001100
#         args = {(  -5,   ): bytes([251]),
#                 (-500, 16): bytes([254, 12]),
#                 (-500, 10): bytes([254, 12])}        
#         def to_bytes(*args):
#             return Sint(*args).to_bytes()        
#         self._test_args(to_bytes, args)
        
#     def test_from_bytes(self):
#         args = {(bytes([251]    ),): Sint(  -5,  8),
#                 (bytes([254, 12]),): Sint(-500, 16),
#                 (bytes([2, 12]  ),): Sint( 524, 16)}        
#         self._test_args(Sint.from_bytes, args)
        
#     def test_to_builtin(self):
#         i = Sint(-5).to_builtin()
#         self.assertEqual(i, -5)
#         self.assertIsInstance(i, int)
#         self.assertNotIsInstance(i, Sint)
        
        
# class TestFloat(GenericTests):
    
#     def test_init(self):
#         args = {( 123.456,   ): 123.456,
#                 (-123.456, 32): -123.456,
#                 (   1.2E3,   ): 1.2E3,
#                 ('123.456',  ): 123.456,
#                 ('1E5',    32): 1E5,
#                 ('inf',      ): float('inf')}        
#         self._test_args(Float, args)
        
#     def test_type(self):
#         self.assertIsInstance(Float(0.0), Float)
#         self.assertIsInstance(Float.from_bytes(bytes([0,0,0,0])), Float)
        
#     def test_inheritance(self):
#         x = Float(123.456)
#         self.assertAlmostEqual(x,     123.456,      delta=1E-5)
#         self.assertAlmostEqual(x + 1, 124.456,      delta=1E-5)
#         self.assertAlmostEqual(x**2,  15241.383936, delta=1E-2)
        
#     def test_bits(self):
#         self.assertEqual(Float(1.0).bits, 32)
#         self.assertEqual(Float(1E30).bits, 32)
        
#     def test_invalid_args(self):
#         args = {( 1E50,   ): ValueError,
#                 (-1E50,   ): ValueError,
#                 (  0.0, 16): ValueError}
#         self._test_args(Float, args)
        
#     def test_to_bytes(self):
#         # 123.456 = 01000010 11110110 11101001 01111001
#         # = [66, 246, 233, 121]
#         args = {(123.456,): bytes([66, 246, 233, 121])}        
#         def to_bytes(*args):
#             return Float(*args).to_bytes()        
#         self._test_args(to_bytes, args)
        
#     def test_from_bytes(self):
#         args = {(bytes([66, 246, 233, 121]),): Float(123.456)}        
#         self._test_args(Float.from_bytes, args)
        
#     def test_to_builtin(self):
#         x = Float(123.456).to_builtin()
#         self.assertAlmostEqual(x, 123.456, 5)
#         self.assertIsInstance(x, float)
#         self.assertNotIsInstance(x, Float)
        
        
# class TestBin(GenericTests):
    
#     def test_init(self):
#         args = {(    '10111101',   ):         '10111101',
#                 ('111100001111', 16): '0000111100001111',
#                 (          101 ,   ):              '101',
#                 (          101 ,  5):            '00101'}        
#         self._test_args(Bin, args)
        
#     def test_type(self):
#         self.assertIsInstance(Bin('1'), Bin)
#         self.assertIsInstance(Bin.from_bytes(bytes([1])), Bin)
        
#     def test_inheritance(self):
#         x = Bin('10111101')
#         self.assertEqual(x[0:2], '10')
#         self.assertEqual(x + 'X', '10111101X')
#         self.assertTrue('1' in x)
        
#     def test_addition(self):
#         s1 = Bin('000')
#         s2 = Bin('111')
#         self.assertEqual(s1 + s2, '000111')
#         self.assertIsInstance(s1 + s2, Bin)
#         s1 += s2
#         self.assertEqual(s1, '000111')
#         self.assertIsInstance(s1, Bin)
        
#     def test_indexing(self):
#         s = Bin('1001')
#         self.assertEqual(s[0], '1')
#         self.assertIsInstance(s[0], Bin)
#         self.assertEqual(s[1:3], '00')
#         self.assertIsInstance(s[1:3], Bin)
        
#     def test_bits(self):
#         self.assertEqual(Bin(8*'1').bits, 8)
#         self.assertEqual(Bin(16*'1').bits, 16)
#         self.assertEqual(Bin('1', 5).bits, 5)
        
#     def test_invalid_args(self):
#         args = {('102',  ): ValueError,
#                 (9*'1', 8): ValueError}
#         self._test_args(Bin, args)
        
#     def test_to_bytes(self):
#         # 123.456 = 01000010 11110110 11101001 01111001
#         # = [66, 246, 233, 121]
#         args = {('10111101' + '00111100', 16): bytes([189, 60]),
#                 ('100111100'           ,   9): bytes([1, 60])}        
#         def to_bytes(*args):
#             return Bin(*args).to_bytes()        
#         self._test_args(to_bytes, args)
        
#     def test_from_bytes(self):
#         args = {(bytes([189, 60]),): Bin('10111101' + '00111100', 16),
#                 (bytes([1, 60]  ),): Bin('00000001' + '00111100', 16)}        
#         self._test_args(Bin.from_bytes, args)
        
#     def test_to_builtin(self):
#         s = Bin('10111101').to_builtin()
#         self.assertAlmostEqual(s, '10111101')
#         self.assertIsInstance(s, str)
#         self.assertNotIsInstance(s, Bin)



if __name__ == '__main__':
    unittest.main()
