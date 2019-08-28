def check_val(x, name, types=None, min=-float('inf'), max=float('inf'), values=None):
    
    if types:
        check_type(x, name, types)
        
    



def check_type(var, name, types):
    
    try:      
        valid_types = ', '.join([t.__name__ for t in types])
    except TypeError:
        valid_types = types.__name__
        
    msg = (f"'{name}' should be one of the following: {valid_types}; "
           f"not {type(var).__name__}")

    if not isinstance(var, types):
        raise TypeError(msg)
        
def check_range(x, name, min_, max_):
    
    msg = (f"'{name}' should be between of the following: {valid_types}; "
           f"not {type(var).__name__}")
    
    if not min_ <= x <= max_:
        raise ValueError()
    



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
