"""This module defines classes representing different data types used
in telegrams.

..
    Aliases for Sphinx.

.. |value| replace:: :attr:`value <Data.value>`
.. |bits| replace:: :attr:`bits <Data.bits>`
.. |n_bytes| replace:: :attr:`n_bytes <Data.n_bytes>`
.. |BYTESIZE| replace:: :const:`BYTESIZE`
"""
import math
import re
import struct
from typing import Optional

from turboctl.singledispatchmethod import singledispatchmethod 


__all__ = ['BYTESIZE', 'maxuint', 'maxsint', 'minsint',
           'Data', 'Uint', 'Sint', 'Float', 'Bin']
# These variables are "public" and are shown in the docs.
# The others are "private" (equivalent to prefixing them with '_').


BYTESIZE = 8
"""The number of bits in a byte."""


def maxuint(bits):
    """Return the largest unsigned integer that can be expressed with
    *bits* bits.
    
    If *bits* is ``0``, ``0`` is returned.
    
    Args:
        bits:
            A non-negative :class:`int`.
    """
    return 2**bits - 1
    

def maxsint(bits):
    """Return the largest (i.e. most positive) signed integer that can
    be expressed with *bits* bits.
    
    If *bits* is ``0``, ``0`` is returned.
    
    Args:
        bits:
            A non-negative :class:`int`.
    """
    if bits == 0:
        return 0
    
    return 2**(bits - 1) - 1


def minsint(bits):
    """Return the smallest (i.e. most negative) signed integer that can
    be expressed with *bits* bits.
    
    If *bits* is ``0``, ``0`` is returned.
    
    Args:
        bits:
            A non-negative :class:`int`.
    """
    if bits == 0:
        return 0
    
    return -2**(bits - 1)


class Data():
    """A superclass for all telegram data types.
    
    This class is not meant to be initialized, since it lacks an
    ``__init__`` method.
    """
    
    @property
    def value(self):
        """The value represented by this data object.
        This is a read-only property.
        """
        return self._value
    
    @property   
    def bits(self) -> int:
        """How many bits of data this object represents.
        This is a read-only property.
        """
        return self._bits 
        
    @property
    def n_bytes(self) -> int:
        """How many bytes are needed to store the data in the object;
        equal to |bits| divided by |BYTESIZE| and rounded up.
        """
        return math.ceil(self.bits / BYTESIZE)

    def __add__(self, other):
        """Return *self* + *other*.
        
        Appends the binary data in *other* to the end of *self* and
        returns an object of the same class as *self* with the
        combined binary data.
        
        Example: ``Bin('010') + Bin('001') = Bin('010001')``
        """
        class_ = type(self)
        string1 = Bin(self).value
        string2 = Bin(other).value
        return class_(Bin(string1 + string2))

    def __eq__(self, other):
        """Return ``self == other``.
        
        Returns ``True``, if *self* and *other* have the same type,
        |value| and |bits|, otherwise ``False``.
        Two objects with a value of ``NaN`` are equal, if their types
        and bits match.
        """
        if type(self) != type(other):
            return False
        
        if self.bits != other.bits:
            return False
        
        equal_values = self.value == other.value

        try:
            both_nans = math.isnan(self.value) and math.isnan(other.value)
        except TypeError:
            both_nans = False
        
        return equal_values or both_nans
        
    def __repr__(self):
        """Return ``repr(self)``.
        
        The returned string uses the format
        ``'ClassName(<value>, bits=<bits>).'``
        """
        class_ = type(self).__name__
        value = repr(self.value)
        bits = self.bits
        return f'{class_}({value}, bits={bits})'
                 
    def __getitem__(self, key):
        """Return ``self[key]``.
        
        This method uses *key* to get an index or a slice
        of the binary data in *self*,
        and returns an object of the same class as *self* containing
        the binary data in the index or slice.
        
        Example:
            >>> Bin('010001')[0:3]
            Bin('010', bits=3)
        """
        class_ = type(self)
        string = Bin(self).value[key]
        return class_(Bin(string))
    
    
class Uint(Data):
    """A data type for unsigned integers."""
            
    @singledispatchmethod
    def __init__(self, value, bits: int=BYTESIZE):
        """Initialize a new :class:`Uint`.
        
        This method may be called with any of the following signatures:
            
        ::
            
            Sint(value: int, bits: int=8)
            Sint(value: Data)
            Sint(value: bytes)
            
        If *value* is an :class:`int`, |value| and |bits| will be set
        to the values given as arguments.
        
        If *value* is an instance of a subclass of :class:`Data`,
        the initialized object will represent exactly the same binary
        data as *value* and have the same |bits|.
        
        If *value* is a :class:`bytes` object, the initialized
        object will represent the same binary data as *value*.  
        Because :class:`bytes` objects represent sequences of full
        bytes, |bits| will be |BYTESIZE| multiplied by ``len(value)``.
        
        Raises:
            TypeError or ValueError:
                If *value* or *bits* have invalid types or values.
            TypeError:
                If the *bits* argument is supplied when *value* is
                not an :class:`int`. 
        """
        raise TypeError(f'invalid type for *value*: {type(value)}')
        
    @__init__.register
    def _from_int(self, value: int, bits: int=BYTESIZE):
        check_uint(value, bits)
        self._value = value
        self._bits = bits        

    @__init__.register
    def _from_data(self, value: Data):
        bytes_ = bytes(value)
        i = int.from_bytes(bytes_, 'big')
        bits = value.bits
        self._from_int(i, bits)

    @__init__.register
    def _from_bytes(self, value: bytes):
        i = int.from_bytes(value, 'big')
        bits = len(value) * BYTESIZE
        self._from_int(i, bits)
        
    def __bytes__(self):
        """Return ``bytes(self)``.
        
        Returns the binary data represented by this object as a
        :class:`bytes` object with a length of |n_bytes|. 
        """
        return self.value.to_bytes(self.n_bytes, 'big')
                            
    
