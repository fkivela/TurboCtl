"""Unit tests for the telegram module."""
import unittest

from test_turboctl import GenericTests
from turboctl import Telegram, Uint, Sint, Float

class TestTelegram(GenericTests):
    
    def setUp(self):
        self.t = Telegram()
        self.t.parameter_code = '0110'
        self.t.parameter_number = 1234 # '0110' + '0' + 1234 = 100 210
        self.t.parameter_index = 56
        self.t.parameter_value = 5432 # = 21 56
        self.t.flag_bits = '1111000011001100' # = 51 15
        self.t.frequency = 1221 # = 4 197
        self.t.temperature = 2332 # = 9 28
        self.t.current = 3443 # = 13 115
        self.t.voltage = 4554 # = 17 202
        
        self.bytes_ = bytes([
            2, 22, 0,     # Start 
            100, 210,     # Mode
            0,            # Empty
            56,           # Index
            0, 0, 21, 56, # Value
            51, 15,       # Bits
            4, 197,       # Frequency
            9, 28,        # Temperature
            13, 115,      # Current
            0, 0,         # Empty
            17, 202,      # Voltage
            250])         # Checksum
    
    def test_init(self):
        t_empty1 = Telegram()
        t_empty2 = Telegram(parameter_number=0, parameter_value=0)
        self.assertEqual(t_empty1, t_empty2)
        
        t_filled1 = Telegram(parameter_number=1, parameter_value=123)
        t_filled2 = Telegram()
        t_filled2.parameter_number = 1
        t_filled2.parameter_value = 123
        
        self.assertEqual(t_filled1, t_filled2)
        
    def test_to_bytes(self):
        # Lists are easier to compare than bytes objects if the test 
        # fails.
        self.assertEqual(list(self.t.to_bytes()), list(self.bytes_))    
    
    def test_from_bytes(self):
        self.assertEqual(Telegram.from_bytes(self.bytes_), self.t)
        
    def test_repr(self):
        copy = eval(repr(self.t))
        self.assertEqual(copy, self.t)
        
    def test_parameter_value_and_type(self):
        t = Telegram()
        self.assertEqual(t.parameter_type, Uint)
        t.parameter_value = 123
        self.assertEqual(t.parameter_type, Uint)
        self.assertEqual(t.parameter_value, 123)
        
        t.parameter_value = -123
        self.assertEqual(t.parameter_type, Sint)
        self.assertEqual(t.parameter_value, -123)
        
        t.parameter_value = 123.456
        self.assertEqual(t.parameter_type, Float)
        self.assertAlmostEqual(t.parameter_value, 123.456, 5)
        

if __name__ == '__main__':
    unittest.main()