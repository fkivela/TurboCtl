"""This module defines classes for different data types used by the 
pump.

Since the classes inherit their magic methods, arithmetic operations 
with them return instances of built-in classes.
E.g. Uint(1) + Uint(1) = int(2)
However, the operations Bin(s1) + Bin(s2), Bin(s1) += Bin(s2) and 
Bin[i] are overridden to return Bins. 
"""

from __future__ import annotations
# ^ This enables forward referencing with type hints.
from typing import Union
import math
import struct

from .check import check

byteslike = Union[bytes, bytearray]
# TODO: Bin(1) ei toimi

def signed_range(bits: int) -> range:
    """Return the range of *bits* bit signed integers."""
    check(bits, 'bits', types=(int,), min_=0)
    return range(-2**(bits-1), 2**(bits-1))

def unsigned_range(bits: int) -> range:
    """Return the range of *bits* bit unsigned integers."""
    check(bits, 'bits', types=(int,), min_=0)
    return range(2**bits)

class TurboNum:
    """An abstract superclass for all pump data types."""    
    
    BYTESIZE = 8
    
    def __new__(cls, value, *args):
        """Return an instance of a subclass of this class.
        
        This function selects an appropriate subclass based on 
        the type of *value*, and returns subclass(value, *args).
        """        
        if isinstance(value, int) and value >= 0:
            numtype = Uint
        elif isinstance(value, int) and value < 0:
            numtype = Sint
        elif isinstance(value, str):
            numtype = Bin
        elif isinstance(value, float):
            numtype = Float
        else:
            raise TypeError(
                f"'value' should be an int, a str or a float, "
                f"not {type(value).__name__}")
            
        return numtype(value, *args)
        
    def to(self, type_):
        return type_.from_bytes(self.to_bytes())
    
    @property
    def n_bytes(self) -> int:
        """Return the amount of bytes (of size self.BYTESIZE) needed 
        to represent *self*.
        """
        return math.ceil(self.bits / self.BYTESIZE)
     
        
class Uint(int, TurboNum):
    """An unsigned integer."""
    
    description = 'unsigned integer'
    
    def __new__(cls, value, bits: int=8):
        """Return a new *bits* bit Uint with a value of *value*.
        *value* is parsed with int(value).
        
        Raises:
            ValueError: If *value* cannot be parsed into a *bits* bit 
                unsigned integer.
        """
        i = int(value)
        check(i, 'value', values=unsigned_range(bits))
        return super().__new__(cls, i)
    
    def __init__(self, value, bits: int=8):
        self.bits = bits
        
    @classmethod
    def from_bytes(cls, bytes_: byteslike) -> Uint:
        """Create a Uint object from its binary representation."""
#        ints = list(bytes_)
#        bits = len(bytes_) * cls.BYTESIZE
#        int_ = c.combine_ints(ints, cls.BYTESIZE)
#        return Uint(int_, bits)
        i = int.from_bytes(bytes_, 'big')
        bits = len(bytes_) * cls.BYTESIZE
        return Uint(i, bits)
        
    def to_bytes(self) -> bytes:
        """Return the binary representation of *self*."""
        #ints = c.split_int(self, self.n_bytes, self.BYTESIZE)
        #return bytes(ints)
        return super().to_bytes(self.n_bytes, 'big')
    
    def to_builtin(self) -> int:
        """Return *self* as an int object."""
        return int(self)


class Sint(int, TurboNum):
    """A signed integer."""
    
    description = 'floating point number'
    
    def __new__(cls, value, bits=8):
        """Return a new *bits* bit Sint with a value of *value*.
        *value* is parsed with int(value).
        
        Raises:
            ValueError: If *value* cannot be parsed into a *bits* bit 
                signed integer.
        """
        i = int(value)
        check(i, 'value', values=signed_range(bits))
        return super().__new__(cls, i)
    
    def __init__(self, value, bits=8):
        self.bits = bits        
        
    @classmethod
    def from_bytes(cls, bytes_: byteslike) -> Sint:
        """Create a Sint object from its binary representation."""
#        ints = list(bytes_)
#        bits = cls.BYTESIZE * len(bytes_)
#        uint = c.combine_ints(ints, cls.BYTESIZE)
#        sint = c.uint_to_sint(uint, bits)
#        return Sint(sint, bits)
        i = int.from_bytes(bytes_, 'big', signed=True)
        bits = len(bytes_) * cls.BYTESIZE
        return Sint(i, bits)
        
    def to_bytes(self) -> byteslike:
        """Return the binary representation of *self*."""
