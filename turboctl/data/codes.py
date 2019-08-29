"""This module defines the meaning of different codes and numbers used 
in TURBOVAC telegrams.
"""

import enum as e

class ValueAndDescription(e.Enum):
    """A superclass for enums that contains an additional attribute 
    (*description*) in addition to *value*.
    
    This enum doesn't have any members, since it's only meant to 
    be subclassed.
    
    A member of a subclass of this enum can be returned with
    any of the following:
    >> member = EnumName.MEMBER_NAME
    >> member = EnumName['MEMBER_NAME']
    >> member = EnumName(member_value)
    >> member = EnumName(member)
    """
    
    def __new__(cls, value, description):
        """__new__ is defined instead of __init__, because setting 
        *_value_* in __init__ prevents the syntax 
        "member = EnumName(value_of_member)" from working.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
            
    def __repr__(self):
        """repr(self) returns '<ParameterAccess.XYZ: 1234>' by default.
        It must be overridden so that the syntax 
        "copy = eval(repr(x))" 
        works.
        """
        return str(self)
    

class ParameterAccess(ValueAndDescription):
    """Different parameter access modes.
    
    Members of this enum have the following attributes:
        value: The parameter access code as a 4-character string of 1's
            and 0's.
        description: A string describing the meaning of the code.
    """
    
    NONE = ('0000', 'No access')
    R    = ('0001', 'Parameter value requested')
    W16  = ('0010', 'Write a 16 bit value')
    W32  = ('0011', 'Write a 32 bit value')
    RF   = ('0110', 'Field value requested')
    W16F = ('0111', 'Write a 16 bit field value')
    W32F = ('1000', 'Write a 32 bit field value')
    
    # Properties don't work with the Enum class, so these are defined
    # as functions.
    @classmethod
    def invalid_code(cls):
        """Returns an invalid access code."""
        return '1111'
    
    @classmethod
    def read_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        reading a parameter.
        """
        return {cls.R, cls.RF}

    @classmethod
    def write_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        writing to a parameter.
        """
        return {cls.W16, cls.W32, cls.W16F, cls.W32F}
    
    @classmethod
    def sixteen_bit_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        accessing 16 bit parameters.
        """
        return {cls.R, cls.RF, cls.W16, cls.W16F}
    
    @classmethod    
    def thirty_two_bit_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        accessing 32 bit parameters.
        """
        return {cls.R, cls.RF, cls.W32, cls.W32F}
    
    @classmethod    
    def unindexed_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        accessing unindexed parameters.
        """
        return {cls.R, cls.W16, cls.W32}
    
    @classmethod
    def indexed_modes(cls):
        """Returns a set of the modes (members of this enum) used for 
        accessing indexed parameters.
        """
        return {cls.RF, cls.W16F, cls.W32F}
            
    
class ParameterResponse(ValueAndDescription):
    """Different parameter response modes.
    
    Members of this enum have the following attributes:
        value: The parameter response code as a 4-character string of 1's
            and 0's.
        description: A string describing the meaning of the code.
    """
    
    NONE     = ('0000', 'No response')
    S16      = ('0001', '16 bit value sent')
    S32      = ('0010', '32 bit value sent')
    S16F     = ('0100', '16 bit field value sent')
    S32F     = ('0101', '32 bit field value sent')
    ERROR    = ('0111', 'The frequency converter can not run the command')
    NO_WRITE = ('1000', 'Write access: no permission to write')
    
    @classmethod
    def invalid_code(cls):
        """Returns an invalid access code."""
        return '1111'
    
    @classmethod
    def sixteen_bit_modes(cls):
        """Returns a set of the modes (members of this enum) where 
        a 16 bit parameter was accessed.
        """
        return  {cls.S16, cls.S16F}
    
    @classmethod
    def thirty_two_bit_modes(cls):
        """Returns a set of the modes (members of this enum) where 
        a 32 bit parameter was accessed.
        """
        return {cls.S32, cls.S32F}
    
    @classmethod    
    def unindexed_modes(cls):
        """Returns a set of the modes (members of this enum) where 
        an unindexed parameter was accessed.
        """
        return {cls.S16, cls.S32}
    
    @classmethod
    def indexed_modes(cls):
        """Returns a set of the modes (members of this enum) where 
        an indexed parameter was accessed.
        """
        return {cls.S16F, cls.S32F}


