"""This module contains functions for converting a variables of one 
type (unsigned integer, signed integer, float or string) to another 
type while maintaining the original binary representation of the 
variable.
"""

import struct
import re

check(bits, types=int, min_=0)


def check_val(val, types=None, min=-float('inf'), max=float('inf'), values=None):
    pass





def check_type(var, name, types):
    
    try:      
        valid_types = ', '.join([t.__name__ for t in types])
    except TypeError:
        valid_types = types.__name__
        
    msg = (f"'{name}' should be one of the following: {valid_types}; "
           f"not {type(var).__name__}")

    if not isinstance(var, types):
        raise TypeError(msg)

def check_range()


def is_sint(i, bits):
    """Return True if *i* is a valid *bits* bit signed integer.
    
    For example, 8 bits is enough to represent signed integers from 
    -128 to 127.
    
    Using this function prevents a problem where the program freezes 
    when 'x in range(a_large_number)' is called for a non-integer 
    float x.
    
    Args:
        i: An object to be tested (may be any type).
        bits: An integer.
        
    Returns:
        True or False.
        
    Raises:
        ValueError: If bits is not positive.
    """
    check_uint(bits, float('inf'))
    if bits <= 0:
        raise ValueError(
            f"'bits' should be a positive number, now was {bits}.")
    
    if not isinstance(i, int):
        return False
    
    return -2**(bits-1) <= i < 2**(bits-1)

def in_uint_range(i, bits):
    """Return True if *i* is a valid *bits* bit unsigned integer.
    
    For example, 8 bits is enough to represent signed integers from 
    0 to 255.
    
    Using this function prevents a problem where the program freezes 
    when 'x in range(a_large_number)' is called for a non-integer 
    float x.
    
    Args:
        i: An object to be tested (may be any type).
        bits: An integer.
        
    Returns:
        True or False.
        
    Raises:
        ValueError: If bits is not positive.
    """
    
    
    if bits <= 0:
        raise ValueError(
            "'bits' should be a positive number, now was {bits}.")
    
    if not isinstance(i, int):
        return False
    
    return 0 <= i < (2**bits)
    
def signed_to_unsigned_int(i, bits):
    """Convert a signed integer to an unsigned one.
    
    This function converts a signed integer to an unsigned integer 
    with the same binary representation. The two's complement 
    representation is used to form binary representations of negative 
    numbers.
    
    For example, with 8 bits the following conversion table is used: 
        
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
     
     Args:
         i: The integer to be converted.
         bits: The number of bits that should be used in the binary 
             representation of i.
             
     Returns:
         An unsigned integer (int) with the same binary 
         representation as i.
         
     Raises:
         ValueError: If i cannot be represented by the given number of 
             bits.
    """
    
    if not in_signed_range(i, bits):
        raise ValueError(f'{i} is not a valid {bits} bit signed integer.')
    
    if i < 0:
        return i + 2**bits
    else:
        return i 
    
def unsigned_to_signed_int(i, bits):
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
     
    Args:
        i: The integer to be converted.
        bits: The number of bits that should be used in the binary 
            representation of i.
             
    Returns:
        A signed integer (int) with the same binary 
        representation as i.
         
    Raises:
        ValueError: If i cannot be represented by the given number of 
            bits.
    """
        
    if not in_unsigned_range(i, bits):
        raise ValueError(f'{i} is not a valid {bits} bit unsigned integer.')
    
    if not in_signed_range(i, bits):
        return i - 2**bits
    else:
        return i

def str_to_int(s):
    """Convert a binary string to an integer.
    
    This function interprets a string of 1's and 0's as the 
    binary representation of an unsigned integer and returns that 
    integer. 
     
    Args:
         s: The string to be converted.
             
    Returns:
         An unsigned integer (int).
         
    Raises:
        ValueError: If s is not a string of only 1's and 0's.
    """
    
    regex = '^[0|1]+$'
    
    if not re.search(regex, s):
        raise ValueError(f'{s} is not a valid binary string.')
    
    return int(s, 2)

def int_to_str(i, bits):
    """Convert an integer to a binary string.
    
    This functions returns a string of 1's and 0's corresponding to 
    the binary representation of a given unsigned integer. 
     
    Args:
         i: An unsigned integer (int).
         bits: The number of bits which should be used in the binary 
             representation.
             
    Returns:
         A string of 1's and 0's (str).
         
    Raises:
        ValueError: If i cannot be represented by the given number of 
            bits.
    """
    
    if not in_unsigned_range(i, bits):
        raise ValueError(f'{i} is not a valid {bits} bit unsigned integer.')
    
    return bin(i)[2:].zfill(bits)

def combine_ints(ints, bytesize):
    """Interpret many small integers as one large integer.
    
    This function takes a list of integers, appends their binary 
    representations one after another, and interprets the resulting 
    binary string as a single large integer. Only unsigned integers 
    are supported.
    
    Args:
         ints: A list or other iterable containing the integers to be 
             combined.
         bits: The number of bits which should be used in the binary 
             representation of each of the integers.
             
    Returns:
         An unsigned integer (int).
         
    Raises:
        ValueError: If any of the given integers cannot be represented 
            by the given number of bits.
    """
    
    strings = [int_to_str(i, bytesize) for i in ints]
    big_string = ''.join(strings)
    return str_to_int(big_string)
    
def split_int(i, n_bytes, bytesize):
    """Interpret one large integer as many small ones.
    
    This function takes a large integer, splits its binary 
    representation to many equally sized sections, and interprets 
    each of the sections as a single smaller integer. Only unsigned 
    integers are supported.
    
    Args:
         i: An unsigned integer to be split (int).
         n_bytes: The number integers i should be split into.
         bytesize: The length (in bits) of the sections into which the 
             binary representation of i is split.
             
    Returns:
         A list of ints.
         
    Raises:
        ValueError: If i is too large to be split into the given 
            number of integers of the given size.
    """
    
    big_string = int_to_str(i, n_bytes*bytesize)
    strings = [big_string[n*bytesize:(n+1)*bytesize] for n in range(n_bytes)]
    return [str_to_int(s) for s in strings]

def float_to_int(x):
    """Convert a float to an integer with the same binary 
    representation.
    
    This function takes a float, converts it to its binary 
    representation using the IEEE 754 standard for 32 bit 
    single-precision floating-point numbers, and then returns an 
    unsigned integer with the same binary representation.
    
    Args:
         x: A float.
             
    Returns:
         An unsigned integer (int).
         
    Raises:
        ValueError: If x is too large to be represented as a 32 bit 
            float.
    """
    
    try:
        ints = list(struct.pack('>f', x))
    except OverflowError as e:
        raise ValueError(
            f'{x} is too large to be a single-precision float.') from e
        
    return combine_ints(ints, 8)
    
def int_to_float(i):
    """Convert an unsigned integer to a float with the same binary 
    representation.
    
    This function converts an integer to its binary representation, 
    and then interprets that as an IEEE 754 32 bit single-precision 
    floating-point number, which is returned.
    
    Args:
         i: An unsigned integer (int).
             
    Returns:
         A float. Note that this may be +-float('inf') or float('nan')
             if i is very large.
         
    Raises:
        ValueError: If i is too large to be represented as a 32 bit 
            float.
    """
    
    ints = split_int(i, 4, 8)
    bytes_ = struct.pack('4B', *ints) # Format: 4 unsigned chars (4*8 bits)
    return struct.unpack('>f', bytes_)[0] # Format: big-endian float (32 bits)