"""Unit tests for the telegram module."""


import unittest

from turboctl.telegram.codes import (ParameterResponse, ParameterError,
                                     ControlBits)
from turboctl.telegram.datatypes import Uint, Sint, Float, Bin
from turboctl.telegram.telegram import (Telegram, TelegramBuilder, 
                                        TelegramReader, checksum)
from test_turboctl.telegram.test_parser import dummy_parameter

import turboctl


# Replace the actual parameters with dummy values for easier testing.
turboctl.telegram.telegram.PARAMETERS = {
    # A basic parameter.
    1234: dummy_parameter(number=1234),
    # Parameters of different types.
    1: dummy_parameter(number=1, datatype=Sint),
    2: dummy_parameter(number=2, datatype=Float),
    3: dummy_parameter(number=3, datatype=Bin),
    # An indexed parameter with a different number of bits. 
    4: dummy_parameter(number=4, indices=range(1), bits=32),
}


class Base(unittest.TestCase):
    
    def setUp(self):
        self.kwargs = {
            'parameter_code': Bin('0001'),
            'parameter_number': Uint(1234, 11), # '0001' + '0' + 1234 = 20 210
            'parameter_index': Uint(56),
            'parameter_value': Uint(5432, 32), # = 21 56
            'flag_bits': Bin('1111000011001100'), # = 51 15
            'frequency': Uint(1221, 16), # = 4 197
            'temperature': Sint(2332, 16), # = 9 28
            'current': Uint(3443, 16), # = 13 115
            'voltage': Uint(4554, 16) # = 17 202
        }
        
        self.telegram = Telegram(**self.kwargs)
        
        self.bytes = bytes([
            2, 22, 0,     # Start 
            20, 210,      # Parameter code and number
            0,            # Empty
            56,           # Parameter index
            0, 0, 21, 56, # Value
            51, 15,       # Flag bits
            4, 197,       # Frequency
            9, 28,        # Temperature
            13, 115,      # Current
            0, 0,         # Empty
            17, 202,      # Voltage
            138           # Checksum
        ])


class TestTelegram(Base):
    
    def test_bytes(self):
        self.assertEqual(bytes(self.telegram), self.bytes)
        
    def _test_bytes_with_value(self, value):
        # test_bytes, but telegram.parameter_value is replaced with *value*.
        
        # Replace parameter_value in self.telegram.
        self.kwargs['parameter_value'] = value
        
        # Replace parameter_value in self.bytes.
        self.bytes = self.bytes[:7] + bytes(value) + self.bytes[11:]
        
        # Update the checksum.
        self.bytes = self.bytes[:-1] + bytes([checksum(self.bytes[:-1])])
        
        t = Telegram(**self.kwargs)
        self.assertEqual(bytes(t), self.bytes)

    def test_bytes_sint(self):
        value = Sint(-1234, 32)        
        self._test_bytes_with_value(value)
        
    def test_bytes_float(self):
        value = Float(1234.5678)
        self._test_bytes_with_value(value)
        
    def test_bytes_bin(self):        
        value = Bin(4 * '10010110')
        self._test_bytes_with_value(value)