class Sint(Data):
    """A data type for signed integers formed with the
    `two's complement
    <https://en.wikipedia.org/wiki/Two%27s_complement>`_ method.
    """

    @singledispatchmethod
    def __init__(self, value, bits: int=BYTESIZE):
        """Initialize a new :class:`Sint`.
        
        This method works like :meth:`Uint.__init__`,
        except that the range of valid :class:`int` values it
        accepts is different.
        """
        raise TypeError(f'invalid type for *value*: {type(value)}')
        
    @__init__.register
    def _from_int(self, value: int, bits: int=BYTESIZE):
        check_sint(value, bits)
        self._value = value
        self._bits = bits        

    @__init__.register
    def _from_data(self, value: Data):
        bytes_ = bytes(value)
        # int.from_bytes(bytes_, 'big', signed=True)
        # only works if bits == BYTESIZE.
        i = int.from_bytes(bytes_, 'big')
        bits = value.bits
        
        # Convert i to a signed integer.
        if i > maxsint(bits):
            i -= 2**bits
        
        self._from_int(i, bits)

    @__init__.register
    def _from_bytes(self, value: bytes):
        i = int.from_bytes(value, 'big', signed=True)
        bits = len(value) * BYTESIZE
        self._from_int(i, bits)
            
    def __bytes__(self):
        """Return ``bytes(self)``.
        
        See :meth:`Uint.__bytes__` for details.
        """
        # Convert self.value to an unsigned integer.
        i = self.value
        if i < 0:
            i += 2**self.bits

        # self.value.to_bytes(self.n_bytes, 'big', signed=True)
        # only works if self.bits == BYTESIZE.
        return i.to_bytes(self.n_bytes, 'big')


class Float(Data):
    """A data type for 
    `IEEE 754 single-precision
    <https://en.wikipedia.org/wiki/
    Single-precision_floating-point_format
    #IEEE_754_single-precision_binary_floating-point_format:
    _binary32>`_  floating point numbers.
    """
    
    @singledispatchmethod
    def __init__(self, value, bits=4*BYTESIZE):
        """Initialize a new :class:`Float`.
        
        This method may be called with any of the following signatures:
            
        ::
            
            Float(value: float, bits: int=32)
            Float(value: Data)
            Float(value: bytes)
            
        The method works like :meth:`Uint.__init__`,
        with the following exceptions:
        
        - If *value* is given as a number, it should be a 
          :class:`float` instead of an :class:`int`.
        - *bits* must always be ``32``; it exists as an argument
          only to give all ``__init__`` methods of :class:`Data`
          subclasses a similar signature.
          Likewise, if *value* is a :class:`Data` or a
          :class:`bytes` object, it must contain exactly 32
          bits of data.
        
        Raises:
            ValueError:
                If *bits* is not ``32``, or *value* can't be expressed in
                32 bits of data.
        """
        raise TypeError(f'invalid type for *value*: {type(value)}')
        
    @__init__.register
    def _from_float(self, value: float, bits: int=4*BYTESIZE):
        check_float(value, bits)
        # Values that are too close to 0 to be expressed as a float are
        # rounded to 0.
        self._value = struct.unpack('>f', struct.pack('>f', value))[0]
        self._bits = bits

    @__init__.register
    def _from_data(self, value: Data):
        bytes_ = bytes(value)
        x = struct.unpack('>f', bytes_)[0]
        bits = value.bits
        self._from_float(x, bits)

    @__init__.register
    def _from_bytes(self, value: bytes):
        x = struct.unpack('>f', value)[0]
        bits = len(value) * BYTESIZE
        self._from_float(x, bits)
            
    def __bytes__(self):
        """Return ``bytes(self)``.
        
        See :meth:`Uint.__bytes__` for details.
        """
        return struct.pack('>f', self.value)
        
    def __add__(self, other):
        """Return *self* + *other*.
        
        This method works like :meth:`Data.__add__`, except that the
        returned object is a :class:`Bin` instead of a :class:`Float`,
        because :class:`Float` objects cannot have more than 32 bits.
        """
        string1 = Bin(self).value
        string2 = Bin(other).value
        return Bin(string1 + string2)
    
    
    def __getitem__(self, key):
        """Return ``self[key]``.
        
        This method works like :meth:`Data.__getitem__`,
        except that the returned object is a :class:`Bin` instead of a
        :class:`Float`,
        because :class:`Float` objects cannot have less than 32 bits.
        """
        return Bin(self)[key]


