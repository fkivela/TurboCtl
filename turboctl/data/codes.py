"""This module defines the meaning of different codes and numbers used 
in TURBOVAC telegrams.
"""

import enum as e

class ValueAndDescription(e.Enum):
    """A superclass for enums that contains an additional attribute 
    (*description*) in addition to *value*.
    
    This enum doesn't have any instances, since it's only meant to 
    be subclassed.
    
    An instance of a subclass of this enum can be returned with
    any of the following:
    >> instance_of_enum = EnumName.NAME_OF_INSTANCE
    >> instance_of_enum = EnumName['NAME_OF_INSTANCE']
    >> instance_of_enum = EnumName(value_of_instance)
    >> instance_of_enum = EnumName(instance_of_enum)
    """
            
    def __new__(cls, value, description):
        """Setting *_value_* in __init__ raises an error because 
        *description* isn't an int.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
            
    def __repr__(self):
        return str(self)

    
#    def __init__(self, value, description):
#        """Create a new instance of this enum.
#        
#        New instances are defined inside a class definition using the 
#        following special syntax:
#            
#            class Numbers(ValueAndDescription):
#                
#                ONE = (1, 'The number one')
#                TWO = (2, 'The number two')
#                THREE = (3, 'The number three')
#        
#        Args:
#            value: Anything accepted by as a value by the Enum class.
#            description: Meant to be a string, but could be anything.
#        """
#        self._value_ = value
#        # The *value* attribute of enums is internally called 
#        # *_value_.* 
#        # The second '_' means it is not a private attribute.
#        self.description = description
        
    def __repr__(self):
        """repr(self) returns '<ParameterAccess.XYZ: 1234>' by default.
        It must be overridden so that the syntax 
        "copy = eval(repr(x))" 
        works.
        """
        return str(self)
    

class ParameterAccess(ValueAndDescription):
    """Different parameter access modes.
    
    Instances of this enum have the following attributes:
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
        """Returns a set of the modes (instances of this enum) used for 
        reading a parameter.
        """
        return {cls.R, cls.RF}

    @classmethod
    def write_modes(cls):
        """Returns a set of the modes (instances of this enum) used for 
        writing to a parameter.
        """
        return {cls.W16, cls.W32, cls.W16F, cls.W32F}
    
    @classmethod
    def sixteen_bit_modes(cls):
        """Returns a set of the modes (instances of this enum) used for 
        accessing 16 bit parameters.
        """
        return {cls.R, cls.RF, cls.W16, cls.W16F}
    
    @classmethod    
    def thirty_two_bit_modes(cls):
        """Returns a set of the modes (instances of this enum) used for 
        accessing 32 bit parameters.
        """
        return {cls.R, cls.RF, cls.W32, cls.W32F}
    
    @classmethod    
    def unindexed_modes(cls):
        """Returns a set of the modes (instances of this enum) used for 
        accessing unindexed parameters.
        """
        return {cls.R, cls.W16, cls.W32}
    
    @classmethod
    def indexed_modes(cls):
        """Returns a set of the modes (instances of this enum) used for 
        accessing indexed parameters.
        """
        return {cls.RF, cls.W16F, cls.W32F}
            
    
class ParameterResponse(ValueAndDescription):
    """Different parameter response modes.
    
    Instances of this enum have the following attributes:
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
        """Returns a set of the modes (instances of this enum) where 
        a 16 bit parameter was accessed.
        """
        return  {cls.S16, cls.S16F}
    
    @classmethod
    def thirty_two_bit_modes(cls):
        """Returns a set of the modes (instances of this enum) where 
        a 32 bit parameter was accessed.
        """
        return {cls.S32, cls.S32F}
    
    @classmethod    
    def unindexed_modes(cls):
        """Returns a set of the modes (instances of this enum) where 
        an unindexed parameter was accessed.
        """
        return {cls.S16, cls.S32}
    
    @classmethod
    def indexed_modes(cls):
        """Returns a set of the modes (instances of this enum) where 
        an indexed parameter was accessed.
        """
        return {cls.S16F, cls.S32F}


