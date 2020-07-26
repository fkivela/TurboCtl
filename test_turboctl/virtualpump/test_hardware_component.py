"""Unit tests for the hardware_component module."""

import unittest
import time
import threading

from turboctl.telegram.codes import ControlBits, StatusBits
from turboctl.telegram.datatypes import Uint
from turboctl.telegram.parser import PARAMETERS
from turboctl.telegram.telegram import TelegramBuilder, TelegramReader
from turboctl.virtualpump.hardware_component import HardwareComponent
from turboctl.virtualpump.parameter_component import ExtendedParameters

# The attributes of HardwareComponent or the on and off methods aren't
# explicitly tested here, but they are used internally by the class,
# so these tests should fail if there was something wrong with them.
# Likewise, the other classes in the hardware_component module aren't tested,
# because they are only used by HardwareComponent.


class TestStop(unittest.TestCase):
    """Test the stop() method."""
    
    def test_stop(self):
        # Test classes are executed in alphabetical order, so this one is
        # executed last. Because of this, we have to wait for the threads
        # created by the other classes to stop.
        # Even if there was no possibility of dangling parallel threads left by
        # this module, this module might be run just after another test module,
        # which could have created its own parallel threads.
        # 0.2 is twice the default timestep for the parallel thread of
        # HardwareComponent.
        time.sleep(0.2)
        
        # Count active threads.
        original_count = threading.active_count()
        
        # Creating a HardwareComponent should add one thread.
        hwc = HardwareComponent(ExtendedParameters(PARAMETERS),
                                threading.Lock())
        self.assertEqual(threading.active_count(), original_count + 1)
        
        # Calling stop() should reduce the number of threads back to its
        # original value.
        hwc.stop()
        time.sleep(2 * hwc.step)
        self.assertEqual(threading.active_count(), original_count)


