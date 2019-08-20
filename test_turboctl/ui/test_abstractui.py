import unittest
import time

from turboctl import AbstractUI, VirtualPump, Query, Reply, Types, PARAMETERS, ParameterError, ControlBits, StatusBits
from test_turboctl import dummy_parameter

new_parameters = [
    dummy_parameter(number=2001, type_=Types.UINT),
    dummy_parameter(number=2002, type_=Types.SINT, min_ = -1000),
    dummy_parameter(number=2003, type_=Types.FLOAT, min_ = -1000),
    dummy_parameter(number=2004, indices=range(5)),
    dummy_parameter(number=2005, writable=False),
    dummy_parameter(number=2006, max_=10),
]
PARAMETERS.update({p.number: p for p in new_parameters})

#Query.parameters = PARAMETERS
#Reply.parameters = TEST_PARAMETERS

class Base(unittest.TestCase):
    pass
    
    @classmethod
    def setUpClass(cls):
        cls.pump = VirtualPump()#TEST_PARAMETERS)
        cls.ui = AbstractUI(cls.pump.port)
        
    @classmethod
    def tearDownClass(cls):
        cls.pump.close()
                
        
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

    
        
        
        

        
#class TestSendAndReceive(Base):
#    
#    def test_success(self):
#        query, reply = self.ui._send(Query())
#        
#        self.assertTrue(isinstance(query, Query))
#        self.assertTrue(isinstance(reply, Reply))
#        self.assertEqual(query, Query())
#        
#    def test_failure(self):
#        
#        for mode in ['NO_REPLY', 'WRONG_LENGTH', 'INVALID_CONTENT']:
#            with self.subTest(i=mode):
#                self.vc.mode = ReplyMode[mode]
#        
#                with self.assertRaises(ValueError):
#                    q, r = self.ui._send(Query())

class TestOther(Base):
    
    
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

        
if __name__ == '__main__':
    unittest.main()