"""This module defines the enum Types."""

import enum as e

class Types(e.Enum):
    """Enum of different types of numbers.
    
    This enum class represents four different types of numbers:
    unsigned and signed integers (UINT and SINT), strings (STR), and 
    floating-point numbers (FLOAT).
    
    This class also includes some utility functions related to these
    types.
    
    A separate enum is needed instead of simply using built-in types
    (i.e. int, str, float), because Python doesn't differentiate
    between signed and unsigned integers.
    
    Strings are included as a number type to provide support for 
    representing binary numbers as strings of 1's and 0's.
    """ 
    
    def __init__(self, description):
        """Create a new instance of this enum.
        
        The value of this instance will be set to *description*,
        and can be accessed using either "x.value" or "x.description".
        """
        self.description = description
    
    # This weird enum syntax calls __init__
    UINT = ('unsigned integer')
    SINT = ('signed integer')
    STR = ('string')
    FLOAT = ('floating-point number')
    
    # __repr__(self) returns '<Types.XYZ: 1234>' by default.
    # It must be overridden so that the syntax "copy = eval(repr(x))" 
    # works.
    def __repr__(self):
        return str(self)
    
    @classmethod
    def to_type(cls, var, type_):
        """Converts *var* to a type corresponding to *type_*.
        
        Args:
            var: A variable of any type.
            type_: An instance of this class.
            
        Returns:
            - int(var), if type_ is cls.UINT or cls.SINT
            - str(var), if type_ is cls.STR
            - float(var), if type_ is cls.FLOAT
            
        Raises: 
            TypeError: If *type_* is not a valid instance of this 
                class.
            ValueError: If *var* cannot be converted to *type_*.
        """
       
        if type_ in (cls.UINT, cls.SINT):
            i = int(var)
            
            if i < 0 and type_ is cls.UINT:
                raise ValueError(
                    f"Can't convert the negative number {i} to UINT")
        
            return i
        
        if type_ == cls.STR:
            return str(var)
        
        if type_ == cls.FLOAT:
            return float(var)
    
        raise TypeError(f'Invalid type: {type_}')

    @classmethod
    def type_of(cls, var):
        """Return an instance of this class corresponding to the 
        type of *var*
        
        Args:
            var: A variable of any type.
            
        Returns:
            - cls.UINT, if var is a non-negative int
            - cls.SINT, if var is a negative int
            - cls.STR, if var is a str
            - cls.FLOAT, if var is a float
            
        Raises: 
            TypeError: If *var* is not an instance of any of the types 
            mentioned above.
        """
        type_ = type(var)
        
        if type_ == int and var >= 0:
            return cls.UINT
        elif type_ == int and var < 0:
            return cls.SINT
        elif type_ == str:
            return cls.STR
        elif type_ == float:
            return cls.FLOAT
        else:
            raise TypeError(f'Invalid type: {type_}')
            
    @classmethod
    def is_type(cls, var, type_):
        """Return True, if *var* is of type *type_*.
        
        Args:
            var: A variable of any type.
            type_: An instance of this class.
            
        Returns:
            True, if:
                - var is a non-negative int and type_ is cls.UINT
                - var is any int and type_ is cls.SINT
                - var is a str and type_ is cls.STR
                - var is a float and type_ is cls.FLOAT
        """
        
        try:
            var_type = cls.type_of(var)
        except TypeError:
            return False

        # Unsigned integers are a subset of signed integers:        
        if var_type == cls.UINT and type_ == cls.SINT:
            return True
        
        return var_type == type_