class IntAndDescription(e.IntEnum):
    """The same as ValueAndDescription, but inherits from IntEnum 
    instead of enum. This means that instances support operations 
    such as ordering, but values can only be ints.
    """
            
    def __new__(cls, value, description):
        """Setting *_value_* in __init__ raises an error because 
        *description* isn't an int.
        """
        obj = int.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
    
    def __hash__(self):
        """IntEnum is unhashable for some reason, so __hash__ 
        has to be defined manually.
        The implementation is identical with the hash function of the
        Enum class."""
        return hash(self._name_)
                
    def __repr__(self):
        return str(self)


class ParameterError(IntAndDescription):
    """Different parameter error types.
    
    Instances of this enum have the following attributes:
        value: The error code as an integer. In the case of an error, 
            the parameter value will be replaced with this number.
        description: A string describing the meaning of the error.
    """
    
    WRONG_NUM     = (0, 'impermissible parameter number')
    CANNOT_CHANGE = (1, 'parameter cannot be changed')
    MINMAX        = (2, 'min./max. restriction')
    OTHER         = (18, 'all other errors')
            
    
class ControlBits(IntAndDescription):
    """Numbers and descriptions of control bits.
    
    Unused control bits have been assigned values in order to 
    prevent error conditions.
    
    Instances of this enum have the following attributes:
        value: The index of the bit as an integer.
        description: A string describing the effect of the bit.
    """
        
    # TODO: Check these
    START_STOP    = ( 0, 'Start/stop')
    UNUSED1       = ( 1, 'Control bit 1 (not assigned)')
    UNUSED2       = ( 2, 'Control bit 2 (not assigned)')
    UNUSED3       = ( 3, 'Control bit 3 (not assigned)')
    UNUSED4       = ( 4, 'Control bit 4 (not assigned)')
    AIR_COOLING   = ( 5, 'Output X201 (air cooling)') 
    FREQ_SETPOINT = ( 6, 'Set frequency setpoint')
    RESET_ERROR   = ( 7, 'Reset error (all components)')
    STANDBY       = ( 8, 'Enable standby')
    UNUSED9       = ( 9, 'Control bit 9 (not assigned)')
    COMMAND       = (10, 'Enable control bits 0, 5, 6, 7, 8, 13, 14, 15')
    X1_ERROR      = (11, 'Error operation relay X1')
    X1_WARNING    = (12, 'Normal operation relay X1')
    X1_NORMAL     = (13, 'Warning relay X1')
    PP_RELAY      = (14, 'Output X202 (packing pump)') 
    VENTING       = (15, 'Output X203 (venting valve)') 


class StatusBits(IntAndDescription):
    """Numbers and descriptions of status bits.
    
    Unused status bits have been assigned values in order to 
    prevent error conditions.
    
    Instances of this enum have the following attributes:
        value: The index of the bit as an integer.
        description: A string describing the effect of the bit.
    """
    
    READY           = (0, 'Ready for operation')
    UNUSED1         = (1, 'Status bit 1 (not assigned)')
    OPERATION       = (2, 'Operation enabled')
    ERROR           = (3, 'Error condition (all components)')
    ACCELERATION    = (4, 'Accelerating')
    DECELERATION    = (5, 'Decelerating')
    SWITCH_ON_LOCK  = (6, 'Switch-on lock')
    TEMP_WARNING    = (7, 'Temperature warning')
    UNUSED8         = (8, 'Status bit 8 (not assigned)')
    PARAM_CHANNEL   = (9, 'Parameter channel enabled')
    DETAINED        = (10, 'Normal operation detained')
    TURNING         = (11, 'Pump is turning')
    UNUSED12        = (12, 'Status bit 12 (not assigned)')
    OVERLOAD        = (13, 'Overload warning')
    WARNING         = (14, 'Collective warning')
    PROCESS_CHANNEL = (15, 'Process channel enabled')