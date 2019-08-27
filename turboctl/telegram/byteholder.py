"""This module defines the ByteHolder class."""

from . import conversions as c

class ByteHolder:
    """Save multi-byte integers to a bytearray.
    
    Initialization: 
        >> bh = ByteHolder(data) 
        sets bh.data to bytearray(data).
        *data* must thus be a valid argument for the bytearray 
        initializer.
    
    Usage:
        Assigning and returning values with the syntax
        >> bh[number] = value
        >> value = bh[number]
        works in the same way as with a bytearray object.
        
        If *number* if replaced with a slice of length n,
        the binary representation of the value will be split into n 
        8-bit bytes, and the value of each byte will be saved to a 
        different cell of bh.data.
        
    Example:
        >> bh = ByteHolder([1,2,3])
        >> bh.data
        << bytearray(b'\x01\x02\x03')
        
        >> bh[0]
        << 1
        >> bh[:]
        << 66051 # = int('00000001' + '00000010' + '00000011', 2)
        
        >> bh[1:3] = 500 # 500 = int('1' + '11110100', 2)
        >> bh
        << ByteHolder([1, 1, 244])
    """
    
    BYTESIZE = 8
    
    def __init__(self, data):
        """Initialize self and set self.data to bytearray(data)."""
        self.data = bytearray(data)
        
    def __repr__(self):
        """Return repr(self).
        
        "eval repr(self)" returns a copy of *self*.
        """
        return f'{type(self).__name__}({list(self.data)})'
            
    def __eq__(self, other):
        """Return self == other
        
        True will be returned, IFF *self* and *other* are both 
        byteholders and contain the same data.
        """
        
        if not isinstance(other, ByteHolder):
            return False
        
        return self.data == other.data
    
    def __len__(self):
        """Return len(self)."""
        return len(self.data)
    
    def __setitem__(self, indices, value):
        """Set self[indices] to *value*.
        
        Args:
            indices: An integer or a slice.
            value: An integer.
        
        Raises:
            TypeError: If *indices* is of an invalid type.
        """
        
        # "bytearray[indices] = value" demands that *value* is an int 
        # if *indices* is an int, and a list if *indices* is a slice.
        
        if isinstance(indices, int):
            self.data[indices] = value
            
        elif isinstance(indices, slice):
            n_bytes = self._number_of_bytes(indices)
            # byte_values is a list
            byte_values = c.split_int(value, n_bytes, self.BYTESIZE)
            self.data[indices] = byte_values
            
        else:
            raise TypeError(
                f'*indices* should be int or slice, not {type(indices)}')
        
    def _number_of_bytes(self, slice_):
        """Return the number of cells/bytes in *self* corresponding to
        *slice_*.
        
        This is not necessarily slice_.stop - slice_.start,
        since slice_.stop and slice_.start might be smaller or larger 
        than the largest and smallest valid indices of *self*.
        """
        L = len(self)
        index_range = range(L)[slice_]
        return len(index_range)
        
    def __getitem__(self, indices):
        """Return self[indices].
        
        Args:
            indices: An integer or a slice.
            
        Returns:
            An integer.
        
        Raises:
            TypeError: If *indices* is of an invalid type.
        """
        
        if isinstance(indices, int):
            return self.data[indices]
            
        elif isinstance(indices, slice):
            value_bytes = list(self.data[indices])
            return c.combine_ints(value_bytes, self.BYTESIZE)
                        
        else:
            raise TypeError(
                f'*indices* should be int or slice, not {type(indices)}')