#        uint = c.sint_to_uint(self, self.bits)
#        ints = c.split_int(uint, self.n_bytes, self.BYTESIZE)
#        return bytes(ints)
        return super().to_bytes(self.n_bytes, 'big', signed=True)
    
    def to_builtin(self) -> int:
        """Return *self* as an int object."""
        return int(self)


class Float(float, TurboNum):
    """A 32 bit single precision floating-ponit number."""
    
    description = 'floating point number'
    bits = 32
    
    def __new__(cls, value, bits: int=32):
        """Return a new 32 bit Float with a value of *value*.
        *value* is parsed with float(value).
        
        The *bits* argument is included to give all __new__ methods 
        of TurboNum subclasses the same signature, but its value must 
        always be 32.
        
        Raises:
            TypeError or ValueError: If *bits* is not 32.
            ValueError: If *value* cannot be parsed into a 32 bit 
                float.
        """
        check(bits, 'bits', types=(int,), values=(32,))
        x = float(value)
        # Make sure x isn't too large to be a 32 bit float.
        try:
            struct.pack('>f', x)
        except OverflowError:
            raise ValueError(
                f'{x} is too large to be a single-precision float')
            
        return super().__new__(cls, x)
    
    @classmethod
    def from_bytes(cls, bytes_: byteslike) -> Float:
        """Create a Float object from its binary representation."""
        #ints = list(bytes_)
        #int_ = c.combine_ints(ints, cls.BYTESIZE)
        #return Float(c.int_to_float(int_))
#        i = Uint.from_bytes(bytes_)
#        x = c.int_to_float(i)
#        return Float(x)
        return Float(struct.unpack('>f', bytes_)[0])

    def to_bytes(self) -> byteslike:
        """Return the binary representation of self."""
        #i = c.float_to_int(self)
        #ints = c.split_int(i, self.n_bytes, self.BYTESIZE)
        #return bytes(ints)
#        i = c.float_to_int(self)
#        return Uint(i, self.bits).to_bytes()
        return struct.pack('>f', self)

    def to_builtin(self) -> float:
        """Return *self* as a float object."""
        return float(self)


class Bin(str, TurboNum):
    """A binary string (i.e. a string of '1's and '0's)."""

    description = 'binary string'
    
    def __new__(cls, value: str, bits=None):
        """Return a new 32 bit Float with a value of *value*.
        
        *value* is parsed with str(value).zill(bits).
        If *bits* is None, it will set to len(str(value)).
        
        Raises:
            ValueError: If *value* cannot be parsed into a string 
                of '1's and '0's with a length of *bits* or less.
        """
        if bits == None:
            bits = len(str(value))
            
        s = str(value).zfill(bits)
        check(s, 'value', regex=f'^[0|1]{{{bits}}}$')
        return super().__new__(cls, s)
    
    def __init__(self, value, bits=None):
        if bits == None:
            bits = len(str(value))
        self.bits = bits
        
    def __add__(self, other):
        """Adding two Bins returns a Bin."""
        result = super().__add__(other)
        return Bin(result) if isinstance(other, Bin) else result
    
    def __getitem__(self, i):
        """Getting an index or a slice of a Bin returns a Bin."""
        return Bin(super().__getitem__(i))
                
    @classmethod
    def from_bytes(cls, bytes_: byteslike) -> Bin:
        """Create a Bin object from its binary representation."""
        #ints = list(bytes_)
        #int_ = c.combine_ints(ints, bytesize=cls.BYTESIZE)
        #bits = cls.BYTESIZE * len(bytes_)
        #str_ = c.int_to_str(int_, bits)
        #return Bin(str_)
#        i = Uint.from_bytes(bytes_)
#        s = c.int_to_str(i, i.bits)
#        return Bin(s)
        i = int.from_bytes(bytes_, 'big')
        bits = len(bytes_) * cls.BYTESIZE
        return Bin(bin(i)[2:].zfill(bits))

    def to_bytes(self) -> byteslike:
        """Return the binary representation of self."""
        #i = c.str_to_int(self)
        #ints = c.split_int(i, self.n_bytes, self.BYTESIZE)
        #return bytes(ints)
        #i = c.str_to_int(self)
        #return Uint(i, self.bits).to_bytes()
        return int(self, 2).to_bytes(self.n_bytes, 'big')
    
    def to_builtin(self) -> str:
        """Return *self* as a str object."""
        return str(self)