class TestTelegramBuilder(Base):
                
    ### Setters ###
            
    def test_setters(self):
        
        # Test creating a query.
        
        tb = (TelegramBuilder()
            # 0001 is "read a value".
            .set_parameter_mode('read')
            .set_parameter_number(1234)
            .set_parameter_index(56)
            .set_parameter_value(5432)
            .set_flag_bits(
            [ControlBits(i) for i, c 
             in enumerate('1111000011001100') if c == '1'])
            .set_frequency(1221)
            .set_temperature(2332)
            .set_current(3443)
            .set_voltage(4554))
        
        self.assertEqual(tb.build('query'), self.telegram)

        # Test creating a reply.

        # 0001 is "16 bit value sent".
        tb.set_parameter_mode('response')
        self.assertEqual(tb.build('reply'), self.telegram)
        
    def test_default(self):
        t = Telegram(
            parameter_code=Bin('0000'), 
            parameter_number=Uint(0, 11), 
            parameter_index=Uint(0, 8), 
            parameter_value=Uint(0, 32), 
            flag_bits=Bin(16 * '0'), 
            frequency=Uint(0, 16), 
            temperature=Sint(0, 16), 
            current=Uint(0, 16),
            voltage=Uint(0, 16)
        )
        self.assertEqual(TelegramBuilder().build(), t)
        
    def test_wrong_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            TelegramBuilder().build('qery')
            
    ### from_bytes ###
    
    def test_from_bytes(self):
        t = TelegramBuilder.from_bytes(self.bytes).build()
        self.assertEqual(t, self.telegram)
            
    def test_from_bytes_with_invalid_byte_0_fails(self):
        bytes2 = bytes([0]) + self.bytes[1:]
        with self.assertRaises(ValueError):
            TelegramBuilder().from_bytes(bytes2)
    
    def test_from_bytes_with_invalid_byte_1_fails(self):
        bytes2 = self.bytes[0:1] + bytes([0]) + self.bytes[2:]
        with self.assertRaises(ValueError):
            TelegramBuilder().from_bytes(bytes2)
            
    def test_from_bytes_with_invalid_length_fails(self):
        bytes2 = self.bytes + bytes([0]) 
        with self.assertRaises(ValueError):
            TelegramBuilder().from_bytes(bytes2)
            
    def test_from_bytes_with_invalid_checksum_fails(self):
        bytes2 = self.bytes[:-1] + bytes([0])
        with self.assertRaises(ValueError):
            TelegramBuilder().from_bytes(bytes2)
            
    ### Parameter value ###
    
    def test_parameter_value_sint(self):
        t = (TelegramBuilder()
            .set_parameter_number(1)
            .set_parameter_mode('write')
            .set_parameter_value(-1234)
            .build())
        
        self.assertEqual(t.parameter_value, Sint(-1234, 32))
        
    def test_parameter_value_float(self):
        t = (TelegramBuilder()
            .set_parameter_number(2)
            .set_parameter_mode('write')
            .set_parameter_value(1234.5678)
            .build())

        self.assertEqual(t.parameter_value, Float(1234.5678))
        
    def test_parameter_value_bin(self):
        t = (TelegramBuilder()
            .set_parameter_number(3)
            .set_parameter_mode('write')
            .set_parameter_value(4 * '10010110')
            .build())

        self.assertEqual(t.parameter_value, Bin(4 * '10010110'))
        
    def test_parameter_value_invalid_value_fails(self):
        tb = (TelegramBuilder()
            .set_parameter_number(1234)
            .set_parameter_mode('write')
            .set_parameter_value(-1234)
        )
        with self.assertRaises(ValueError):
            tb.build()
        
    def test_parameter_value_wrong_type_fails(self):
        tb = (TelegramBuilder()
            .set_parameter_number(3)
            .set_parameter_mode('write')
            .set_parameter_value(1234)
        )
        with self.assertRaises(TypeError):
            tb.build()
            
    def test_parameter_value_with_no_parameter_access(self):
        """Make sure the parameter type is always Uint when there is no
        parameter access.
        """
        for mode in ['none', 'error']:
            with self.subTest(i=mode):
        
                t =  (TelegramBuilder()
                     .set_parameter_number(3)
                     .set_parameter_mode('none')
                     .set_parameter_value(1234)
                     .build())
                self.assertEqual(t.parameter_value, Uint(1234, 32))
            
    ### Parameter value from bytes
    
    # The most basic case has already been tested in test_from_bytes.
            
    def _test_value_from_bytes(self, param_number, param_value):
        # test_from_bytes, but telegram.parameter_number and 
        # telegram.parameter_value are replaced with *param_number* and
        # *param_value*.
        
        parameter_bytes = bytes(Bin('00010') + Uint(param_number, 11))
        value_bytes = bytes(param_value)
        
        # Replace parameter_number and parameter_value in self.bytes.
        self.bytes = (self.bytes[:3] + parameter_bytes + self.bytes[5:7]
                      + value_bytes + self.bytes[11:])
        
        # Update the checksum.
        self.bytes = self.bytes[:-1] + bytes([checksum(self.bytes[:-1])])
        
        t = TelegramBuilder.from_bytes(self.bytes).build()
        self.assertEqual(t.parameter_value, param_value)
        
    def test_sint_from_bytes(self):
        number = 1
        value = Sint(-1234, 32)        
        self._test_value_from_bytes(number, value)
        
    def test_float_from_bytes(self):        
        number = 2
        value = Float(1234.5678)
        self._test_value_from_bytes(number, value)        
        
    def test_bin_from_bytes(self):        
        number = 3
        value = Bin(4 * '10010110')
        self._test_value_from_bytes(number, value)        
            
    ### Parameter code ###
    
    def test_parameter_codes(self):
        # Test some parameter codes with an indexed 32 bit parameter.
        # An unindexed 16 bit prameter was tested in test_setters.
        
        tb = (TelegramBuilder().set_parameter_number(4))
        
        tb.set_parameter_mode('read')
        t = tb.build('query')
        self.assertEqual(t.parameter_code, Bin('0110'))

        tb.set_parameter_mode('write')
        t = tb.build('query')
        self.assertEqual(t.parameter_code, Bin('1000'))


        tb.set_parameter_mode('response')
        t = tb.build('reply')
        self.assertEqual(t.parameter_code, Bin('0101'))
        
    ### Parameter code from bytes ###
        
    def _set_parameter_access_and_value(self, code, number, value):
        """Update the parameter code, number and value in self.bytes.
        
        The checksum is updated automatically.
        
        Args:
            code: A string.
            number: An int.
            value: A Data subclass instance.
        """
        # Change the 4 code bits but keep the other bits in the parameter
        # block the same.
        parameter_block = bytes(Bin(code) + Bin('0') + Uint(number, 11))

        # Replace the parameter code/number and value blocks.
        self.bytes = (self.bytes[:3] + parameter_block + self.bytes[5:7]
                      + bytes(value) + self.bytes[11:])
        
        # Update the checksum.
        self.bytes = (
            self.bytes[:-1] + bytes([checksum(self.bytes[:-1])]))
    
    def test_from_bytes_no_parameter_access(self):
        """Make sure invalid parameter numbers are accepted if the parameter
        mode is 'none' or 'error'.
        """
        no_access_code = ParameterResponse.NONE.value
        error_code = ParameterResponse.ERROR.value
        
        for code in [no_access_code, error_code]:
            with self.subTest(i=code):
                
                # parameter_number is 0 (an invalid value), but this should be
                # ok since the parameter isn't accessed.
                self._set_parameter_access_and_value(code, 0, Sint(-1, 32))
                                
                # The 'error' mode only works here if the telegram is a reply.
                t = TelegramBuilder.from_bytes(self.bytes).build('reply')

                # The value will be interpreted as an Uint instead of a Sint,
                # since the type of the parameter wasn't checked.
                self.assertEqual(t.parameter_value, Uint(2**32 - 1, 32))
        
    def test_from_bytes_invalid_parameter_number(self):
        """Make sure invalid parameter numbers are not accepted if the
        parameter mode is not 'none' or 'error'.
        """
        # parameter_number is 0, which should raise an error, since the
        # parameter is now accessed.        
        self._set_parameter_access_and_value('0001', 0, Uint(0, 32))
        
        with self.assertRaises(ValueError):
            TelegramBuilder.from_bytes(self.bytes).build()


