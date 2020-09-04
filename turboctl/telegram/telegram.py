"""This module defines classes for creating, representing and reading
telegrams which are used to communicate with the pump.
    
..
    Aliases for Sphinx.

.. |Uint| replace:: :class:`~turboctl.telegram.datatypes.Uint`
.. |Sint| replace:: :class:`~turboctl.telegram.datatypes.Sint`
.. |Float| replace:: :class:`~turboctl.telegram.datatypes.Float`
.. |Bin| replace:: :class:`~turboctl.telegram.datatypes.Bin`
"""

from dataclasses import dataclass

from turboctl.telegram.codes import (
    ControlBits, StatusBits, get_parameter_code, get_parameter_mode,
    ParameterResponse, ParameterError
)
from turboctl.telegram.datatypes import (Data, Uint, Sint, Bin)
from turboctl.telegram.parser import PARAMETERS


@dataclass
class Telegram:
    """A simple dataclass that represents a telegram sent to or from the pump.
    
    This class is cumbersome to initialize directly, since the values of all 
    attributes must be given as arguments. Instances should instead be 
    created with the :class:`TelegramBuilder` class.
    
    The Leybold TURBOVAC i/iX vacuum pump communicates with a computer 
    via its RS 232 or RS 485 serial port or a USB port using telegrams 
    of 24 bytes. The general structure of the telegrams follows the 
    USS protocol.
    
    Each byte consists of a start bit (0), 8 data bits, an even 
    parity bit (1 if there are an even number of 1s in the data 
    bits, 0 otherwise) and an ending bit (1). However, only the data 
    bits are included in the bytes objects that represent telegrams;
    the `serial <https://pyserial.readthedocs.io/en/latest/>`_ 
    module automatically adds the other bits. 
    
    In the TURBOVAC manual, the data bits in a byte are indexed as 
    [7,6,5,4,3,2,1,0] (i.e. according to the power of 2 they
    represent), but this class uses the convention [0,1,2,3,4,5,6,7], 
    because it corresponds to the indices of a Python list.
    
    The functions and values of the different bytes in a telegram 
    are detailed below. Each list entry contains the name of the  
    :class:`Telegram` object attribute (if any) that represents 
    the value associated with the entry.
    
    Unless otherwise noted, all bytes have a default value of 0.
        
    **Byte 0:** STX (start of text). Always 2.
    
    **Byte 1:** LGE (telegram length). 
    Excludes bytes 0 and 1, and thus always has a value of 22.
    
    **Byte 2:** ADR (address). 
    With a RS485 port this denotes the slave node number (0-31).
    Reading or changing this byte is not currently supported by this 
    class.
    
    **Bytes 3-4:** PKE (parameter number and type of access). 
    A 16 bit block:
        
        - Bits 0-3: 
            Type of parameter access or response. 
            This is a 4 bit code indicating e.g. whether a parameter 
            should be read from or written to.
            Valid codes are detailed in the :mod:`~turboctl.telegram.codes` 
            module.
            
            Attribute: :attr:`parameter_code`.
            
        - Bit 4: 
            Always 0.
        
        - Bits 5-15:
            The number of the parameter to be accessed.
            
            Attribute: :attr:`parameter_number`.
    
    **Byte 5:** - (reserved). Always 0.
    
    **Byte 6:** IND (parameter index). 
    If the requested parameter is indexed, this specifies the number 
    of the requested index.
    
    Attribute: :attr:`parameter_index`.

    **Bytes 7-10:** PWE (parameter value). 
    This block contains a parameter value that is written to or read 
    from the pump. If the pump tries to access a parameter but fails, the 
    reply will contain an error code in this block.
    
    Attribute: :attr:`parameter_value`.

    **Bytes 11-12:** PZD1 (status and control bits).
    16 bits each corresponding to a single setting or command which 
    can be turned on by setting the bit to 1.
    In a reply from the pump these correspond to status 
    conditions affecting the pump instead of commands.
    
    Attribute: :attr:`flag_bits`.

    **Bytes 13-14:** PZD2 (current rotor frequency). 
    Rotor frequency in Hz; the same as parameter 3.
    Included in all replies, and can be included in queries to define 
    a setpoint for the frequency. (This only works if the setpoint is 
    enabled through the control bits, and overrides the setpoint 
    defined in parameter 24).
    
    Attribute: :attr:`frequency`.

    **Bytes 15-16:** PZD3 (current frequency converter temperature). 
    Frequency converter temperature in °C, included in all replies. 
    Same as parameter 11.
    
    Attribute: :attr:`temperature`.
    
    **Bytes 17-18**: PZD4 (current motor current). 
    Motor current in 0.1 A, included in all replies. 
    Same as parameter 5.
    
    Attribute: :attr:`current`.

    **Bytes 19-20:** - (reserved). Always 0.

    **Bytes 21-22:** PZD6 (current intermediate circuit voltage).
    Intermediate circuit voltage in V, included in all replies.
    Same as parameter 4.
    
    Attribute: :attr:`voltage`

    **Byte 23:** BCC (byte block check): 
    A checksum computed using the following algorithm:
    ::
        
        checksum = bytes_[0]
        for byte in bytes_[1:23]:
            checksum = checksum ^ byte_
                
    where ``^`` is the exclusive or (XOR) operator.    
    """
    # The manual uses "stator frequency (=P3)" instead of "rotor frequency",
    # but the entry for parameter 3 uses the word "rotor", which seems to be
    # the correct version since the rotor is the moving part.
    # The manual also lists the unit of voltage as 0.1 V, but the correct unit
    # seems to be V.
    
    # :mod:`serial` links to a weird place in pySerial's documentation, so a
    # manual hyperlonk to the front page was used instead.
    
    parameter_code: Bin
    """The parameter access or response code as a 4-bit |Bin|."""
    
    parameter_number: Uint
    """The parameter number as an 11-bit |Uint|."""
    
    parameter_index: Uint
    """The parameter index as a 8-bit |Uint|."""
    
    parameter_value: Data
    """The parameter value. This attribute is always a 32-bit instance of a 
    subclass of :class:`~turboctl.telegram.datatypes.Data`, 
    but the exact type depends on the parameter.
    """
    
    flag_bits: Bin
    """The control or status bits as a 32-bit |Bin|."""
    
    frequency: Uint
    """The frequency as a 32-bit |Uint|."""
    
    temperature: Sint
    """The temperature as a 32-bit |Sint|."""
    
    current: Uint
    """The current as a 32-bit |Uint|."""
    
    voltage: Uint
    """The voltage as a 32-bit |Uint|."""
    
    LENGTH = 24
    """The length of a telegram in bytes."""
    
    def __bytes__(self):
        """Return the telegram as a :class:`bytes` object.
        
        The checksum is computed automatically and added to the end.
        """
        bytes_ = bytes(
            Uint(2, 8) +
            Uint(22, 8) +
            Uint(0, 8) +
            self.parameter_code + 
            Bin('0') + 
            self.parameter_number + 
            Uint(0, 8) + 
            self.parameter_index + 
            self.parameter_value +
            self.flag_bits[::-1] +    
            self.frequency +
            self.temperature +
            self.current + 
            Uint(0, 16) +
            self.voltage
        )
        return bytes_ + bytes([checksum(bytes_)])


