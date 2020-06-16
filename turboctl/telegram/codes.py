"""This module defines enums for the different codes and numbers used 
in TURBOVAC telegrams.

Members of enums can be accessed with any of the following syntaxes: 
    
    >>> member = EnumName.MEMBER_NAME
    >>> member = EnumName['MEMBER_NAME']
    >>> member = EnumName(member_value)
    >>> member = EnumName(member)
    
    TODO: 
        - ParameterCode.__repr__ doesn't show up in the docs.
        - Classes that inherit both from CustomInt and Enum don't show up in
          the docs.
        - Explain the meaning of these enums a bit (e.g. parameter errors 
          represent error codes that are sent when a parameter can't be 
          accessed).
"""

import enum as e


class ParameterCode(e.Enum):
    """A superclass for parameter access and response codes.
    
    This enum doesn't have any members, since it's only meant to 
    be subclassed. Members of subclasses have the following fields:
                
        ``value``
            The code (a 4-character :class:`str`).
        
        ``mode``
            A string that groups the codes together by function 
            (e.g. ``read`` for all read modes).
        
        ``indexed``
            ``True`` if this mode can be only used for indexed parameters, 
            ``False`` if it can only be used for unindexed parameters, 
            and ``...`` if it can be used for both.
        
        ``bits``
            ``16`` or ``32`` if the mode can only be used for 16 or 32 bit 
            parameters, and ``...`` if it can be used for both.
        
        ``description``: 
            A verbal description of the meaning of the code.
    """
        
    def __new__(cls, value, mode, indexed, bits, description):
        """``__new__`` is defined instead of ``__init__``, because setting 
        *_value_* in ``__init__`` prevents the syntax 
        :code:`member = EnumName(value_of_member)` from working.
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
    

class ParameterAccess(ParameterCode):
    """Different parameter access modes."""
    
#   Name     Value   Mode    Indexed  Bits  Description
    NONE = ('0000', 'none',  ...,     ..., 'No access')
    R    = ('0001', 'read',  False,   ..., 'Read a value')
    W16  = ('0010', 'write', False,    16, 'Write a 16 bit value')
    W32  = ('0011', 'write', False,    32, 'Write a 32 bit value')
    RF   = ('0110', 'read',  True,    ..., 'Read a field value')
    W16F = ('0111', 'write', True,     16, 'Write a 16 bit field value')
    W32F = ('1000', 'write', True,     32, 'Write a 32 bit field value')            

    
class ParameterResponse(ParameterCode):
    """Different parameter response modes."""
    
#   Name         Value   Mode       Indexed Bits  Description
    NONE     = ('0000', 'none',     ...,    ..., 'No response')
    S16      = ('0001', 'response', False,   16, '16 bit value sent')
    S32      = ('0010', 'response', False,   32, '32 bit value sent')
    S16F     = ('0100', 'response', True,    16, '16 bit field value sent')
    S32F     = ('0101', 'response', True,    32, '32 bit field value sent')
    ERROR    = ('0111', 'error',    ...,    ..., 'Cannot run command')
    NO_WRITE = ('1000', 'no write', ...,    ..., 'No write access')


def get_parameter_code(telegram_type, mode, indexed, bits):
    """Return the parameter code that matches the arguments.
    
    *telegram_type* is ``'query'`` for messages to the pump and ``'reply'`` for
    messages from the pump.
    
    Raises:
         :class:`ValueError`: If the number of matching members isn't 1,
             or if *telegram_type* is invalid.
    """
    
    if telegram_type == 'query':
        enum = ParameterAccess
    elif telegram_type == 'reply':
        enum = ParameterResponse
    else:
        raise ValueError(f'invalid telegram_type: {telegram_type}')
        
    results = []
        
    for member in enum:    
        mode_match = member.mode == mode
        index_match = member.indexed in [indexed, ...]
        bits_match = member.bits in [bits, ...]
        
        if mode_match and index_match and bits_match:
            results.append(member)
            
    if len(results) == 0:
        raise ValueError('no matching codes')
    
    if len(results) > 1:
        raise ValueError('several matching codes')
        
    return results[0]


def get_parameter_mode(telegram_type, code):
    """Return the parameter mode that matches the arguments.
    
    *telegram_type* is ``'query'`` for messages to the pump and ``'reply'`` for
    messages from the pump.
    """
    
    if telegram_type == 'query':
        enum = ParameterAccess
    elif telegram_type == 'reply':
        enum = ParameterResponse
    else:
        raise ValueError(f'invalid telegram_type: {telegram_type}')
        
    member = enum(code)
    return member.mode    
    
    
class CustomInt(int):
    """A custom superclass for enums that inherit :class:`int` while having
    members with multiple fields.
    """
    
    def __new__(cls, value, *args, **kwargs):
        """The arguments of ``__new__`` methods in enums inheriting :class:`int` 
        are always passed to :meth:`int.__new__`, which often raises 
        an error if there are multiple arguments present.
        This class solves the problem by only passing the first argument to 
        :meth:`int.__new__`.
        """
        return int.__new__(cls, value)


# Define error classes for ParameterError members.
class ParameterException(Exception): pass

class WrongNumError(ParameterException): pass
class CannotChangeError(ParameterException): pass
class MinMaxError(ParameterException): pass
class ParameterIndexError(ParameterException): pass
class AccessError(ParameterException): pass
class OtherError(ParameterException): pass
class SavingError(ParameterException): pass


class ParameterError(CustomInt, e.Enum):
    """Different parameter error types.
    
    This class also inherits :class:`CustomInt`, which means its members can
    e.g. be easily ordered. 
    
    Members of this enum have the following fields:
    
    value: The number of the error (:class:`int`).
    exception: An exception class that can be raised.
    description: A verbal description of the meaning of the error.
    """
    
    def __init__(self, value, description, exception):
        self._value_ = value
        self.description = description
        self.exception = exception
                        
    WRONG_NUM =     (  0, 'invalid parameter number',    WrongNumError)
    CANNOT_CHANGE = (  1, 'parameter cannot be changed', CannotChangeError)
    MINMAX        = (  2, 'min/max error',               MinMaxError)
    INDEX         = (  3, 'index error',                 ParameterIndexError)
    ACCESS        = (  5, "access mode doesn't match "
                          "parameter",                   AccessError)
    OTHER         = ( 18, 'other error',                 OtherError)
    SAVING        = (102, 'parameter is being saved to '
                          'nonvolatile memory',          SavingError)
    # Error codes 3, 5 and 102 aren't included in the manual, but were 
    # discovered while testing the pump.
    
    
class FlagBits(CustomInt, e.Enum):
    """A superclass for control and status bits.
    
    This class is otherwise similar to :class:`ParameterError`, but it doesn't 
    have any members as it's a superclass, and the members of its subclasses 
    but lack the *exception* field. 
    """

    def __init__(self, value, description):
        """Lorem ipsum."""
        self._value_ = value
        self.description = description


class ControlBits(FlagBits):
    """Different control bits.
    
    Unused control bits have been assigned values in order to 
    prevent errors in the program.
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


class StatusBits(FlagBits):
    """Different status bits.
    
    Unused status bits have been assigned values in order to 
    prevent errors in the program.
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