class CustomInt(int):
    """The arguments of __new__ methods in enums inheriting int are 
    always passed to the __new__ method of the int class, which raises 
    an error if the *description* argument is present.
    This class solves the problem by preventing *description* from 
    being passed to int.__new__.
    """
    
    def __new__(cls, value, description):
        return int.__new__(cls, value)


class IntAndDescription(CustomInt, e.Enum):
    """The same as ValueAndDescription, but members also behave like 
    ints.
    """    
                
    def __init__(self, value, description):
        self._value_ = value
        self.description = description
                    
    def __repr__(self):
        return str(self)


class ParameterError(IntAndDescription):
    """Different parameter error types.
    
    Members of this enum have the following attributes:
        value: The error code as an integer. In the case of an error, 
            the parameter value will be replaced with this number.
        description: A string describing the meaning of the error.
    """
    
    WRONG_NUM     = (  0, 'invalid parameter number')
    CANNOT_CHANGE = (  1, 'parameter cannot be changed')
    MINMAX        = (  2, 'min/max error')
    INDEX         = (  3, 'index error')
    ACCESS        = (  5, "access mode doesn't match parameter")
    OTHER         = ( 18, 'other error')
    SAVING        = (102, 'parameter is being saved to nonvolatile memory')
    # Error codes 3, 5 and 102 aren't included in the manual, but were 
    # discovered while testing the pump.
            
    
class ControlBits(IntAndDescription):
    """Numbers and descriptions of control bits.
    
    Unused control bits have been assigned values in order to 
    prevent error conditions.
    
    Members of this enum have the following attributes:
        value: The index of the bit as an integer.
        description: A string describing the effect of the bit.
    """
        
    ON            = ( 0, 'Turn or keep the pump on')
    UNUSED1       = ( 1, 'Unknown control bit: 1')
    UNUSED2       = ( 2, 'Unknown control bit: 2')
    UNUSED3       = ( 3, 'Unknown control bit: 3')
    UNUSED4       = ( 4, 'Unknown control bit: 4')
    X201          = ( 5, 'Output X201 (air cooling)') 
    SETPOINT      = ( 6, 'Enable frequency setpoint')
    RESET_ERROR   = ( 7, 'Reset error (all components)')
    STANDBY       = ( 8, 'Enable standby')
    UNUSED9       = ( 9, 'Unknown control bit: 9')
    COMMAND       = (10, 'Enable control bits')
    X1_ERROR      = (11, 'Error operation relay X1')
    X1_WARNING    = (12, 'Normal operation relay X1')
    X1_NORMAL     = (13, 'Warning relay X1')
    X202          = (14, 'Output X202 (packing pump)')
    X203          = (15, 'Output X203 (venting valve)') 
    # According to the manual, bit 10 enables bits 
    # 0, 5, 6, 7, 8, 13, 14 and 15. Either bits 11 and 12 don't need 
    # to be enabled, or the manual is wrong.


class StatusBits(IntAndDescription):
    """Numbers and descriptions of status bits.
    
    Unused status bits have been assigned values in order to 
    prevent error conditions.
    
    Members of this enum have the following attributes:
        value: The index of the bit as an integer.
        description: A string describing the effect of the bit.
    """
    
    READY           = ( 0, 'Ready for operation')
    UNUSED1         = ( 1, 'Unknown status bit: 1')
    OPERATION       = ( 2, 'Operation enabled')
    ERROR           = ( 3, 'Error condition (all components)')
    ACCELERATION    = ( 4, 'Accelerating')
    DECELERATION    = ( 5, 'Decelerating')
    SWITCH_ON_LOCK  = ( 6, 'Switch-on lock')
    TEMP_WARNING    = ( 7, 'Temperature warning')
    UNUSED8         = ( 8, 'Unknown status bit: 8')
    PARAM_CHANNEL   = ( 9, 'Parameter channel enabled')
    DETAINED        = (10, 'Normal operation detained')
    TURNING         = (11, 'Pump is turning')
    UNUSED12        = (12, 'Unknown status bit: 12')
    OVERLOAD        = (13, 'Overload warning')
    WARNING         = (14, 'Collective warning')
    PROCESS_CHANNEL = (15, 'Process channel enabled')