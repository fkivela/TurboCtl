import unittest
import serial
import time
import threading

from turboctl.telegram.codes import ControlBits
from turboctl.telegram.telegram import TelegramBuilder, TelegramReader
from turboctl.virtualpump.virtualpump import VirtualPump


class TestStop(unittest.TestCase):
    """Make sure VirtualPump shuts down all parallel threads properly."""
    
    def test_with_block(self):
        """Test the __enter__ and __exit__ methods."""
        
        # Wait for parallel threads to shut down in case some other tests are
        # run before this one.
        # 0.2 s is twice the default timestep of the frequency loop
        # in HardwareComponent.
        time.sleep(0.2)
        # Count the number of active threads.
        original_count = threading.active_count()
        
        with VirtualPump():
            # Creating a VirtualPump should increase the number of threads by
            # two (one from the connection thread and one from the frequency
            # simulation thread).
            self.assertEqual(threading.active_count(), original_count + 2)
            
        # Exiting the with block should automatically stop the new threads.
        # Wait for them to shut down and make sure they have done so.
        time.sleep(0.2)
        self.assertEqual(threading.active_count(), original_count)
        
    def test_stop(self):
        """Test manually stopping VirtualPump."""
        
        # Do the same things as in test_with_block, but stop the VirtualPump
        # manually.
        time.sleep(0.2)
        original_count = threading.active_count()
        
        vp = VirtualPump()
        self.assertEqual(threading.active_count(), original_count + 2)
            
        vp.stop()
        time.sleep(0.2)
        self.assertEqual(threading.active_count(), original_count)


class TestVirtualPump(unittest.TestCase):
    
    def setUp(self):
        self.vp = VirtualPump()
        # A timeout is needed; otherwise the connection will block forever if
        # the pump doesn't send a response.
        self.connection = serial.Serial(self.vp.connection.port, timeout=0.01)
        
    def tearDown(self):
        self.vp.stop()
        self.connection.close()
        
    def send(self, mode='none', number=0, value=0, bits=[]):
        
        query = (TelegramBuilder()
                 .set_parameter_mode(mode)
                 .set_parameter_number(number)
                 .set_parameter_value(value)
                 .set_flag_bits(bits)
                 .build('query'))
        
        self.connection.write(bytes(query))
        time.sleep(0.1)
        bytes_out = self.connection.read(24)
        reply = TelegramBuilder().from_bytes(bytes_out).build('reply')
        return TelegramReader(reply, 'reply')
        
    def test_parallel_thread_starts_and_stops(self):
        with VirtualPump() as vp:
            self.assertTrue(vp.connection.is_running())
        
        time.sleep(2 * vp.connection.sleep_time)
        # The parallel thread must finish the current iteration before
        # stopping.
        self.assertFalse(vp.connection.is_running())
    
    def test_invalid_telegram(self):
        """Make sure sending something that isn't a valid telegram 
        doesn't cause blocking or other unwanted effects.
        """
        self.connection.write(bytes([1,2,3,4]))
        out = self.connection.read(24)
        self.assertEqual(out, bytes())

    def test_change_setpoint(self):
        """Make sure ParameterComponent and HardwareComponent work properly
        together. The frequency setpoint parameter should determine the
        pump frequency, which in turn should be reflected in the frequency
        parameter.
        """
        # Make the pump accelerate infinitely fast in order to make testing
        # easier.
        self.vp.hardware_component.abs_acceleration = float('inf')
        # The bits required to turn or keep the pump on.
        bits = [ControlBits.COMMAND, ControlBits.ON]
        
        # Ask pump frequency and turn it on.
        reply = self.send(mode='read', number=3, bits=bits)
        self.assertEqual(reply.parameter_value, 0)
        self.assertEqual(reply.frequency, 0)
        
        # Wait for the pump to turn on.
        time.sleep(2 * self.vp.hardware_component.step)
        
        # Ask pump frequency, which should now be at the setpoint.
        reply = self.send(mode='read', number=3, bits=bits)
        self.assertEqual(reply.parameter_value, 1000)
        self.assertEqual(reply.frequency, 1000)
        
        # TODO: Investigate whether there might be an error with these limits
        # in the pump manual.        
        # Set a new lower limit for the lower limit of the setpoint
        # (default = 2000).
        self.send(mode='write', number=20, value=0, bits=bits)
        # Set a new lower limit for the setpoint (default = 2000).
        self.send(mode='write', number=19, value=1000, bits=bits)
        # Set a new upper limit for the setpoint (default = 1000).
        self.send(mode='write', number=18, value=2000, bits=bits)
        # Set a new setpoint.
        reply = self.send(mode='write', number=24, value=1234, bits=bits)
        
        # Wait for the frequency to change.
        time.sleep(2 * self.vp.hardware_component.step)
        
        # Ask for frequency again.
        reply = self.send(mode='read', number=3, bits=bits)
        self.assertEqual(reply.parameter_value, 1234)
        self.assertEqual(reply.frequency, 1234)
        
        
if __name__ == '__main__':
    unittest.main()
