import unittest
import sys
import time
from io import StringIO

from turboctl import (ShellTUI, VirtualPump, Query, Reply, StatusBits, 
                      ControlBits, full_output, control_or_status_output, 
                      hardware_output, parameter_output, 
                      UIArgumentNumberError, UITypeError, UIValueError)      
        
class Base(unittest.TestCase):
    
    def setUp(self):
        self.maxDiff = None
        self.old = sys.stdout
        self.printed = StringIO()
        sys.stdout = self.printed
        self.vp = VirtualPump()
        self.ui = ShellTUI(self.vp.port)
        
    def tearDown(self):
        sys.stdout = self.old
        self.vp.close()
    
    
class TestOnOff(Base):
    
    @classmethod
    def setUpClass(cls):
        cls.q = Query(control_or_status_set={ControlBits.START_STOP, 
                      ControlBits.COMMAND}, frequency=0, temperature=40, 
                      current=10, voltage=20)
        cls.r = Reply(cls.q.data)
        cls.r.control_or_status_set={StatusBits.OPERATION, 
                                     StatusBits.ACCELERATION}
    
    def test_verbosity_1(self):
        self.ui.cmd_verbosity(1)
        self.ui.cmd_onoff()
        string = ('Turning the pump on or off\n')
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_2(self):
        self.ui.cmd_verbosity(2)
        self.ui.cmd_onoff()
        string = ('Turning the pump on or off\n' +
                  control_or_status_output(self.r, True) + '\n')
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_3(self):
        self.ui.cmd_verbosity(3)
        self.ui.cmd_onoff()
        string = full_output(self.q, self.r) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
        
class TestStatus(Base):
    
    @classmethod
    def setUpClass(cls):
        cls.q = Query()
        cls.r = Reply(control_or_status_set={StatusBits.READY})
    
    def test_verbosity_1(self):
        self.ui.cmd_verbosity(1)
        self.ui.cmd_status()
        string = hardware_output(self.r, False) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_2(self):
        self.ui.cmd_verbosity(2)
        self.ui.cmd_status()
        string = (control_or_status_output(self.r) + '\n' + 
                  hardware_output(self.r, True) + '\n')
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_3(self):
        self.ui.cmd_verbosity(3)
        self.ui.cmd_status()
        string = full_output(self.q, self.r) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
        
class TestRead(Base):
    
    @classmethod
    def setUpClass(cls):
        cls.q = Query(parameter_number=1, parameter_mode='read')
        cls.r = Reply(parameter_number=1, parameter_mode='response',
                      parameter_value=180, 
                      control_or_status_set={StatusBits.READY})
    
    def test_verbosity_1(self):
        self.ui.cmd_verbosity(1)
        self.ui.cmd_read(1)
        string = parameter_output(self.r, False) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_2(self):
        self.ui.cmd_verbosity(2)
        self.ui.cmd_read(1)
        string = parameter_output(self.r, True) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_verbosity_3(self):
        self.ui.cmd_verbosity(3)
        self.ui.cmd_read(1)
        string = full_output(self.q, self.r) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_index(self):
        self.ui.cmd_verbosity(2)
        self.ui.cmd_read(1, 1)
        r = Reply(self.r.data)
        r.parameter_index = 1
        string = parameter_output(r, True) + '\n'
        self.assertEqual(self.printed.getvalue(), string)
        
    def test_invalid_args(self):
        self.ui.cmd_verbosity(2)
        
        errors = {'1'  : UITypeError,
                  1.0  : UITypeError,
                  -1   : UIValueError,
                  2**16: UIValueError}
        
        for n, e in errors.items():
            with self.assertRaises(e):
                self.ui.cmd_read(n)
                
        for n, e in errors.items():
            with self.assertRaises(e):
                self.ui.cmd_read(1, n)






        
    
    
#    def test_status(self):
#        
#        str_in = 'status'
#        
#        str_out = (
#"""
#Sent a telegram with the following contents:
#    No parameter access
#    No control bits active
#
#Received a telegram with the following contents:
#    No parameter access
#    No status conditions present
#    Stator frequency: 0 Hz
#    Frequency converter temperature: 0 °C
#    Motor current: 0×0.1 A
#    Intermediate circuit voltage: 0×0.1 V
#""")
#        
#        self.ui.run(str_in)
#        self.assertEqual(self.ui.output, str_out)


if __name__ == '__main__':
    unittest.main()