class Base(unittest.TestCase):

    def setUp(self):
        self.parameters = ExtendedParameters(PARAMETERS)
        # The lock would normally be used by VirtualPump to prevent the
        # frequency-updating loop from running while the reply is being
        # composed.
        # Since HardwareComponent is tested here alone without a VirtualPump,
        # the lock object doesn't really do anything.
        # Because the lock doesn't work correctly, there is a small chance of a
        # test failing due to a race condition.
        # E.g. when the pump is turned on, the reply should report the
        # frequency as 0, but the parallel loop might actually have time to
        # update the frequency to a nonzero value after the pump has turned on
        # but before the frequency has been read and written to the reply.
        # However, in practice this chance is very small, since the default
        # timestep of the frequency loop is 100 ms, which is very large
        # compared to the time required to execute a few lines of code.
        # In the unlikely event that the tests fail due to this, they may be
        # simply run again.
        self.hwc = HardwareComponent(self.parameters, threading.Lock())
        
    def tearDown(self):
        self.hwc.stop()
        
    def send(self, flag_bits):
        builder = TelegramBuilder().set_flag_bits(flag_bits)

        query = TelegramReader(builder.build('query'), 'query')
        # The reply initially contains the same data as the query, so we can
        # use the builder used to build the query as a basis for the reply.
        self.hwc.handle_hardware(query, builder)
        reply = TelegramReader(builder.build('reply'), 'reply')

        return reply
    
    def pump_off_test(self, reply):
        """Test the status of the pump in the off state."""
        self.assertEqual(reply.flag_bits, [StatusBits.READY,
                                            StatusBits.PARAM_CHANNEL])

        self.assertEqual(reply.frequency, 0)
        self.assertEqual(reply.temperature, 0)
        self.assertEqual(reply.current, 0)
        self.assertEqual(reply.voltage, 0)
        
        self.assertEqual(self.parameters[3].value[0].value, 0)
        self.assertEqual(self.parameters[11].value[0].value, 0)
        self.assertEqual(self.parameters[5].value[0].value, 0)
        self.assertEqual(self.parameters[4].value[0].value, 0)
        
    def on_command_test(self, reply):
        """Test the reply to an on commend."""
        self.assertEqual(set(reply.flag_bits), set([StatusBits.OPERATION,
                                                    StatusBits.ACCELERATION,
                                                    StatusBits.PARAM_CHANNEL,
                                                    StatusBits.PROCESS_CHANNEL
                                                    ]))

        self.assertEqual(reply.frequency, 0)
        self.assertEqual(reply.temperature, HardwareComponent.TEMPERATURE)
        self.assertEqual(reply.current, HardwareComponent.CURRENT)
        self.assertEqual(reply.voltage, HardwareComponent.VOLTAGE)
        
        self.assertEqual(self.parameters[3].value[0].value, 0)
        self.assertEqual(
            self.parameters[11].value[0].value, HardwareComponent.TEMPERATURE)
        self.assertEqual(
            self.parameters[5].value[0].value, HardwareComponent.CURRENT)
        self.assertEqual(
            self.parameters[4].value[0].value, HardwareComponent.VOLTAGE)
        
    def after_on_command_test(self, reply):
        """Test the status of the pump slightly after an on command."""
        self.assertEqual(set(reply.flag_bits), set([StatusBits.OPERATION,
                                                    StatusBits.ACCELERATION,
                                                    StatusBits.PARAM_CHANNEL,
                                                    StatusBits.PROCESS_CHANNEL,
                                                    StatusBits.TURNING
                                                    ]))

        self.assertGreater(reply.frequency, 0)
        self.assertEqual(reply.temperature, HardwareComponent.TEMPERATURE)
        self.assertEqual(reply.current, HardwareComponent.CURRENT)
        self.assertEqual(reply.voltage, HardwareComponent.VOLTAGE)
        
        self.assertGreater(self.parameters[3].value[0].value, 0)
        self.assertEqual(
            self.parameters[11].value[0].value, HardwareComponent.TEMPERATURE)
        self.assertEqual(
            self.parameters[5].value[0].value, HardwareComponent.CURRENT)
        self.assertEqual(
            self.parameters[4].value[0].value, HardwareComponent.VOLTAGE)
        
    def long_after_on_command_test(self, reply):
        """Test the status of the pump after the frequency setpoint has been
        reached."""
        self.assertEqual(set(reply.flag_bits), set([StatusBits.OPERATION,
                                                    StatusBits.PARAM_CHANNEL,
                                                    StatusBits.PROCESS_CHANNEL,
                                                    StatusBits.TURNING
                                                    ]))

        setpoint = self.parameters[24].value[0].value
        
        self.assertEqual(reply.frequency, setpoint)
        self.assertEqual(reply.temperature, HardwareComponent.TEMPERATURE)
        self.assertEqual(reply.current, HardwareComponent.CURRENT)
        self.assertEqual(reply.voltage, HardwareComponent.VOLTAGE)
        
        self.assertEqual(self.parameters[3].value[0].value, setpoint)
        self.assertEqual(
            self.parameters[11].value[0].value, HardwareComponent.TEMPERATURE)
        self.assertEqual(
            self.parameters[5].value[0].value, HardwareComponent.CURRENT)
        self.assertEqual(
            self.parameters[4].value[0].value, HardwareComponent.VOLTAGE)
        
    def off_command_test(self, reply):
        """Test the reply to an off commend."""
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.TURNING,
                                                    StatusBits.DECELERATION,
                                                    StatusBits.PARAM_CHANNEL,
                                                    ]))

        setpoint = self.parameters[24].value[0].value
        
        self.assertEqual(reply.frequency, setpoint)
        self.assertEqual(reply.temperature, 0)
        self.assertEqual(reply.current, 0)
        self.assertEqual(reply.voltage, 0)
        
        self.assertEqual(self.parameters[3].value[0].value, setpoint)
        self.assertEqual(self.parameters[11].value[0].value, 0)
        self.assertEqual(self.parameters[5].value[0].value, 0)
        self.assertEqual(self.parameters[4].value[0].value, 0)
        
    def after_off_command_test(self, reply):
        """Test the status of the pump slightly after an off command."""
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.TURNING,
                                                    StatusBits.DECELERATION,
                                                    StatusBits.PARAM_CHANNEL,
                                                    ]))

        setpoint = self.parameters[24].value[0].value
        
        self.assertLess(reply.frequency, setpoint)
        self.assertEqual(reply.temperature, 0)
        self.assertEqual(reply.current, 0)
        self.assertEqual(reply.voltage, 0)
        
        self.assertLess(self.parameters[3].value[0].value, setpoint)
        self.assertEqual(self.parameters[11].value[0].value, 0)
        self.assertEqual(self.parameters[5].value[0].value, 0)
        self.assertEqual(self.parameters[4].value[0].value, 0)

        
