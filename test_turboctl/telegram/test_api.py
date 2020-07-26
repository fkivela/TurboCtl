"""Unit tests for the api module."""

import unittest

import serial

from turboctl.telegram import api
from turboctl.telegram.codes import ControlBits
from turboctl.virtualpump.virtualpump import VirtualPump


class TestApi(unittest.TestCase):
    
    def setUp(self):
        self.vp = VirtualPump()
        self.connection = serial.Serial(self.vp.connection.port, timeout=1)
        
    def tearDown(self):
        self.vp.stop()
        
    def test_test(self):
        self.assertTrue(True)
        
    def check_parameter(self, telegram, type_, mode, number, value, index):
        self.assertEqual(telegram.type, type_)
        self.assertEqual(telegram.parameter_mode, mode)
        self.assertEqual(telegram.parameter_number, number)
        self.assertEqual(telegram.parameter_value, value)
        self.assertEqual(telegram.parameter_index, index)
        
    def check_hardware(self, telegram, frequency, temperature, current,
                       voltage, bits):
        self.assertEqual(telegram.type, 'query')
        self.assertEqual(telegram.frequency, 0)
        self.assertEqual(telegram.temperature, 0)
        self.assertEqual(telegram.current, 0)
        self.assertEqual(telegram.voltage, 0)
        # Compare sets so that the order doesn't matter.
        self.assertEqual(set(telegram.flag_bits), set(bits))
        
    def test_write_and_read_unindexed_parameter(self):
        # Parameter 16 has the following relevant properties:
        # min=0 max=150 default=80 access=r/w type=s16.
        
        # Write a value to the parameter.
        query, reply = api.write_parameter(self.connection, 16, 123)
        self.check_parameter(query, 'query', 'write', 16, 123, 0)
        self.check_parameter(reply, 'reply', 'response', 16, 123, 0)
        
        # Read the written value.
        query, reply = api.read_parameter(self.connection, 16)
        self.check_parameter(query, 'query', 'read', 16, 0, 0)
        self.check_parameter(reply, 'reply', 'response', 16, 123, 0)
        
    def test_write_and_read_indexed_parameter(self):
        # Parameter 26 has the following relevant properties:
        # min=0 max=65535 default=25 access=r/w type=u16 indices=[0,1,2]
        
        # Write a value to the parameter.
        query, reply = api.write_parameter(self.connection, 26, 123, 1)
        self.check_parameter(query, 'query', 'write', 26, 123, 1)
        self.check_parameter(reply, 'reply', 'response', 26, 123, 1)
        
        # Read the written value.
        query, reply = api.read_parameter(self.connection, 26, 1)
        self.check_parameter(query, 'query', 'read', 26, 0, 1)
        self.check_parameter(reply, 'reply', 'response', 26, 123, 1)
        
    def test_onoff_cycle(self):
        
        on_bits = [ControlBits.COMMAND, ControlBits.ON]
        
        # There's no need to properly test reply, since the data it contains is
        # determined by VirtualPump, which is tested separately.
        # It is enough to make sure the reply exists and actually represents a
        # reply.
        
        # Ask pump status when the pump is off.
        query, reply = api.status(self.connection, pump_on=False)
        self.check_hardware(query, 0, 0, 0, 0, [])
        self.assertEqual(reply.type, 'reply')
        self.assertFalse(self.vp.hardware_component.is_on)
        
        # Turn the pump on.
        query, reply = api.status(self.connection, pump_on=True)
        self.check_hardware(query, 0, 0, 0, 0, on_bits)
        self.assertEqual(reply.type, 'reply')
        self.assertTrue(self.vp.hardware_component.is_on)
        
        # Turn the pump off again.
        query, reply = api.status(self.connection, pump_on=False)
        self.check_hardware(query, 0, 0, 0, 0, [])
        self.assertEqual(reply.type, 'reply')
        self.assertFalse(self.vp.hardware_component.is_on)


if __name__ == '__main__':
    unittest.main()
