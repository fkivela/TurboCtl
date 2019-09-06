"""This module defines the Telegram class, which can used to 
communicate with a Leybold TURBOVAC i/iX vacuum pump.        
"""
from __future__ import annotations
from typing import Union
from collections import namedtuple, OrderedDict

from .numtypes import TurboNum, Uint, Sint, Bin

class Telegram:    
    """A telegram for communicating with a Leybold TURBOVAC vacuum 
    pump.
    
    Commands are added to a Telegram object by setting its attributes 
    to desired values. A Telegram can be converted into a bytes object 
    through its to_bytes() method, and this object can be sent to the 
    pump with the serial module. A response from the pump may be 
    turned into a Telegram object with  Telegram.from_bytes().
    
    Telegram attributes can be given values as regular Python 
    built-in types (ints, floats and strs), but their values are 
    internally handled and returned as Uints, Sints, Floats and Bins.
        
    A thorough explanation of the structure of telegrams is included 
    below:
    
    The Leybold TURBOVAC i/iX vacuum pump communicates with a computer 
    via its RS 232 or RS 485 serial port or a USB port using telegrams 
    of 24 bytes. The general structure of the telegrams follows the 
    USS protocol.
    
    Each byte consists of a start bit (0), 8 data bits, an even 
    parity bit (1 if there are an even number of 1's in the data 
    bits, 0 otherwise) and an ending bit (1). However, only the data 
    bits are included bytes objects representing telegrams; the serial 
    module automatically adds the other bits. 
    
    In the TURBOVAC manual, the data bits in a byte are indexed as 
    [7,6,5,4,3,2,1,0] (i.e. according to the power of 2 they 
    represent), but the convention [0,1,2,3,4,5,6,7] is used here, 
    because it corresponds to the indices of a Python list. 
    
    The functions and values of the different bytes in a telegram 
    are detailed below. Each list entry contains the name of the  
    Telegram object attribute (if any) that can be used to access 
    the value associated with the entry.
    
    Unless otherwise noted, all bytes have a default value of 0.
        
    Byte 0: STX (start of text). 
    Always 2.
    
    Byte 1: LGE (telegram length). 
    Excludes bytes 0 and 1, and thus always has a value of 22.
    
    Byte 2: ADR (address). 
    With a RS485 port this denotes the slave node number (0-31).
    Reading or changing this byte is not currently supported by this 
    class.
    
    Bytes 3-4: PKE (parameter number and type of access). 
    A 16 bit block:
        - Bits 0-3: Type of parameter access or response. 
            This is a 4 bit code indicating e.g. whether a parameter 
            should be read from or written to.
            Attribute: parameter_mode.
            Valid codes are detailed in the codes module.
        - Bit 4: 0
        - Bits 5-15: The parameter number.
            Attribute: parameter_number.
    
    Byte 5: - (reserved). Always 0.
    
    Byte 6: IND (parameter index). 
    If the requested parameter is indexed, this specifies the number 
    of the requested index.
    Attribute: parameter_index.

    Bytes 7-10: PWE (parameter value). 
    This block contains a parameter value that is written to or read 
    from the pump.
    Attribute: parameter_value.

    Bytes 11-12: PZD1 (status and control bits).
    16 bits each corresponding to a single setting or command which 
    can be turned on by setting the bit to 1.
    In a response from the pump these correspond to status 
    conditions affecting the pump instead of commands.
    Attribute: flag_bits.

    Bytes 13-14: PZD2 (current stator frequency). 
    Stator frequency in Hz; the same as parameter 3.
    Included in all replies, and can be included in queries to define 
    a setpoint for the frequency. (This only works if the setpoint is 
    enabled through the control bits, and overrides the setpoint 
    defined in parameter 24).
    Attribute: frequency.

    Bytes 15-16: PZD3 (current frequency converter temperature). 
    Frequency converter temperature in °C, included in all replies. 
    Same as parameter 11.
    Attribute: temperature.
    
    Bytes 17-18: PZD4 (current motor current). 
    Motor current in 0.1 A, included in all replies. 
    Same as parameter 5.
    Attribute: current

    Bytes 19-20: - (reserved). Always 0.

    Bytes 21-22: PZD6 (current intermediate circuit voltage).
    Intermediate circuit voltage in 0.1 V, included in all replies.
    Same as parameter 4.
    Attribute: voltage

    Byte 23: BCC (byte block check): 
    A checksum computed using the following algorithm: 
        checksum = bytes_[0]
        for byte in bytes_[1:22]:
            checksum = checksum XOR byte_
    """        
    Attribute = namedtuple('Attribute', 'name, type_, default, bits')    
 
    attributes = OrderedDict((a.name, a) for a in [
        Attribute('parameter_mode',   Bin,      '0000',      4),
        Attribute('parameter_number', Uint,     0,          11),
        Attribute('parameter_index',  Uint,     0,           8),
        Attribute('parameter_value',  TurboNum, 0,          32),
        Attribute('_parameter_bytes', bytes,    bytes(4), None),
        Attribute('parameter_type',   type,     Uint,     None),
        Attribute('flag_bits',        Bin,      16*'0',     16),
        Attribute('frequency',        Uint,     0,          16),
        Attribute('temperature',      Sint,     0,          16),
        Attribute('current',          Uint,     0,          16),
        Attribute('voltage',          Uint,     0,          16),
    ])
   
    def __init__(self, **kwargs):
        """Initalize a new Telegram.
        
        Args:
            kwargs: Initial values for Telegram attributes may be set 
                as keyword arguments.
            
        Raises:
            TypeError:
                If a keyword argument doesn't match any telegram 
                attribute.
            ValueError or TypeError: 
                If the value of any keyword argument is invalid.
        """
        # Set default values first.
        for a in self.attributes.values():
            setattr(self, a.name, a.default)
        # Then set keyword values.
        for name, value in kwargs.items():
            if name not in self.attributes or name[0] == '_':
                raise TypeError(f'invalid keyword: {name}')
            setattr(self, name, value)
    
    @classmethod
    def from_bytes(cls, bytes_: Union[bytes, bytearray]) -> Telegram:
        """Initalize a new Telegram from a bytes or bytearray object.
            
        The pump indexes bits in opposite order compared to Python, 
        so telegram.flag_bits are inverted when the Telegram object 
        is formed from the bytes-like object.
        
        Raises:
            ValueError: If bytes_ doesn't match the format for a valid 
                telegram.
        """
               
        if len(bytes_) != 24:
            raise ValueError(f'len(bytes_) should be 24, not {len(bytes_)}')
        
        if bytes_[0] != 2:
            raise ValueError(f'bytes_[0] should be 2, not {bytes_[0]}')
            
        if bytes_[1] != 22:
            raise ValueError(f'bytes_[1] should be 22, not {bytes_[1]}')
            
        checksum = cls.checksum(bytes_[0:23])[0]
        if bytes_[23] != checksum:
            raise ValueError(
                f'bytes_[23] (the checksum) should be '
                f'{checksum}, not was {bytes_[23]}')
        
        t = cls.__new__(cls)
        bits = Bin.from_bytes(bytes_[3:5])
        t.parameter_mode = bits[0:4]
        t.parameter_number = bits[5:16].to(Uint)
        
        t.parameter_index = bytes_[6]
        t.parameter_value = Uint.from_bytes(bytes_[7:11])
        t.flag_bits = Bin.from_bytes(bytes_[11:13])[::-1]
        
        t.frequency   = Uint.from_bytes(bytes_[13:15])
        t.temperature = Sint.from_bytes(bytes_[15:17])
        t.current     = Uint.from_bytes(bytes_[17:19])
        t.voltage     = Uint.from_bytes(bytes_[21:23])        
        return t
    
    def to_bytes(self) -> bytes:
        """Return *self* as a bytes object.
        
        The pump indexes bits in opposite order compared to Python, 
        so self.flag_bits are inverted when forming the bytes object.
        """
        
        list_ = [
            Uint(2, 8),             # STX
            Uint(22, 8),            # LGE
            Uint(0, 8),             # ADR
            (self.parameter_mode    # PKE
             + Bin('0') 
             + self.parameter_number.to(Bin)[-11:]), 
            Uint(0, 8),             # Reserved
            self.parameter_index,   # IND 
            self.parameter_value,   # PWE
            self.flag_bits[::-1],   # PZD1    
            self.frequency,         # PZD2
            self.temperature,       # PZD3
            self.current,           # PZD4 
            Uint(0, 16),            # Reserved
            self.voltage            # PZD6
        ]
        
        bytes_ = b''.join([x.to_bytes() for x in list_])
        bytes_ += self.checksum(bytes_)
        
        if len(bytes_) != 24:
            raise AssertionError(
                f'len(bytes_) should be 24, not {len(bytes_)}')
        return bytes_
    
    def __setattr__(self, name, value):
        """Convert *value* to an appropriately sized instance of a 
        TurboNum subclass before setting it.
        
        E.g. telegram.parameter_number = 1 actually sets 
        telegram.parameter_number to Uint(1, 11).
        
        Attributes not found in self.attributes and those of a 
        non-numeric type are set normally.
        """        
        #if value == -1:
        #    print('setattr called')
        #    return
        try:
            attr = self.attributes[name]
        except KeyError:
            object.__setattr__(self, name, value)
            return
        
        if issubclass(attr.type_, TurboNum):
            turbonum_value = attr.type_(value, attr.bits)
            object.__setattr__(self, name, turbonum_value)
        else:
            object.__setattr__(self, name, value)
            
    def __str__(self) -> str:
        """Same as __repr__, but also includes private attributes.
        """
        printable = OrderedDict(
            (attr, getattr(self, attr).__name__ if attr == 'parameter_type' 
             else repr(getattr(self, attr))) 
            for attr in self.attributes.keys()) 
        
        a_str = ', '.join(f'{a}={v}' for a, v in printable.items())
        return f'{type(self).__name__}({a_str})'       
    
    def __repr__(self) -> str:
        """Return a string that can be used to construct  an exact 
        copy of *self*.
        """
        printable = OrderedDict(
            (attr, getattr(self, attr).__name__ if attr == 'parameter_type' 
             else repr(getattr(self, attr))) 
            for attr in self.attributes.keys()
            if attr[0] != '_') 
        
        a_str = ', '.join(f'{a}={v}' for a, v in printable.items())
        return f'{type(self).__name__}({a_str})'

    def __eq__(self, other):
        """Two Telegrams are equal if their to_bytes() methods return 
        the same bytes.
        """
        try:
            return self.to_bytes() == other.to_bytes()
        except AttributeError:
            return False
            
    @property
    def parameter_value(self):
        """Get or set self.parameter_value.
        
        Setting self.parameter_value automatically sets 
        self.parameter_type to an appropriate type.
        This ensures that 
        "t.parameter_value = x; x == t.parameter_value"
        always returns True, unless self.parameter_type is changed by 
        hand between the calls to the setter and the getter.
        """
        return self.parameter_type.from_bytes(self.parameter_bytes)
    
    @parameter_value.setter
    def parameter_value(self, value):
        self.parameter_type = type(value)
        self.parameter_bytes = self.parameter_type(value, 32).to_bytes()
        
    @staticmethod
    def checksum(bytes_: Union[bytes, bytearray]) -> bytes:
        """Return the checksum computed from *bytes_*.
        
        Returns:
            The checksum in a bytes object of length 1.
        
        All bytes in *bytes_* are included in the checksum, so 
        byte 23 (where the checksum is saved) should be excluded from 
        *bytes_*.
        """
        # An argument type of bytes instead of a list of ints assures 
        # that all values are in range(256).
        numbers = tuple(bytes_)        
        checksum = 0
        for i in numbers:
            checksum = checksum ^ i  
        return bytes([checksum])