class TestHardwareComponent(Base):
    
    def test_cycle(self):
        """Test a complete on-off cycle."""
        
        # Ask pump status in the off state.
        reply = self.send(flag_bits=[])
        self.pump_off_test(reply)
        
        # Send the on command and check the response.
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.on_command_test(reply)
        
        # Wait for the pump to start, and ask its status.
        # The wait time is twice the timestep of the pump so that it certainly
        # has enough time to update the frequency.
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.after_on_command_test(reply)
    
        # Set the acceleration rate to infinite, wait for the frequency to
        # reach the setpoint, and ask pump status.
        # Afterwards the acceleration rate is reset back to its old value.
        old_value = self.hwc.abs_acceleration
        self.hwc.abs_acceleration = float('inf')
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.long_after_on_command_test(reply)
        self.hwc.abs_acceleration = old_value
    
        # Send the off command and check the response.
        reply = self.send(flag_bits=[])
        self.off_command_test(reply)
    
        # Wait for the pump to turn off, and ask its status.
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[])
        self.after_off_command_test(reply)
        
        # Set the acceleration to infinite again, wait for the requency to
        # drop to zero, and ask pump status.
        self.hwc.abs_acceleration = float('inf')
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[])
        self.pump_off_test(reply)
        
    def test_change_setpoint(self):
        self.hwc.abs_acceleration = float('inf')

        # Changing the setpoint while the pump is off shouldn't affect the
        # frequency immediately.
        self.parameters[24].value[0] = Uint(1234, 16)
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[])
        self.assertEqual(reply.frequency, 0)
        
        # However, after sending the on command the frequency becomes equal to
        # the checkpoint.
        # Send the on command.
        self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        time.sleep(2 * self.hwc.step)
        # Ask for pump status.
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.assertEqual(reply.frequency, 1234)
        
        # Change the setpoint to a bigger value.
        self.parameters[24].value[0] = Uint(4567, 16)
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.assertEqual(reply.frequency, 4567)
        
        # Change the setpoint to a smaller value.
        self.parameters[24].value[0] = Uint(89, 16)
        time.sleep(2 * self.hwc.step)
        reply = self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.assertEqual(reply.frequency, 89)
        
    def test_on_control_bit_alone(self):
        """Make sure the 'ON' control bit doesn't do anything without the
        'COMMAND' control bit.
        """
        # Sending the 'ON' bit in the off state doesn't turn the pump on.
        reply = self.send(flag_bits=[ControlBits.ON])
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.PARAM_CHANNEL]))
        
        # Turn the pump on.
        self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        self.assertTrue(self.hwc.is_on)
        
        # Sending the 'ON' bit in the on state turns the pump off just like an
        # empty telegram does.
        reply = self.send(flag_bits=[ControlBits.ON])
        self.assertFalse(self.hwc.is_on)
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.PARAM_CHANNEL]))
        
    def test_command_control_bit_alone(self):
        """Make sure the 'COMMAND' control bit doesn't do anything (except add
        the 'PROCESS_CHANNEL' status bit) without the 'ON' control bit.
        """
        # Sending the 'COMMAND' bit in the off state doesn't turn the pump on.
        reply = self.send(flag_bits=[ControlBits.COMMAND])
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.PARAM_CHANNEL,
                                                    StatusBits.PROCESS_CHANNEL
                                                    ]))
        
        # Turn the pump on.
        self.send(flag_bits=[ControlBits.COMMAND, ControlBits.ON])
        
        # Sending the 'COMMAND' bit in the on state turns the pump off just
        # like an empty telegram does.
        reply = self.send(flag_bits=[ControlBits.COMMAND])
        self.assertFalse(self.hwc.is_on)
        self.assertEqual(set(reply.flag_bits), set([StatusBits.READY,
                                                    StatusBits.PARAM_CHANNEL,
                                                    StatusBits.PROCESS_CHANNEL
                                                    ]))
    
        
if __name__ == '__main__':
    unittest.main()