class TelegramBuilder:
    """
    TelegramBuilder(parameters=PARAMETERS)
    
    This class can be used to easily construct instances of the 
    :class:`Telegram` class.
    
    Here is an example of how to use this class:     
    ::
        
        telegram = (TelegramBuilder().set_parameter_mode('write')
                                     .set_paramerer_number(1)
                                     .set_parameter_index(2)
                                     .set_parameter_value(3)
                                     .build())
        
    The above creates a telegram which writes the value 3 to parameter 1,
    index 2. Note that this is just an example of the syntax; parameter 1
    isn't actually indexed.
   
    Attributes which aren't explicitly set to a value with a setter method are 
    set to zero when the telegram is created.
    Trying to set an attribute to an invalid value results in a
    :class:`ValueError` or a :class:`TypeError`.
        
    A telegram can also be created from a :class:`bytes` object:
    ::
        
        telegram = TelegramBuilder().from_bytes(bytes_).build()
        
    Attributes:
        parameters: A :class:`dict` of
            :class:`~turboctl.telegram.parser.Parameter` objects, with
            parameter numbers as keys.
            The default value is :const:`~turboctl.telegram.parser.PARAMETERS`,
            but non-default parameter sets can be used for testing purposes.
    """
    # The first line of the docstring overrides the default signature generated
    # by Sphinx, and thus prevents PARAMETERS from being expanded.
    
    def __init__(self, parameters=PARAMETERS):
        """
        __init__(parameters=PARAMETERS)
        
        Initialize a new :class:`TelegramBuilder`.
        
        Args:
            parameters: The object to be assigned to :attr:`parameters`.
        """
        self.parameters = parameters
        
        # Keyword arguments used to create a telegram.
        self._kwargs = {
            'parameter_code':   Bin(4 * '0', bits=4),
            'parameter_number': Uint(0,  bits=11),
            'parameter_index':  Uint(0,  bits=8),
            'parameter_value':  Uint(0,  bits=32),
            'flag_bits':        Bin(16 * '0', bits=16),
            'frequency':        Uint(0,  bits=16),
            'temperature':      Sint(0,  bits=16),
            'current':          Uint(0,  bits=16,),
            'voltage':          Uint(0,  bits=16),
        }
        # parameter_value and parameter_mode are special cases.
        # These variables store the values given by the user, and the final
        # values used as arguments are only determined when the telegram is
        # created.
        
        # __init__ and set_parameter_value set this to a int or a float,
        # and from_bytes to a bytes object.
        self._parameter_value = 0
        
        # __init__ and set_parameter_mode set this to a string, and from_bytes
        # to a Bin object.
        self._parameter_mode = 'none'

    def from_bytes(self, bytes_):
        """Read the contents of the telegram from a :class:`bytes` object.
        
        The type of :attr:`parameter_value <Telegram.parameter_value>`
        depends on :attr:`parameter_number <Telegram.parameter_number>`,
        and is assigned automatically. If *bytes_* contains a parameter 
        number that doesn't exist, a :class:`ValueError` is raised.
        
        If the parameter isn't accessed (i.e. the parameter mode is set to 
        ``'none'`` or code to ``'0000'``), invalid parameter numbers, such as
        the default value of 0, are permitted.
        In that case, the parameter type is set to
        :class:`~turboctl.telegram.datatypes.Uint`.
        
        Note that this isn't a class method; a :class:`TelegramBuilder` must
        first be initialized normally with :meth:`__init__`, after which
        this method may be called.
        
        Raises:
            ValueError: If *bytes_* doesn't represent a valid telegram.
        """
        self._check_valid_telegram(bytes_)
        
        code_and_number_bits = Bin(bytes_[3:5])    
        self._kwargs = {
            'parameter_number':     Uint(code_and_number_bits[5:16]),
            'parameter_index':      Uint(bytes_[6]),
            'flag_bits':            Bin(bytes_[11:13])[::-1],
            'frequency':            Uint(bytes_[13:15]),
            'temperature':          Sint(bytes_[15:17]),
            'current':              Uint(bytes_[17:19]),
            'voltage':              Uint(bytes_[21:23])        
        }
        
        self._parameter_value = bytes_[7:11]
        self._parameter_mode = Bin(code_and_number_bits[0:4])

        return self
        
    @staticmethod
    def _check_valid_telegram(bytes_):
        """Raise a ValueError if bytes_ doesn't represent a valid Telegram.
        """
        
        if len(bytes_) != 24:
            raise ValueError(f'len(bytes_) should be 24, not {len(bytes_)}')
        
        if bytes_[0] != 2:
            raise ValueError(f'bytes_[0] should be 2, not {bytes_[0]}')
            
        if bytes_[1] != 22:
            raise ValueError(f'bytes_[1] should be 22, not {bytes_[1]}')
            
        cs = checksum(bytes_[0:23])
        if cs != bytes_[23]:
            raise ValueError(f'bytes_[23] (the checksum) should be '
                             f'{cs}, not {bytes_[23]}')
    
    def set_parameter_mode(self, value: str):
        """Set the parameter access or response mode to one of the following:
            
            Access modes:
                - ``'none'``
                - ``'read'``
                - ``'write'``
                
            Response modes:
                - ``'none'``
                - ``'response'``
                - ``'error'``
                - ``'no write'``
                
            The parameter access or response code is determined automatically
            based on the parameter mode and the parameter number. 
            """
        self._parameter_mode = value
        return self
    
    def set_parameter_number(self, value: int):
        """Set the parameter number.
        
        Raises:
            ValueError: If there isn't a parameter with the specified number.
        """
        self._kwargs['parameter_number'] = Uint(value, 11)
        return self
        
    def set_parameter_index(self, value: int):
        """Set the parameter index."""
        self._kwargs['parameter_index'] = Uint(value, bits=8)
        return self
    
    def set_parameter_value(self, value):
        """Set the parameter value.
        
        The type of *value* depends on the type of the parameter.
        This method can also be used to set the error code; if
        :meth:`set_parameter_mode` is called to set the parameter mode to
        ``'error'``, the parameter value is always interpreted as an |Uint|
        error code regardless of parameter number or type.
        """
        self._parameter_value = value
        return self
        
    def set_flag_bits(self, bits):
        """Set the control or status bits.
        
        *bits* should be an iterable of those 
        :class:`~turboctl.telegram.codes.ControlBits` or 
        :class:`~turboctl.telegram.codes.StatusBits` members that should be 
        included in the telegram.
        """
        bitlist = 16 * ['0']
        for bit in bits:
            bitlist[bit.value] = '1'
        string = ''.join(bitlist)
        self._kwargs['flag_bits'] = Bin(string, bits=16)
        return self
    
    def set_frequency(self, value: int):
        """Set the frequency."""
        self._kwargs['frequency'] = Uint(value, bits=16)
        return self
    
    def set_temperature(self, value: int):
        """Set the temperature.
        
        Note that *value* can also be negative.
        """
        self._kwargs['temperature'] = Sint(value, bits=16)
        return self
    
    def set_current(self, value):
        """Set the current."""
        self._kwargs['current'] = Uint(value, bits=16)
        return self
    
    def set_voltage(self, value):
        """Set the voltage."""
        self._kwargs['voltage'] = Uint(value, bits=16)
        return self
        
    def build(self, type_='query'):
        """Build and return a :class:`Telegram` object.
        
        Args:
            type_: ``query`` if the telegram represents a message to the pump, 
                ``reply`` if it represents a message from the pump.
        
        Raises:
            :class:`ValueError` or :class:`TypeError`: If a telegram cannot
                be created with the specified attributes.
        """
        
        # Make sure type_ is valid to avoid bugs caused by a misspelled
        # argument.
        if type_ not in ['query', 'reply']:
            raise ValueError(f'invalid type_: {type_}')
        
        # Determine parameter access code.
        
        none_code = '0000'
        error_code = ParameterResponse.ERROR.value
        
        # __init__() and set_parameter_mode set self._parameter_mode to a
        # string, while from_bytes() sets it to a Bin object.
        mode_is_none = self._parameter_mode in ['none', Bin(none_code)]
        mode_is_error = (type_ == 'reply' and
                      self._parameter_mode in ['error', Bin(error_code)])
        
        if mode_is_none:
            self._kwargs['parameter_code'] = Bin(none_code)
        elif mode_is_error:
            self._kwargs['parameter_code'] = Bin(error_code)
        else:
            # parameter_number must be valid if the access mode isn't 'none'
            # or 'error'.
            number = self._kwargs['parameter_number'].value
            try:
                parameter = self.parameters[number]
            except KeyError:
                raise ValueError(f'invalid parameter number: {number}') 

            if isinstance(self._parameter_mode, Bin):
                # If this object was created from a Bin object,
                # self._parameter_mode will be a bytes object.
                self._kwargs['parameter_code'] = self._parameter_mode
            else:
                code = get_parameter_code(
                    type_,  self._parameter_mode,
                    bool(parameter.indices), parameter.bits
                ).value
                self._kwargs['parameter_code'] = Bin(code)

        # Determine parameter value.
        
        if mode_is_none or mode_is_error:
            # If the mode is 'none', there is no parameter access and the
            # datatype doesn't matter.
            # If the mode is 'error', the parameter value is replaced by an
            # Uint error code.
            datatype = Uint
        else:
            datatype = parameter.datatype
                
        if isinstance(self._parameter_value, bytes):
            # If self._parameter_value was set by from_bytes(),
            # self._parameter_value will be a bytes object and bits cannot be
            # specified.
            self._kwargs['parameter_value'] = datatype(self._parameter_value)
        else:
            # If _parameter_value was specified by the user, its type should
            # match the type of the parameter.
            # The default value of 0 is accepted by all parameter types.
            self._kwargs['parameter_value'] = datatype(self._parameter_value,
                                                       bits=32)

        return Telegram(**self._kwargs)