class Bin(Data):
    
    @singledispatchmethod
    def __init__(self, value, bits: Optional[int]=None):
        """Initialize a new :class:`Bin`.
        
        This method may be called with any of the following signatures:
            
        ::
            
            Bin(value: str, bits: Optional[int]=None)
            Bin(value: Data)
            Bin(value: bytes)
            
        The method works like :meth:`Uint.__init__`, with the exception that 
        if *value* is specified directly, it must be a :class:`str` instead 
        of an :class:`int`.
        In this case, *value* should be composed solely of
        the characters ``'1'`` and ``'0'``, or be an empty string. 
        If *bits* is ``None``, it will be set to the length of
        *value*. Otherwise, *value* is padded with zeroes to a length
        of *bits*.
        
        Giving *bits* a value that is smaller than the length of
        *value* will raise a :class:`ValueError`.
        """
        raise TypeError(f'invalid type for *value*: {type(value)}')
        
    @__init__.register
    def _from_str(self, value: str, bits: Optional[int]=None):
        check_bin(value, bits)
        self._value = value
        if bits == None:
            bits = len(self.value)
        self._bits = bits
                
    @__init__.register
    def _from_data(self, value: Data):
        bytes_ = bytes(value)
        i = int.from_bytes(bytes_, 'big')
        bits = value.bits
        s = bin_str(i, bits)
        self._from_str(s, bits)

    @__init__.register
    def _from_bytes(self, value: bytes):
        i = int.from_bytes(value, 'big')
        bits = len(value) * BYTESIZE
        s = bin_str(i, bits)
        self._from_str(s, bits)
                    
    def __bytes__(self):
        """Return ``bytes(self)``.
        
        See :meth:`Uint.__bytes__` for details.
        """
        if not self.value:
            return b''
        
        return int(self.value, 2).to_bytes(self.n_bytes, 'big')


def check_uint(value, bits=None):
    """Make sure *value* is a valid *bits* bit unsigned integer.
    
    If *bits* is None, *value* can have any number of bits.
    
    Raises:
        TypeError or ValueError:
            If *value* or *bits* have invalid values or types.
    """
    if not isinstance(value, int):
        raise TypeError(f'value is not an int: {value}')
        
    if value < 0:
        raise ValueError(f'value is negative: {value}')
    
    if bits is not None:
        check_uint(bits)
        
        if value > maxuint(bits):
            raise ValueError(f'value is too large: {value}')
    
    
def check_sint(value, bits=None):
    """Like 'check_uint', but for signed integers."""
    if not isinstance(value, int):
        raise TypeError(f'value is not an int: {value}')
        
    if bits is not None:
        check_uint(bits)
        
        if value < minsint(bits) or value > maxsint(bits):
            raise ValueError(f'value is too large or too small: {value}')


def check_float(value, bits=4*BYTESIZE):
    """Like 'check_uint', but for floats.
    
    Raises:
        TypeError or ValueError:
            If *bits* is not 32
            (in addition to the exceptions raised by 'check_uint').
    """
    if not isinstance(value, float):
        raise TypeError(f'value is not a float: {value}')
        
    check_uint(bits)
        
    if bits != 4*BYTESIZE:
        raise ValueError(f'*bits* should be 32, not {bits}')
        
    try:
        struct.pack('>f', value)
    except OverflowError:
        raise ValueError(f'value is too large or too small: {value}')
    
    
def check_bin(value, bits=None):
    """Like 'check_uint', but for binary strings.
    
    A binary string is '' or a string of '1's and '0's.
    If *bits* is None, it is set to len(value).
    
    Raises:
        ValueError:
            If len(value) != bits
            (in addition to the exceptions raised by 'check_uint').
    """
    # Print 'repr(value)' instead of 'value',
    # since *value* is probably a string.
    if not isinstance(value, str):
        raise TypeError(f'value is not a str: {repr(value)}')
        
    if bits is None:
        bits = len(value)
        
    check_uint(bits)
        
    if bits != len(value):
        raise ValueError(
            f'bits != len(value); bits={bits}, value={repr(value)}')

    regex=f'\A[01]{{{bits}}}\Z'
    if not re.match(regex, value):
        raise ValueError(
            f'{repr(value)} is not a {bits} bit binary string')


def bin_str(i: int, bits: int) -> str:
    """Return a *bits* bit binary representation of i.
    
    *i* must be non-negative, but returned strings are cropped
    at *bits* characters so that representations of signed integers
    are handled correctly.
    E.g. bin_str(-1, 1) doesn't work,
    but bin_str(255, 1) returns the correct value of '1'.
    """
    string = (
        # Returns something like '0b101'.
        bin(i)
        # Remove '0b'.
        [2:]
        # Remove extra bits.
        # Uints are padded with 0s and sints with 1s.
        # Unlike slicing with negative indices,
        # this syntax produces empty strings when bits=0.
        [::-1][0:bits][::-1]
        # Pad with zeroes to a length of *bits*.
        .zfill(bits)
    )
    return string