class TestTelegramReader(Base):
        
    ### Getters ###
    
    def test_values(self):
        tr = TelegramReader(self.telegram)
        
        self.assertEqual(tr.parameter_mode, 'response')
        self.assertEqual(tr.parameter_number, 1234)
        self.assertEqual(tr.parameter_index, 56)
        self.assertEqual(tr.parameter_value, 5432)
        self.assertEqual(
            tr.flag_bits, [ControlBits(i) for i, c 
                           in enumerate('1111000011001100') if c == '1'])
        self.assertEqual(tr.frequency, 1221)
        self.assertEqual(tr.temperature, 2332)
        self.assertEqual(tr.current, 3443)
        self.assertEqual(tr.voltage, 4554)
        
    def test_query(self):
        tr = TelegramReader(self.telegram, 'query')        
        self.assertEqual(tr.parameter_mode, 'read')
        
    def test_invalid_type_fails(self):
        with self.assertRaises(ValueError):
            TelegramReader(self.telegram, 'qery')
            
    ### parameter_mode ###
    
    # Test the same modes as in TestTelegramBuilder.test_parameter_codes.
    
    def test_parameter_mode_read(self):        
        self.kwargs['parameter_code'] = Bin('0110')
        
        t = Telegram(**self.kwargs)
        tr = TelegramReader(t, 'query')
        
        self.assertEqual(tr.parameter_mode, 'read')
        
    def test_parameter_mode_write(self):
        self.kwargs['parameter_code'] = Bin('1000')
        
        t = Telegram(**self.kwargs)
        tr = TelegramReader(t, 'query')
        
        self.assertEqual(tr.parameter_mode, 'write')
        
    def test_parameter_mode_response(self):
        self.kwargs['parameter_code'] = Bin('0101')
        
        t = Telegram(**self.kwargs)
        tr = TelegramReader(t, 'reply')
        
        self.assertEqual(tr.parameter_mode, 'response')

    ### parameter_error ###
        
    def test_parameter_error(self):
        t = (TelegramBuilder()
            .set_parameter_number(1234)
            .set_parameter_mode('error')
            .set_parameter_value(0)
            .build('reply'))
            
        tr = TelegramReader(t)
        self.assertEqual(tr.parameter_error, ParameterError.WRONG_NUM)

    def test_no_parameter_error(self):
        t = (TelegramBuilder().build('reply'))
            
        tr = TelegramReader(t)
        self.assertEqual(tr.parameter_error, None)
        
    def test_invalid_parameter_error_number_fails(self):
        t = (TelegramBuilder()
            .set_parameter_number(1234)
            .set_parameter_mode('error')
            .set_parameter_value(999)
            .build('reply'))
            
        tr = TelegramReader(t)
        with self.assertRaises(ValueError):
            tr.parameter_error
            
    ### Magic methods ###
    
    def test_repr(self):
        # Replace the default status bits since there are so many.
        self.telegram.flag_bits = Bin('1010000000000000')        
        
        tr = TelegramReader(self.telegram)
        string = f"TelegramReader(telegram={str(self.telegram)}, type='reply')"
        
        self.assertEqual(repr(tr), string)
    
    def test_str(self):
        self.telegram.flag_bits = Bin('1010000000000000')        
        tr = TelegramReader(self.telegram)
        
        string = f"""
TelegramReader(
    telegram={str(self.telegram)},
    type='reply',
    parameter_mode='response',
    parameter_number=1234,
    parameter_index=56,
    parameter_value=5432,
    parameter_error=None,
    flag_bits=[<StatusBits.READY: 0>, <StatusBits.OPERATION: 2>],
    frequency=1221,
    temperature=2332,
    current=3443,
    voltage=4554
)
"""[1:-1]

        self.assertEqual(str(tr), string)


if __name__ == '__main__':
    unittest.main()
