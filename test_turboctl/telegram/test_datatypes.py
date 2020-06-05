"""Unit tests for the datatypes module.

TODO: the following tests should be added:
    - make sure init with an invalid value produce a ValueError
    - make sure init with an invalid bits does the same
    - make sure init works correctly if bits is not specified
"""

import math
import unittest

from hypothesis import given, assume, strategies as st

from turboctl.telegram.datatypes import (
    maxuint, maxsint, minsint, Uint, Sint, Float, Bin)

# Testing with large numbers provides no benefits and slows the tests
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
def iterables_and_bits(draw, min_bits=0, max_bits=MAX_BITS):
    """Generate tuples of valid arguments for initializing Bin
    objects from iterables.
    """
    bits = draw(st.integers(min_value=min_bits, max_value=max_bits))
    iterable = draw(st.iterables(st.integers(min_value=0, max_value=bits)))
    return iterable, bits


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
    def test_uint_from_int_sets_attributes_correctly(self, i_and_bits):
        i, bits = i_and_bits
        uint = Uint(i, bits)
        self.assertEqual(uint.value, i)
        self.assertEqual(uint.bits, bits)
        
    @given(values_and_bits(Sint))
    def test_sint_from_int_sets_attributes_correctly(self, i_and_bits):
        i, bits = i_and_bits
        sint = Sint(i, bits)
        self.assertEqual(sint.value, i)
        self.assertEqual(sint.bits, bits)
        
    @given(values_and_bits(Float))
    def test_float_from_float_sets_attributes_correctly(self, x_and_bits):
        x, bits = x_and_bits
        float_ = Float(x, bits)
        
        if math.isnan(x):
            self.assertTrue(math.isnan(float_.value))
        else:
            self.assertEqual(float_.value, x)
        
        self.assertEqual(float_.bits, bits)
        
    @given(values_and_bits(Bin))
    def test_bin_from_str_sets_attributes_correctly(self, str_and_bits):
        s, bits = str_and_bits
        bin_ = Bin(s, bits)
        
        self.assertEqual(bin_.value, s)        
        self.assertEqual(bin_.bits, bits)
        
    @given(iterables_and_bits())
    def test_bin_from_iterable_sets_attributes_correctly(self, it_and_bits):
        it, bits = it_and_bits
        # Some iterables (i.e. generators) can only be iterated once, 
        # so we need to save the contents to a list.
        list_ = list(it)
        bin_ = Bin(list_, bits)
        
        for i, c in enumerate(bin_.value):
            self.assertEqual(c, '1' if i in list_ else '0')
  
        self.assertEqual(bin_.bits, bits)
        
        
if __name__ == '__main__':
    unittest.main()