class TelegramReader:
    """This class can be used to read the data of a telegram in a more
    user-friendly way. This means the returned values are Python built-ins 
    instead of the custom datatypes used by the :class:`Telegram` class, and 
    *parameter_code* is automatically converted to a human-readable value.
        
    Attributes:        
        type:
            ``'query'`` for telegrams to the pump, ``'reply'`` for telegrams
            from the pump.
            
        telegram:
            The :class:`Telegram` object that is read.
    """
    
    def __init__(self, telegram, type_='reply'):
        """Initialize a new :class:`TelegramReader`.
        
        Args:
            telegram: The :class:`Telegram` to be read.
            type_: ``query`` if the telegram represents a message to the pump, 
                ``reply`` if it represents a message from the pump.
                
        Raises:
            :class:`ValueError`: If *type_* has an invalid value.
        """
        
        # Make sure type_ is valid to avoid bugs caused by a misspelled
        # argument.
        if type_ not in ['query', 'reply']:
            raise ValueError(f'invalid type_: {type_}')
        
        self.type = type_
        self.telegram = telegram
        
    def __repr__(self):
        """Return an exact string respresentation of this object.
        
        The returned string can be evaluated to create a copy of this object.
        The format is ``ClassName(telegram=<telegram>, type=<type>)``.
        """
        return type(self).__name__ + (
            f'(telegram={self.telegram}, type={repr(self.type)})')

        
    def __str__(self):
        """Return an easily readable string representation of this object.
        
        The returned string shows the values of both the attributes and the
        read-only properties of this object, and cannot thus be passed to
        :func:`eval` without an raising error. 
        
        The format is
        
        .. highlight:: none
        
        ::
        
            ClassName(
                telegram=<telegram>,
                type=<type>,
                parameter_mode=<parameter_mode>,
                ...
            )
            
        .. highlight:: default
        """
        # str(self.parameter_error) must be used instead of
        # self.parameter_error, because the latter is displayed as just a
        # number instead of its __repr__ or __str__. This is probably caused by
        # the fact that that ParameterError inherits int.
        return type(self).__name__ + ('(\n'
            f'    telegram={self.telegram},\n'
            f'    type={repr(self.type)},\n'
            f'    parameter_mode={repr(self.parameter_mode)},\n'
            f'    parameter_number={self.parameter_number},\n'
            f'    parameter_index={self.parameter_index},\n'
            f'    parameter_value={self.parameter_value},\n'
            f'    parameter_error={str(self.parameter_error)},\n'
            f'    flag_bits={self.flag_bits},\n'
            f'    frequency={self.frequency},\n'
            f'    temperature={self.temperature},\n'
            f'    current={self.current},\n'
            f'    voltage={self.voltage}\n'
            ')'
        )

    @property
    def parameter_mode(self):
        """Return the parameter mode.
        
        This method is the reverse of
        :meth:`TelegramBuilder.set_parameter_mode`: it automatically converts
        a parameter access or response code to a human-readable string.
        
        Raises:
            ValueError: If the parameter code of the telegram is invalid.
        """
        code = self.telegram.parameter_code.value
        return get_parameter_mode(self.type, code)
        
    @property
    def parameter_number(self):
        """Return the parameter number."""
        return self.telegram.parameter_number.value
        
    @property
    def parameter_index(self):
        """Return the parameter index."""
        return self.telegram.parameter_index.value
    
    @property
    def parameter_value(self):
        """Return the parameter value."""
        return self.telegram.parameter_value.value
    
    @property
    def parameter_error(self):
        """Return the parameter error.
        
        Returns:
            A member of the :class:`~turboctl.telegram.codes.ParameterError` 
            enum, or ``None``, if :attr:`parameter_mode` isn't ``'error'``.
            
        Raises:
            ValueError: If the error number isn't valid.
        """
        # The error code could be easily read from parameter_value
        # (which could be changed to always give the value as an Uint if
        # parameter_mode is 'error'). This property mostly exists to aid in
        # debugging; __str__ displays its value, which makes it easy to see
        # which error has occurred without looking up the meaning of the error
        # code.
        # There's no equivalent TelegramBuilder.set_error_code method, because
        # it isn't really needed, and adding that bit of symmetry wouldn't be
        # worth the increased complexity.

        if self.parameter_mode != 'error':
            return None
        
        number = Uint(self.telegram.parameter_value).value
        try:
            return ParameterError(number)
        except KeyError:
            raise ValueError(f'invalid parameter error number: {number}')
    
    @property
    def flag_bits(self):
        """Return the control or status bits as a list of those
        :class:`~turboctl.telegram.codes.StatusBits` or
        :class:`~turboctl.telegram.codes.ControlBits` members that are set to 
        1 in the telegram.
        """
        bits = self.telegram.flag_bits.value
        enum = ControlBits if self.type == 'query' else StatusBits
        return [enum(i) for i, char in enumerate(bits) if char == '1']
    
    @property
    def frequency(self):
        """Return the frequency."""
        return self.telegram.frequency.value
    
    @property
    def temperature(self):
        """Return the temperature."""
        return self.telegram.temperature.value
    
    @property
    def current(self):
        """Return the current."""
        return self.telegram.current.value
    
    @property
    def voltage(self):
        """Return the voltage."""
        return self.telegram.voltage.value
    

def checksum(bytes_: bytes) -> int:    
    """Compute a checksum for a telegram."""
    checksum = 0
    for i in bytes_:
        checksum = checksum ^ i  
    return checksum
