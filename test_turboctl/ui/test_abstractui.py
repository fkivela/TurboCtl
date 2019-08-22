import unittest
import time
import serial

from turboctl import (AbstractUI, VirtualPump, VirtualConnection, Query, 
                      TelegramWrapper, Types, PARAMETERS, ParameterError, 
                      StatusBits)
from test_turboctl import dummy_parameter

# Add some new parameters for simpler testing.
# The largest actual parameter number is 1102, so these won't 
# override any old parameters. Otherwise the virtual pump might not 
# work, since it accesses hardware parameters.
new_parameter_list = [
    dummy_parameter(number=2001, type_=Types.UINT),
    dummy_parameter(number=2002, type_=Types.SINT, min_ = -1000),
    dummy_parameter(number=2003, type_=Types.FLOAT, min_ = -1000),
    dummy_parameter(number=2004, indices=range(5)),
    dummy_parameter(number=2005, writable=False),
    dummy_parameter(number=2006, max_=10),
]


class Base(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Replace *PARAMETERS* with *new_parameters*
        new_parameters = PARAMETERS 
        new_parameters.update({p.number: p for p in new_parameter_list})
        TelegramWrapper.parameters = new_parameters
        
        cls.pump = VirtualPump(new_parameters)
        cls.ui = AbstractUI(cls.pump.port)
        
    @classmethod
    def tearDownClass(cls):
        cls.pump.close()
        # Reset TelegramWrapper back to its original state to avoid 
        # breaking tests in other test modules when running all unit 
        # tests at once.
        TelegramWrapper.parameters = PARAMETERS
                
        
class TestReadAndWriteParameter(Base):
    
    def read_and_write(self, value, number, index):
        q, r = self.ui.write_parameter(value, number, index)
        
        self.assertEqual(q.parameter_mode, 'write')
        self.assertEqual(q.parameter_number, number)
        self.assertEqual(q.parameter_index, index)
        self.assertAlmostEqual(q.parameter_value, value, 5)
        
        self.assertEqual(r.parameter_mode, 'response')
        self.assertEqual(r.parameter_number, number)
        self.assertEqual(r.parameter_index, index)
        self.assertAlmostEqual(r.parameter_value, value, 5)
        
        q, r = self.ui.read_parameter(number, index)
        
        self.assertEqual(q.parameter_mode, 'read')
        self.assertEqual(q.parameter_number, number)
        self.assertEqual(q.parameter_index, index)
        self.assertAlmostEqual(q.parameter_value, 0, 5)
        
        self.assertEqual(r.parameter_mode, 'response')
        self.assertEqual(r.parameter_number, number)
        self.assertEqual(r.parameter_index, index)
        self.assertAlmostEqual(r.parameter_value, value, 5)
        
    def test_uint(self):
        self.read_and_write(100, 2001, 0)
        
    def test_sint(self):
        self.read_and_write(-100, 2002, 0)
        
    def test_float(self):
        # This also tests reading 32-bit numbers.
        self.read_and_write(123.456, 2003, 0)
        
    def test_indexed(self):
        self.read_and_write(123, 2004, 3)
        
    def test_no_write(self):
        q, r = self.ui.write_parameter(123, 2005, 0)
        
        self.assertEqual(r.parameter_mode, 'no write')
        self.assertEqual(r.parameter_number, 2005)
        self.assertEqual(r.parameter_index, 0)
        self.assertEqual(r.parameter_value, 123)
                
    def test_error(self):
        q, r = self.ui.write_parameter(11, 2006, 0)
        self.assertEqual(r.parameter_mode, 'error')
        self.assertEqual(r.error_code, ParameterError.MINMAX)

        
class TestOtherCommands(Base):
    
    def test_on_off_and_status(self):
        
        # Make sure the status signal is correct, and the pump is 
        # initially not turning.
        q, r = self.ui.status()
        status_bits = [2,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20]
        status_query = Query(status_bits)
        self.assertEqual(q, status_query)        
        self.assertFalse(StatusBits.TURNING in r.control_or_status_set)

        # Make sure the on_off signal is correct.
        q, r = self.ui.on_off()
        onoff_bits = [2,22,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,17]
        onoff_query = Query(onoff_bits)
        self.assertEqual(q, onoff_query)
        
        # Wait for the pump to start.
        time.sleep(0.1)
        
        # Make sure the pump starts turning.
        q, r = self.ui.status()
        self.assertTrue(StatusBits.TURNING in r.control_or_status_set)
        
    def test_save_data(self):
        # Turn the pump on.
        self.ui.on_off()
        
        # Write a value and restart the pump.
        self.ui.write_parameter(200, 1)
        self.ui.on_off()
        self.ui.on_off()
        # The written value is replaced by the default value.
        q, r = self.ui.read_parameter(1)
        self.assertEqual(r.parameter_value, 180)
        
        # The written value is saved to nonvolatile memory.
        self.ui.write_parameter(200, 1)
        self.ui.save_data()
        self.ui.on_off()
        self.ui.on_off()
        q, r = self.ui.read_parameter(1)
        self.assertEqual(r.parameter_value, 200)
        
    def test_set_frequency(self):
        # Turn the pump on.
        self.ui.on_off()
        
        # Make sure the setpoint frequency is the default value.
        q, r = self.ui.read_parameter(24)
        self.assertEqual(r.parameter_value, 1000)
        
        # Set a new setpoint.
        self.ui.set_frequency(800)
        time.sleep(0.1)
        
        # Make sure the change was applied.
        q, r = self.ui.read_parameter(24)
        self.assertEqual(r.parameter_value, 800)
        
        
class TestConnection(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.vc = VirtualConnection()
        cls.ui = AbstractUI(cls.vc.port)
        
    @classmethod
    def tearDownClass(cls):
        cls.vc.close()
    
    def test_invalid_port(self):
        with self.assertRaises(serial.SerialException):
            AbstractUI('test')
            
    def test_empty_port(self):
        ui = AbstractUI(None)
        with self.assertRaises(serial.SerialException):
            ui.status()
            
    def test_no_response(self):
        def process(input_):        
            return b''
        self.vc.process = process
        with self.assertRaises(ValueError):
            self.ui.status()
            
    def test_invalid_response(self):
        def process(input_):        
            return b'1234'
        self.vc.process = process
        with self.assertRaises(ValueError):
            self.ui.status()

        
if __name__ == '__main__':
    unittest.main()