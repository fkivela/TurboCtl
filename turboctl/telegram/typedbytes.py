"""This module defines the TypedBytes subclass of ByteHolder."""

import math

#from turboctl.telegram import conversions as c
#from turboctl.telegram.byteholder import ByteHolder
#from turboctl.telegram.numtypes import Types

from ..data import Types

from .byteholder import ByteHolder
from . import conversions as c

class TypedBytes(ByteHolder):
    """Save multi-byte numbers to a bytearray.
    
    This class works the same way as a ByteHolder, but instead of
    just unsigned integers, it can also store signed integers, binary 
    strings and floating-point numbers.
    
    Internally, values that are not unsigned integers are converted
    into unsigned integers with the same binary representation.
    
    Example:
        Values can be assigned using a value of any valid type
        (int, str or float). The type of the value is detected
        automatically, and the value is converted to an unsigned 
        integer with the same binary representation.
        >> tb = TypedBytes([1,2,3])
        >> tb[0:2] = '0000000011111111'
        >> print(tb)
        << TypedBytes([0,255,3])
        
        >> tb[2] = -1
        >> tb
        << TypedBytes([0,255,255])
    
        When reading values, the default return type is an unsigned
        integer.
        >> tb[0]
        << 0
        Other return types can be specified by passing an instance of
        Types as a second argument.
        >> tb[0, Types.STR]
        << '00000000'
        >> tb[0:2, Types.SINT]
        << -1
    """
        
    def __setitem__(self, indices, value):
        """Set self[indices] to *value*.
        
        Args:
            indices: An integer or a slice.
            value: An int, a str, or a float.
        
        Raises:
            TypeError: If *value* is not of a valid type.
            ValueError: If *indices* specifies an amount of indices
                that is not large enough to store *value*. If *value*
                is a float, *indices* must specify exactly 
                4 bytes/cells bits (32 bits). 
        """
        
        index_bits = self._bits_in_indices(indices)
        value_bits = self._bits_in_value(value)
        
        if index_bits < value_bits:
            raise ValueError(
                f'{value_bits} bits are needed to save the value {value}, '
                f'only {index_bits} were given.')
            
        # It's important that index_bits are used here instead of 
        # value_bits, otherwise signed ints will break.
        uint_val = self._to_unsigned_int(value, index_bits)
        super().__setitem__(indices, uint_val)
        
    def __getitem__(self, arg):
        """Return self[arg].
        
        This function is used with the syntax
        >> typedbytes[indices]
        or
        >> typedbytes[indices, type_]
        
        Args:
            arg: An integer/slice (if the [indices] syntax is used)
                or a tuple of an integer/slice and an instance of Types
                (if the [indices, type_] syntax is used).
                
        Returns:
            An int, str or float depending on *type_*. If type_ 
            is not specified, a default value of type_=Types.UINT 
            will be used.
                
        Raises:
            TypeError: If *arg* doesn't follow the correct syntax. 
            ValueError: If *type_* is not a valid instance of Types.
        """
        
        indices, type_ = self._parse_getter_arg(arg)
        index_bits = self._bits_in_indices(indices)
                        
        uint_val = super().__getitem__(indices)
        return self._from_unsigned_int(uint_val, type_, index_bits)
        
    def _bits_in_indices(self, indices):
        """Return the number of bits corresponding to *indices*.
        
        This is 8 times the number of corresponding bytes.
        """
        
        if isinstance(indices, int):
            return self.BYTESIZE
            
        if isinstance(indices, slice):
            return self._number_of_bytes(indices) * self.BYTESIZE
            
        raise TypeError(
            f'*indices* should be int or slice, not {type(indices)}')
    
    def _bits_in_value(self, value):
        """Return the minimum number of bits needed to save *value*."""
        
        if isinstance(value, int) and value >= 0:
            return math.ceil(math.log(value + 1, 2))
            
        if isinstance(value, int) and value < 0:
            # ~x = -x-1
            return math.ceil(math.log(~(2 * value) + 1, 2))
            
        if isinstance(value, str):        
            return len(value)
            
        if isinstance(value, float):
            # floats are always 32 bits
            return 4 * self.BYTESIZE
            
        else:
            raise TypeError(
                f'*value* should be int, str or float, not {type(value)}')
        
    @staticmethod
    def _to_unsigned_int(value, index_bits):
        """Return an unsigned integer with the same binary
        representation as *value*.
        
        *index_bits* signifies the number of bits used in the
        representation (relevant for signed integers and floats).
        """
        
        if isinstance(value, int) and value >= 0:
            return value
            
        if isinstance(value, int) and value < 0:
            return c.signed_to_unsigned_int(value, index_bits)
            
        if isinstance(value, str):        
            return c.str_to_int(value)
            
        if isinstance(value, float):
            
            if index_bits != 32:
                raise ValueError(
                    f'floats have a size of 32 bits, but a size of '
                    f'{index_bits} bits was requested.')
            
            return c.float_to_int(value)
            
        else:
            raise TypeError(
                f'value must be int, str or float, not {type(value)}')
        
    @staticmethod
    def _from_unsigned_int(uint_val, type_, index_bits):
        """Return a value of type *type_* with the same binary representation as *uint_val*
        
        Args:
            uint_val: An unsigned integer (an int that is >= 0).
            type_: An instance of Types.
            index_bits: An int specifying how many bits are used
                in the representation.
                
        Returns:
            An int, str or float depending on *type_*.
                
        Raises:
            ValueError: If *type_* is Types.FLOAT but *index_bits* is 
                not 32. 
            TypeError: If *type_* is not a valid instance of Types.
        """
        
        if type_ is Types.UINT:
            return uint_val
        
        if type_ is Types.SINT:
            return c.unsigned_to_signed_int(uint_val, index_bits)
        
        if type_ is Types.STR:
            return c.int_to_str(uint_val, index_bits)
        
        if type_ is Types.FLOAT:
            
            if index_bits != 32:
                raise ValueError(
                    f'floats have a size of 32 bits, but a size of '
                    f'{index_bits} bits was requested.')
            
            return c.int_to_float(uint_val)
                
        raise TypeError(
            f"*type_* must be a valid instance of Types, not {type_}")
        
    def _parse_getter_arg(self, arg):
        """Return *indices* and *type* by parsing the argument of the
        __getitem__ method."""
        
        if isinstance(arg, (int, slice)):
            indices = arg
            type_ = Types.UINT
        else:
            
            try:
                indices = arg[0]
                type_ = arg[1]
            except (TypeError, IndexError):
                raise TypeError(
                        f'getter indices must use the format [index] '
                        f'or [index, type_]')
                
        return indices, type_