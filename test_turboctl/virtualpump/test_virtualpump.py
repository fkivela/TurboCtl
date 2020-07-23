import unittest
import serial
import time
from copy import copy

from turboctl.telegram.codes import WrongNumError, MinMaxError, OtherError
from turboctl.telegram.datatypes import Uint, Sint, Float
from turboctl.telegram.telegram import TelegramBuilder, TelegramReader
from turboctl.virtualpump.virtualpump import VirtualPump
from test_turboctl.telgram.test_parser import dummy_parameter        
        
class TestConnection(Base): 
    
    def test_invalid_telegram(self):
        """Make sure sending something that isn't a valid telegram 
        doesn't cause blocking or other unwanted effects.
        """
        self.connection.write(bytes([1,2,3,4]))
        out = self.connection.read(24)
        self.assertEqual(out, bytes())
            
    def test_parallel_thread_starts_and_stops(self):
        with VirtualPump() as vp:
            self.assertTrue(vp.connection.is_running())
        
        time.sleep(0.1)
        # The parallel thread must finish the current iteration before
        # stopping.
        self.assertFalse(vp.connection.is_running())

    def test_empty_telegram(self):
        parameter = dummy_parameter(number=0)
        reply = self.access_parameter(dummy_parameter(number=0), 'none', 0)       
        
        self.check_response(reply, parameter, 'none', 0, 0)
        self.assertFalse(reply.status_list)
        
        # Since a virtual pump returns random values for these,
        # one of these might be 0 by chance, and this test 
        # would fail. In this case, the test should be run again.
        self.assertEquals(reply.frequency, HardwareComponent.FREQUENCY)
        self.assertTrue(reply.temperature, HardwareComponent.TEMPERATURE)
        self.assertTrue(reply.current, HardwareComponent.CURRENT)
        self.assertTrue(reply.voltage, HardwareComponent.VOLTAGE)
        
        
        
if __name__ == '__main__':
    unittest.main()