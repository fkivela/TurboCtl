"""This module defines the Telegram class, which can used to 
communicate with a Leybold TURBOVAC i/iX vacuum pump.        
"""

import collections
import re

from ..data import Types

from .typedbytes import TypedBytes

class Telegram:
    """A telegram for communicating with a Leybold TURBOVAC vacuum 
    pump.
    
    Objects of this class contain a TypedBytes object to store the 
    binary data contained in a TURBOVAC telegram and provide methods 
    for reading and writing this data.
        
    The Leybold TURBOVAC i/iX vacuum pump communicates with a computer 
    via its RS 232 or RS 485 serial port using telegrams consisting of 
    a series of bytes. The general structure of the telegrams follows 
    the USS protocol.
    
    Each byte consists of a start bit (0), 8 data bits, an even 
    parity bit (1 if there are an even number of 1's in the data 
    bits, 0 otherwise) and an ending bit (1).
    
    In the TURBOVAC manual, the bits in a byte are indexed as 
    [7,6,5,4,3,2,1,0] (i.e. according to the power of 2 they 
    represent), but the convention [0,1,2,3,4,5,6,7] is used here, 
    because it corresponds to the indices of a Python list. 
    
    The telegrams have the following structure:
        
        Byte 0: STX (start of text). Always 2.
        
        Byte 1: LGE (telegram length). Excludes bytes 0 and 1, and 
        thus always has a value of 22.
        
        Byte 2: ADR (address). With a RS485 port this denotes the 
        slave node number (0-31), and with a RS232 this has a value 
        of 0.
        
        Bytes 3-4: PKE (parameter number and type of access). A 16 bit 
        value.
            - Bits 0-3: Type of parameter access or response. When a 
                query is sent to the pump, the type of access 
                (read or write) is specified as well as the size of 
                the value (16 or 32 bit) and whether it is a regular 
                value or a field value (i.e. one index of an indexed 
                parameter). When a response is received from the pump, 
                the type of the parameter is repeated or replaced by a 
                code indicating an error message. The possible values 
                for this 4 bit code are detailed in the 
                codes module.
            - Bit 4: 0
            - Bits 5-15: The parameter number.
        
        Byte 5: - (reserved). Always 0.
        
        Byte 6: IND (parameter index). If the requested parameter is 
        indexed, this specifies the number of the requested index. For 
        unindexed parameters this is 0.
    
        Bytes 7-10: PWE (parameter value). A 32 bit value. In write 
        mode the new value is specified here (and repeated in the 
        response from the pump), while in read mode this has a value 
        of 0.
    
        Bytes 11-12: PZD1 (status and control bits). The first process 
        data block. 16 bits each corresponding to a single setting or 
        command which can be turned on by setting the bit to 1. In a 
        response from the pump these correspond to 16 status conditions
        with each 1 signifying that the corresponding status condition 
        is currently affecting the pump.
    
        Bytes 13-14: PZD2 (current stator frequency). A response from 
        the pump returns the frequency in Hz. This is the same as 
        parameter 3. The value is 0 for queries to the pump.
    
        Bytes 15-16: PZD3 (current frequency converter temperature). 
        The temperature in °C; 0 for queries. Same as parameter 11.
        
        Bytes 17-18: PZD4 (current motor current). The current 
        in 0.1 A; 0 for queries. Same as parameter 5.
    
        Bytes 19-20: - (reserved). Always 0.
    
        Bytes 21-22: PZD6 (current intermediate circuit voltage) The 
        voltage in 0.1 V; 0 for queries. Same as parameter 4.
    
        Byte 23: BCC (byte block check): A checksum computed using the 
        following algorithm: 
                checksum = data[0]
                for byte_ in data[1:22]:
                    checksum = checksum XOR byte_
                    
    Changing the pump address in a telegram is not currently supported, 
    but all other data (parameter data, command/status bits and hardware
    data) can be read and written using the methods in Telegram object.
    """
    
    START_BYTE_VALUE = 2
    LENGTH_BYTE_VALUE = 22
    LENGTH = 24
    
    START_BYTE = 0
    LENGTH_BYTE = 1
    ADDRESS_BYTE = 2
    ACCESS_BYTES = slice(3, 5)
    INDEX_BYTE = 6
    VALUE_BYTES = slice(7, 11)
    CONTROL_BYTES = slice(11, 13)
    FREQUENCY_BYTES = slice(13, 15)
    TEMPERATURE_BYTES = slice(15, 17)
    CURRENT_BYTES = slice(17, 19)
    VOLTAGE_BYTES = slice(21, 23)
    CHECK_BYTE = 23
    
    WRITABLE_PROPERTIES = [
        'parameter_access_type',
        'parameter_number',
        'parameter_index',
        'parameter_value',
        'control_or_status_bits',
        'frequency',
        'temperature',
        'current',
        'voltage',
        'checksum'
    ]
    READABLE_PROPERTIES = WRITABLE_PROPERTIES
    
    def __init__(self, data=None, **kwargs): 
        """Initalize a new Telegram object with given data.
        
        Args:
            data=None: None, or any argument accepted by the 
                constructor of the TypedBytes class.
            kwargs: If *data* is None, initial values for telegram 
                properties may be set as keyword arguments.
        
        Returns:
            If data is None and no other keyword arguments are used: 
                An otherwise empty telegram with bytes 0, 1 and 23 set 
                to their correct values.
            If data is not None or some other keyword arguments are 
            used: 
                A telegram containing the specified data.
            
        Raises:
            TypeError or ValueError: 
                If the value of any argument is invalid.
            TypeError:
                If both *data* and other keyword arguments are defined.
            TypeError:
                If a keyword argument doesn't match any valid telegram 
                property.
            ValueError: If the telegram created from *data* has an 
                incorrect length or checksum.
        """
        
        if data and kwargs:
            raise TypeError(
                'Keyword arguments cannot be given when initializing from '
                '*data*')
        
        if data:
            self._create_from_data(data)
        else:
            self._create_empty()
            self._set_kwargs(**kwargs)                        
                
        valid = self.is_valid()
        if not valid:
            raise ValueError('Cannot create telegram: ' 
                             + valid.reason_for_fail)
            
    def _create_empty(self, **kwargs):
        """Initialize an empty Telegram."""
        self.typedbytes = TypedBytes(self.LENGTH)
        self.typedbytes[self.START_BYTE] = self.START_BYTE_VALUE
        self.typedbytes[self.LENGTH_BYTE] = self.LENGTH_BYTE_VALUE
        self.set_checksum()
                
    def _create_from_data(self, data):
        """Initialize a new Telegram from given data."""
        try:
            self.typedbytes = TypedBytes(data)
        except (TypeError, ValueError) as e:
            # "raise type(e)" raises a ValueError if *e* is a VE, 
            # and a TypeError if *e* is a TE.
            raise type(e)(f'Could not create a telegram from the following '
                          f'input data: {data}') from e
                      
    def _set_kwargs(self, **kwargs):
        """Set properties given as keyword arguments to their 
        given values."""
        for key, value in kwargs.items():
            if not key in self.WRITABLE_PROPERTIES:
                raise TypeError(f'Invalid kwarg key: {key}')
            setattr(self, key, value)                  
    
    def __str__(self):
        """Return a string representation of *self*.
        
        This representation includes the values of read-only derived
        properties.
        """
        return self._kwarg_str(self.READABLE_PROPERTIES)
                
    def __repr__(self):
        """Return an exact string representation of *self*.
        
        For subclasses, this representation doesn't include the values 
        of read-only derived properties.
        
        Usage: 
            >> repr(telegram)
            
            >> eval(repr(telegram)) 
            returns a copy of *telegram*.
        """
        return self._kwarg_str(self.WRITABLE_PROPERTIES)
    
    def _kwarg_str(self, properties):
        """#TODO"""
        string = f'{type(self).__name__}('
        first_iteration = True
        
        for p in properties:
            
            if first_iteration:
                first_iteration = False
            else:
                string += ', '
            
            string += f'{p}={repr(getattr(self, p))}'
        
        string += ')'
        return string  
    
    def __eq__(self, other):
        """Determine equality between two Telegram objects.
        
        Usage:
            telegram1 == telegram2 
        
        Returns:
            True if *other* is a Telegram and self.data == other.data;
            otherwise False. 
        """
        
        if not isinstance(other, Telegram):
            return False
        
        return self.data == other.data
    
    def __len__(self):
        """Return the number of bytes in the telegram.
        
        Usage: 
            >> len(telegram)
                
        Returns:
            This should always return 24.
        """
        return len(self.typedbytes)
    
    @property
    def data(self):
        """Get the bytes in the telegram.
        
        Returns:
            self.typedbytes.data (a bytearray object).
        """
        return self.typedbytes.data
    
    @property
    def parameter_access_type(self):
        """Get or set parameter access/response type.
        
        This property defines whether the type of parameter access
        or response: read or write, size of the value, and whether the 
        parameter is indexed or not.
        
        While this property is called parameter access, it instead 
        defines the type of parameter response in cases where this
        class is used to represent a reply telegram from the pump.
        
        Setter args / getter returns:
            string: A 4-character string of 1's and 0's. All such codes
                are accepted, but only those described in the codes
                module are understood by the pump.
                
        Setter raises:
            ValueError: If *string* is not valid.
            TypeError: If *string* is the wrong type.
        """

        return self.typedbytes[self.ACCESS_BYTES, Types.STR][0:4]

    @parameter_access_type.setter
    def parameter_access_type(self, string):
        self._assert_valid_bits(string, 4)

        parameter = self.parameter_number
        access_str = string + '0' + bin(parameter)[2:].zfill(11)

        self.typedbytes[self.ACCESS_BYTES] = access_str
        self.set_checksum()
        
    @property
    def parameter_number(self):
        """Get or set parameter number.
        
        This property defines which parameter should be accessed. 
        The value should be left to 0 if no parameter access is 
        defined.
        
        Setter args / getter returns:
            value: An 11 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """
        
        param_str = self.typedbytes[self.ACCESS_BYTES, Types.STR][5:16]
        return int(param_str, 2)
        
    @parameter_number.setter
    def parameter_number(self, value):
        
        # Make sure *value* is an unsigned integer so that
        # self.parameter_number returns the same value.
        self._assert_unsigned_int(value)
        
        param_access = self.parameter_access_type
        access_str = param_access + '0' + bin(value)[2:].zfill(11)
        self.typedbytes[self.ACCESS_BYTES] = access_str
        self.set_checksum()
        
    @property
    def parameter_index(self):
        """Get or set parameter index.
        
        This property defines which index of a parameter should be 
        accessed. The value should be left to 0 for unindexed 
        parameters.
        
        Setter args / getter returns:
            value: An 8 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """

        return self.typedbytes[self.INDEX_BYTE]
    
    @parameter_index.setter
    def parameter_index(self, value):
        self._assert_unsigned_int(value)
        self.typedbytes[self.INDEX_BYTE] = value
        self.set_checksum()
        
    @property
    def parameter_value(self):
        """Get or set parameter value.
        
        This property defines the value of a parameter. For telegrams 
        that are sent to the pump, this is be a new value that should 
        be set. For reply telegrams from the pump, this is a value that
        was read and returned.
        
        Setter args:
            value: An 32 bit int, str or float.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
            
        Getter returns:
            An unsigned integer (i.e. an non-negative int). 
            The get_parameter_value() function should be used if the 
            value should be returned using another number type.
        """
        return self.get_parameter_value()
    
    @parameter_value.setter
    def parameter_value(self, value):
        self.typedbytes[self.VALUE_BYTES] = value
        self.set_checksum()
    
    def get_parameter_value(self, type_=Types.UINT):
        """Get parameter value as a *type_*.
        
        Args:
            type_: An instance of Types (default Types.UINT).
            
        Returns:
            The value as an int, str or float.
            
        Raises:
            TypeError: If *type_* is not a valid instance of Types.
        """
        
        return self.typedbytes[self.VALUE_BYTES, type_]
        
    @property
    def control_or_status_bits(self):
        """Get or set control/status bits.
        
        This property defines which control or status bits are active.
        
        Setter args / getter returns:
            bits: A 16-character string of 1's and 0's.
                Bits should be given in an order where bit 0 is the 
                first character. The string is automatically flipped
                so that it is saved into the telegram in the correct
                order (i.e. bit 0 being the last character).
                
        Setter raises:
            ValueError or TypeError: If *bits* is not valid.
        """
        # The bits are reversed because bit numbers are given in the
        # manual in reverse order compared to Python indexing       
        reverse_bits = self.typedbytes[self.CONTROL_BYTES, Types.STR]
        return reverse_bits[::-1]
    
    @control_or_status_bits.setter
    def control_or_status_bits(self, bits):
        self._assert_valid_bits(bits, 16)
        reverse_bits = bits[::-1];
        self.typedbytes[self.CONTROL_BYTES] = reverse_bits
        self.set_checksum()
        
    def set_control_or_status_bits(self, indices, values):
        """Set specific control/status bits.
        
        Args:
            indices: The indices of the bits that should be set 
                (an iterable of ints).
            values: New values for the specified bits. A string of 1's 
                and 0's (with the same len() as *indices*), or an 
                iterable of 1-character strings '1' and '0'.
                
        Raises:
            IndexError: If any of the indices is out of range.
            ValueError: If any of the values is invalid.
        """
        
        # Python strings are immutable, so the control bit string is 
        # converted to a list so that it can be edited.
        ctrl_bits = list(self.control_or_status_bits);
        
        for n, ind in enumerate(indices):
            ctrl_bits[ind] = values[n]
        
        # Convert the list back to a string with join
        self.control_or_status_bits = ''.join(ctrl_bits)

    @property
    def frequency(self):
        """Set or get stator frequency in Hz.
        
        If *self* is a reply telegram from the pump, the current stator
        frequency reported by the pump can be read from this property. 
        
        The value of this property can be manually set for testing 
        purposes, but this has no effect on the pump.
        
        Setter args / getter returns:
            value: A 16 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """
        
        return self.typedbytes[self.FREQUENCY_BYTES]
    
    @frequency.setter    
    def frequency(self, value):
        self._assert_unsigned_int(value)
        self.typedbytes[self.FREQUENCY_BYTES] = value
        self.set_checksum()
        
    @property
    def temperature(self):
        """Set or get frequency converter temperature in  °C.
        
        If *self* is a reply telegram from the pump, the current 
        frequency converter temperature reported by the pump can be 
        read from this property. 
        
        The value of this property can be manually set for testing 
        purposes, but this has no effect on the pump.
        
        Setter args / getter returns:
            value: A 16 bit signed integer. Note that the value of 
                temperature can be negative, while the other values 
                (frequency, current, voltage) are always non-negative.
                
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, too small or too large).
        """
        
        return self.typedbytes[self.TEMPERATURE_BYTES, Types.SINT]
    
    @temperature.setter
    def temperature(self, value):
        self._assert_signed_int(value, 16)
        self.typedbytes[self.TEMPERATURE_BYTES] = value
        self.set_checksum()
        
    @property
    def current(self):
        """Set or get motor current in 0.1 A.
        
        If *self* is a reply telegram from the pump, the current 
        motor current reported by the pump can be read from this 
        property. 
        
        The value of this property can be manually set for testing 
        purposes, but this has no effect on the pump.
        
        Setter args / getter returns:
            value: A 16 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """
        
        return self.typedbytes[self.CURRENT_BYTES]
    
    @current.setter
    def current(self, value):
        self._assert_unsigned_int(value)
        self.typedbytes[self.CURRENT_BYTES] = value
        self.set_checksum()
    
    @property
    def voltage(self):
        """Set or get intermediate circuit voltage in 0.1 V. 
        
        If *self* is a reply telegram from the pump, the current 
        intermediate circuit voltage reported by the pump can be read 
        from this property. 
        
        The value of this property can be manually set for testing 
        purposes, but this has no effect on the pump.
        
        Setter args / getter returns:
            value: A 16 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """
        
        return self.typedbytes[self.VOLTAGE_BYTES]  
    
    @voltage.setter
    def voltage(self, value):
        self._assert_unsigned_int(value)
        self.typedbytes[self.VOLTAGE_BYTES] = value
        self.set_checksum()
        
    @staticmethod
    def _assert_unsigned_int(value):
        
        if not isinstance(value, int):
            raise TypeError(f'*value* must be an int, not {type(value)}')
        
        if value < 0:
            raise ValueError(f'*value* must be non-negative, was {value}')
    
    @staticmethod        
    def _assert_signed_int(value, size):
        
        if not isinstance(value, int):
            raise TypeError(f'*value* must be an int, not {type(value)}')
        
        if value > 2**(size-1) - 1:
            raise ValueError(f'setting values larger than {2**(size-1)-1} '
                             f'results in signed integer overflow')
    
    @staticmethod        
    def _assert_valid_bits(string, length):
        regex = f'^[01]{{{length}}}$' #Returns ^[01]{<length>}
        valid = re.fullmatch(regex, string)
        
        if not valid:
            raise ValueError(f"The string {string} doesn't match the "
                             "correct format")
    
    @property
    def checksum(self):
        """Set or get the value of the checksum byte. 
        
        There is no need to manually set this property outside 
        testing, because its value is automatically updated with the 
        set_checksum() method when other properties are changed.
        
        Setter args / getter returns:
            value: An 8 bit unsigned integer.
            
        Setter raises:
            ValueError or TypeError: If *value* is invalid 
                (wrong type, negative or too large).
        """
        
        return self.typedbytes[self.CHECK_BYTE]
    
    @checksum.setter
    def checksum(self, value):
        self._assert_unsigned_int(value)
        self.typedbytes[self.CHECK_BYTE] = value
    
    @classmethod  
    def compute_checksum(cls, numbers):
        """Returns the value of the checksum.
        
        Args:
            numbers: The values of all other bytes except the 
                checksum byte (an iterable of ints).
                
        Returns:
            The checksum as an int.
            
        Raises:
            TypeError: If any of the numbers is not an int.
        """
        
        checksum = 0
        for i in numbers:
            checksum = cls._xor(checksum, i)
            
        return checksum
    
    @staticmethod
    def _xor(a, b):
        """Returns a XOR b.
        
        XOR is the exclusive OR operator.
        The integers *a* and *b* are compared using a bitwise XOR 
        operation and the result is returned as an integer.
        
        XOR truth table:
            1 XOR 1 = 0
            0 XOR 0 = 0
            1 XOR 0 = 1
            0 XOR 1 = 1
        """
        
        # Bitwise operations: (a or b) and not (a and b)
        return (a|b) & ~(a&b)
    
    def set_checksum(self):
        """Set the checksum byte to its correct value.
        
        The checksum in computed from the values of all other bytes in 
        the telegram, and this function is thus called every time a 
        value in the telegram is changed in order to keep the checksum
        correct.
        """                    
        self.checksum = self.compute_checksum(self.data[:self.CHECK_BYTE])
        
    def is_valid(self):
        """Checks whether *self* is a valid telegram.
        
        If a telegram has an incorrect number of bytes or an invalid 
        value in its start byte, length byte or checksum byte, 
        this method will return False and a string explaining what is 
        wrong with the Telegram. If the telegram is valid, True and 
        an empty string are returned instead. 
        
        Returns:
            A tuple with the following indices:
                [0] A boolean
                [1] A str
        """
                
        checks = collections.OrderedDict()
        # An ordered dict is used instead of a regular one so that 
        # length is always tested first.
        checks['length'] = {'current': len(self), 'correct': self.LENGTH}
            
        try:
            checks['start byte'] = {
                    'current': self.typedbytes[self.START_BYTE],
                    'correct': self.START_BYTE_VALUE
                    }
            
            checks['length byte']  = {
                    'current': self.typedbytes[self.LENGTH_BYTE],
                    'correct': self.LENGTH_BYTE_VALUE
                    }
            
            checks['checksum'] = {
                    'current': self.checksum,
                    'correct': self.compute_checksum(
                            self.data[:self.CHECK_BYTE])
                    }
            
        except IndexError:
            # If the telegram is too short, the other checks can't be 
            # defined. However, they aren't needed, since it is already
            # known that the telegram is invalid.
            pass
                            
        for name, value in checks.items():
            
            if value['current'] != value['correct']:
                reason_for_fail = (
                    f"{name} should be {value['correct']}, "
                    f"was {value['current']}"
                    )
                return Validity(False, reason_for_fail)
            
        return Validity(True, None)    
    
    
class Validity():
# TODO: document
    def __init__(self, is_valid, reason_for_fail):
        self.is_valid = is_valid
        self.reason_for_fail = reason_for_fail

    def __bool__(self):
        return self.is_valid
    
    def __repr__(self):
        kwargs = [f'{k}={v}' for k, v in self.__dict__.items()]
        kwstring = ', '.join(kwargs)
        return f'{type(self).__name__}({kwstring})'
