"""This module defines classes for creating, representing and reading
telegrams which are used to communicate with the pump.

\TODO: 
    - Add the error code property to TelegramReader.
    - Redirect the link to the serial module to the front page.
    - Add a list of telegram attributes with their types.
    - The docstring of TelegramBuilder.__init__ generates a weird indent
    - The links to Status/ControlBits don't work'
    
..
    Aliases for Sphinx.

.. |Uint| replace:: :class:`~turboctl.telegram.datatypes.Uint`
.. |Sint| replace:: :class:`~turboctl.telegram.datatypes.Sint`
.. |Float| replace:: :class:`~turboctl.telegram.datatypes.Float`
.. |Bin| replace:: :class:`~turboctl.telegram.datatypes.Bin`
"""

from dataclasses import dataclass

from turboctl.telegram.codes import (ControlBits, StatusBits, 
    get_parameter_code, get_parameter_mode)
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
    the :mod:`serial` module automatically adds the other bits. 
    
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
    from the pump.
    
    Attribute: :attr:`parameter_value`.

    **Bytes 11-12:** PZD1 (status and control bits).
    16 bits each corresponding to a single setting or command which 
    can be turned on by setting the bit to 1.
    In a reply from the pump these correspond to status 
    conditions affecting the pump instead of commands.
    
    Attribute: :attr:`flag_bits`.

    **Bytes 13-14:** PZD2 (current stator frequency). 
    Stator frequency in Hz; the same as parameter 3.
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
    Intermediate circuit voltage in 0.1 V, included in all replies.
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
            self.data.voltage
        )
        return bytes_ + self._get_checksum(bytes_)


class TelegramBuilder:
    """This class can be used to easily construct instances of the 
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
    """
    
    
    def __init__(self):
        """Initialize a new :class:`TelegramBuilder`."""
        
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
        self._parameter_value = None
        self._parameter_mode = None
        
    
    @classmethod
    def from_bytes(cls, bytes_):
        """Read the contents of the telegram from a :class:`bytes` object."""
        cls._check_valid_telegram(bytes_)

        self = cls.__new__()
        code_and_number_bits = Bin(bytes_[3:5])    
        self.kwargs = {
            'parameter_code':       Bin(code_and_number_bits[0:4]),
            'parameter_number':     Uint(code_and_number_bits[5:16]),
            'parameter_index':      Uint(bytes_[6]),
            # parameter_value is uint by default.
            # Use TelegramReader to read it as the correct data type. 
            'parameter_value':      Uint(bytes_[7:11]),
            'flag_bits':            Bin(bytes_[11:13][::-1]),
            'frequency':            Uint(bytes_[13:15]),
            'temperature':          Sint(bytes_[15:17]),
            'current':              Uint(bytes_[17:19]),
            'voltage':              Uint(bytes_[21:23])        
        }
        return self
        
    @classmethod
    def _check_valid_telegram(cls, bytes_):
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
        if not value in PARAMETERS:
            raise ValueError('parameter does not exist')
        self.kwargs['parameter_number'] = Uint(value, 11)
        return self
        
    def set_parameter_index(self, value: int):
        """Set the parameter index."""
        self.kwargs['parameter_index'] = Uint(value, bits=8)
        return self
    
    def set_parameter_value(self, value):
        """Set the parameter value.
        
        The type of *value* depends on the type of the parameter.
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
        self.kwargs['flag_bits'] = Bin([bit.value for bit in bits], bits=16)
        return self
    
    def set_frequency(self, value: int):
        """Set the frequency."""
        self.kwargs['frequency'] = Uint(value, bits=8)
        return self
    
    def set_temperature(self, value: int):
        """Set the temperature.
        
        Note that *value* can also be negative.
        """
        self.kwargs['temperature'] = Sint(value, bits=8)
        return self
    
    def set_current(self, value):
        """Set the current."""
        self.kwargs['current'] = Uint(value, bits=8)
        return self
    
    def set_voltage(self, value):
        """Set the voltage."""
        self.kwargs['voltage'] = Uint(value, bits=8)
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
        
        # If _parameter_value is 0, there is no need to find the correct
        # data type, since all data types represent 0 in the same way.
        if self._parameter_value or self._parameter_mode:
            try:
                parameter_number = self.kwargs['parameter_number'].value
                parameter = PARAMETERS[parameter_number]
            except KeyError:
                raise ValueError(
                    f'invalid parameter number: {parameter_number}')
        
        # The type of parameter_value depends on the parameter.
        if self._parameter_value:
            datatype = parameter.type_
            self.kwargs['parameter_value'] = datatype(self._parameter_value)
            
        # The right parameter code is selected automatically based on
        # parameter_mode and the parameter.
        if self._parameter_mode:
            indexed = bool(parameter.indices)
            bits = parameter.bits
            code = get_parameter_code(
                type_,  self._parameter_mode, indexed, bits)
            self.kwargs['parameter_code'] = Bin(code, bits=4)
            
        return Telegram(**self.kwargs)


class TelegramReader:
    """This class can be used to read the data of a telegram in a more
    user-friendly way. This means the returned values are Python built-ins 
    instead of the custom datatypes used by the :class:`Telegram` class, and 
    *parameter_code* and *parameter_value* are automatically converted to 
    human-readable values.    
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
        return self.telegram.parameter_index.value
    
    @property
    def flag_bits(self):
        """Return the control or status bits as an iterable those
        :class:`codes.StatusBits` or :class:`codes.ControlBits` members that 
        are set to 1 in the telegram.
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
    

@staticmethod
def checksum(bytes_):        
    """Compute a checksum for a telegram."""
    checksum = 0
    for i in bytes_:
        checksum = checksum ^ i  
    return checksum
