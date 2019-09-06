"""This module contains functions for converting a variable of one 
type (unsigned integer, signed integer, float or string) to another 
type while maintaining the original binary representation of the 
variable.
"""

import struct
from typing import Iterable, List

from .check import check

def signed_range(bits: int) -> range:
    """Return the range of *bits* bit signed integers."""
    check(bits, 'bits', types=(int,), min_=0)
    return range(-2**(bits-1), 2**(bits-1))

def unsigned_range(bits: int) -> range:
    """Return the range of *bits* bit unsigned integers."""
    check(bits, 'bits', types=(int,), min_=0)
    return range(2**bits)
    
def uint_to_sint(i: int, bits: int) -> int:
    """Convert an unsinteger to a signed one.
    
    This function converts an unsigned integer to a signed integer 
    with the same binary representation. The two's complement 
    representation is used to form binary representations of negative 
    numbers.
    
    For example, with 8 bits the following conversion table is used: 
       
      0 ->    0
      1 ->    1
    ...
    126 ->  126
    127 ->  127
    128 -> -128
    129 -> -127
    ...
    254 ->   -2
    255 ->   -1
     
    Raises:
        ValueError: If i cannot be represented by the given number of 
            bits.
    """
    check(i, 'i', values=unsigned_range(bits))
    return i if i in signed_range(bits) else i - 2**bits

def sint_to_uint(i: int, bits: int) -> int:
    """Convert a signed integer to an unsigned one.
    
    This is the reverse function of uint_to_sint. For example, with 8 
    bits the following conversion table is used: 
        
    −128 -> 128
    −127 -> 129
    ...
      −2 -> 254
      −1 -> 255
       0 ->   0
       1 ->   1
    ...
     126 -> 126
     127 -> 127
     """
    check(i, 'i', values=signed_range(bits))
    return i + 2**bits if i < 0 else i
    

def str_to_int(s: str) -> int:
    """Convert a binary string to an integer.
    
    This function interprets a string of 1's and 0's as the 
    binary representation of an unsigned integer and returns that 
    integer. 

    Raises:
        ValueError: If s is not a string of only 1's and 0's.
    """
    check(s, 's', regex='^[0|1]+$')
    return int(s, 2)

def int_to_str(i: int, bits: int) -> str:
    """Convert an integer to a binary string.
    
    This is the reverse function of str_to_int.
    
    Raises:
        ValueError: If i cannot be represented by the given number of 
            bits.
    """
    check(i, 'i', values=unsigned_range(bits))    
    return bin(i)[2:].zfill(bits)

def combine_ints(ints: Iterable[int], bytesize: int) -> int:
    """Interpret many small integers as one large integer.
    
    This function takes a list of integers, appends their binary 
    representations one after another, and interprets the resulting 
    binary string as a single large integer. Only unsigned integers 
    are supported.
    
    Args:
         ints: An iterable of integers to be combined.
         bytesize: The number of bits which should be used in the binary 
             representation of each of the integers.
         
    Raises:
        ValueError: If any of the given integers cannot be represented 
            by the given number of bits.
    """
    strings = [int_to_str(i, bytesize) for i in ints]
    big_string = ''.join(strings)
    return str_to_int(big_string)
    
def split_int(i: int, n_bytes: int, bytesize: int) -> List[int]:
    """Interpret one large integer as many small ones.
    
    This is the reverse function of combine_ints. It takes a large 
    integer, splits its binary representation to many equally sized 
    sections, and interprets each of the sections as a single smaller 
    integer. Only unsigned integers are supported.
    
    Args:
         i: An unsigned integer to be split.
         n_bytes: The number integers i should be split into.
         bytesize: The length (in bits) of the sections into which the 
             binary representation of i is split.
         
    Raises:
        ValueError: If i is too large to be split into the given 
            number of integers of the given size.
    """
    check(n_bytes, 'n_bytes', types=(int,), min_=1)
    big_string = int_to_str(i, n_bytes*bytesize)
    strings = [big_string[n*bytesize:(n+1)*bytesize] for n in range(n_bytes)]
    return [str_to_int(s) for s in strings]

def float_to_int(x: float) -> int:
    """Convert a float to an integer with the same binary 
    representation.
    
    This function takes a float, converts it to its binary 
    representation using the IEEE 754 standard for 32 bit 
    single-precision floating-point numbers, and then returns an 
    unsigned integer with the same binary representation.
    
    Raises:
        ValueError: If x is too large to be represented as a 32 bit 
            float.
    """
    try:
        ints = list(struct.pack('>f', x))
    except OverflowError:
        raise ValueError(f'{x} is too large to be a single-precision float')
        
    return combine_ints(ints, 8)    
    
def int_to_float(i: int) -> float:
    """Convert an unsigned integer to a float with the same binary 
    representation.
    
    This is the reverse function of float_to_int.    
         
    Raises:
        ValueError: If i is too large to be represented as a 32 bit 
            int.
    """    
    ints = split_int(i, 4, 8)
    bytes_ = struct.pack('4B', *ints) # Format: 4 unsigned chars (4*8 bits)
    return struct.unpack('>f', bytes_)[0] # Format: big-endian float (32 bits)