"""Unit tests for the output module."""

import unittest

from turboctl import (help_string, full_output, parameter_output, 
                      control_or_status_output, hardware_output, Query, Reply, 
                      ParameterError, ControlBits, StatusBits, Command)

class Base(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Print long strings.
        cls.maxDiff = None

class TestOther(Base):
    
    def test_full_output(self):
        
        q = Query(parameter_number=1,
                  parameter_value=123,
                  parameter_mode='write',
                  control_or_status_set={ControlBits.COMMAND,
                                         ControlBits.START_STOP,
                                         ControlBits.FREQ_SETPOINT},
                   frequency=1000
                   )
        
        r = Reply(parameter_number=1,
                  parameter_value=123,
                  parameter_mode='response',
                  control_or_status_set={StatusBits.TURNING,
                                         StatusBits.ACCELERATION},
                   frequency=1000,
                   temperature=30,
                   current=100,
                   voltage=120
                   )

        string = (
"""
Sent a telegram with the following contents:
    Write the value 123 to parameter 1
    Active control bits:
        Start/Stop
        Set frequency setpoint
        Enable control bits 0, 5, 6, 7, 8, 13, 14, 15
    Stator frequency setpoint: 1000 Hz

Received a telegram with the following contents:
    The value of parameter 1 is 123
    Present status conditions:
        Accelerating
        Pump is turning
    Stator frequency: 1000 Hz
    Frequency converter temperature: 30 °C
    Motor current: 100×0.1 A
    Intermediate circuit voltage: 120×0.1 V
""".strip()                
)
        self.assertEqual(full_output(q, r), string)
    
    def test_help_string(self):
        commands = [
            Command(names=['test1', 't, t1'],
                function='cmd_test1',
                args=[],
                description='Test command 1'),
        
            Command(names=['test2', 't2'],
                    function='cmd_test2',
                    args=['a', 'b', 'c=1'],
                    description=('Test command 2 with a very long '
                                 'description. This long description is '
                                 'intended to test line wrapping.'))
        ]
        
        string = (
"""
Accepted commands:
Command    Aliases    Args           Description
test1      t, t1                     Test command 1
test2      t2         <a> <b> [c=1]  Test command 2 with a very
                                     long description. This long
                                     description is intended to
                                     test line wrapping.
""".strip()
)
        self.assertEqual(help_string(commands), string)

class TestParameterOutput(Base):
    
    def setUp(self):
        self.q    = Query(parameter_number=1,  parameter_value=123)
        self.q_Hz = Query(parameter_number=3,  parameter_value=123)
        self.qi   = Query(parameter_number=29, parameter_value=123, 
                          parameter_index=1)
        self.r    = Reply(parameter_number=1,  parameter_value=123)
        self.r_Hz = Reply(parameter_number=3,  parameter_value=123)
        self.ri   = Reply(parameter_number=29, parameter_value=123, 
                          parameter_index=1)
    
    def test_read(self):
        self.q.parameter_mode = 'read'
        self.qi.parameter_mode = 'read'

        string = 'Return the value of parameter 1'
        indexed_string = 'Return the value of parameter 29, index 1'
        
        self.assertEqual(parameter_output(self.q), string)
        self.assertEqual(parameter_output(self.qi), indexed_string)
        self.assertEqual(parameter_output(self.q, verbose=False), '')    
        
    def test_write(self):
        self.q.parameter_mode = 'write'
        self.qi.parameter_mode = 'write'
        self.q_Hz.parameter_mode = 'write'
        
        string = 'Write the value 123 to parameter 1'
        index_string = 'Write the value 123 to parameter 29, index 1'
        unit_string = 'Write the value 123 Hz to parameter 3'
        
        self.assertEqual(parameter_output(self.q), string)
        self.assertEqual(parameter_output(self.qi), index_string)
        self.assertEqual(parameter_output(self.q_Hz), unit_string)
        self.assertEqual(parameter_output(self.q, verbose=False), '')
        
    def test_none(self):
        q = Query()
        r = Reply()
        
        string = 'No parameter access'
        self.assertEqual(parameter_output(q), string)
        self.assertEqual(parameter_output(r), string)
        self.assertEqual(parameter_output(q, verbose=False), '')
        self.assertEqual(parameter_output(r, verbose=False), '')
        
    def test_response(self):
        self.r.parameter_mode = 'response'
        self.ri.parameter_mode = 'response'
        self.r_Hz.parameter_mode = 'response'
        
        string = 'The value of parameter 1 is 123'
        index_string = 'The value of parameter 29, index 1 is 123'
        unit_string = 'The value of parameter 3 is 123 Hz'
        
        self.assertEqual(parameter_output(self.r), string)
        self.assertEqual(parameter_output(self.ri), index_string)
        self.assertEqual(parameter_output(self.r_Hz), unit_string)
        self.assertEqual(parameter_output(self.r, verbose=False), '123')
        self.assertEqual(parameter_output(self.r_Hz, verbose=False), '123 Hz')
        
    def test_error(self):
        self.r.parameter_mode = 'error'
        self.ri.parameter_mode = 'error'
        self.r.error_code = ParameterError.MINMAX.value
        self.ri.error_code = ParameterError.MINMAX.value
        
        string = "Can't access parameter 1: min/max restriction"
        index_string = (
            "Can't access parameter 29, index 1: min/max restriction")
        
        self.assertEqual(parameter_output(self.r), string)
        self.assertEqual(parameter_output(self.ri), index_string)
        self.assertEqual(parameter_output(self.r, verbose=False), 
                         'Error: min/max restriction')
        
    def test_no_write(self):
        self.r.parameter_mode = 'no write'
        self.ri.parameter_mode = 'no write'
        
        string = "Parameter 1 isn't writable"
        index_string = "Parameter 29 isn't writable"
        
        self.assertEqual(parameter_output(self.r), string)
        self.assertEqual(parameter_output(self.ri), index_string)
        self.assertEqual(parameter_output(self.r, verbose=False), 
                         'Not writable')


# Shorten lines by defining an alias:
out = control_or_status_output

class TestControlOrStatusOutput(Base):
    
    def test_normal(self):
        
        self.q = Query(control_or_status_set = {ControlBits.START_STOP, 
                                                   ControlBits.COMMAND})
        self.r = Reply(control_or_status_set = {StatusBits.TURNING, 
                                                StatusBits.ACCELERATION})

        control_string = ('Active control bits:\n'
                          '    Start/Stop\n'
                          '    Enable control bits 0, 5, 6, 7, 8, 13, 14, 15')
        status_string = ('Present status conditions:\n'
                         '    Accelerating\n'
                         '    Pump is turning')
        
        self.assertEqual(out(self.q), control_string)
        self.assertEqual(out(self.r), status_string)
        self.assertEqual(out(self.q, verbose=False), '')    
        self.assertEqual(out(self.r, verbose=False), '')    
        
    def test_errors_and_warnings(self):
        """Make sure control_or_status_output(wrapper, verbose=False) 
        doesn't return '' if there are errors or warnings present.
        """
        
        self.error   = Reply(control_or_status_set = {StatusBits.ERROR})
        self.warning = Reply(control_or_status_set = {StatusBits.WARNING})
        self.both    = Reply(control_or_status_set = {StatusBits.ERROR, 
                                                      StatusBits.WARNING})
        
        error_string = 'Error(s) present'
        warning_string = 'Warning(s) present'
        both_string = 'Error(s) present\nWarning(s) present'
        
        self.assertEqual(out(self.error, verbose=False), error_string)    
        self.assertEqual(out(self.warning, verbose=False), warning_string)    
        self.assertEqual(out(self.both, verbose=False), both_string)
        
        
class TestHardwareOutput(unittest.TestCase):
    
    def test_normal(self):
        q = Query(frequency=1000, temperature=30, current=100, voltage=120)
        r = Reply(frequency=1000, temperature=30, current=100, voltage=120)
        
        long_string = (
            'Stator frequency: 1000 Hz\n'
            'Frequency converter temperature: 30 °C\n'
            'Motor current: 100×0.1 A\n'
            'Intermediate circuit voltage: 120×0.1 V')
        
        short_string = (
            'f=1000 Hz\n'
            'T=30 °C\n'
            'I=100×0.1 A\n'
            'U=120×0.1 V')
        
        self.assertEqual(hardware_output(r), long_string)    
        self.assertEqual(hardware_output(r, verbose=False), short_string)   
        self.assertEqual(hardware_output(q), '')    
        self.assertEqual(hardware_output(q, verbose=False), '')    
        
    def test_setpoint(self):
        q = Query(frequency=1000, temperature=30, current=100, voltage=120, 
                  control_or_status_set = {ControlBits.COMMAND, 
                                           ControlBits.FREQ_SETPOINT})
        
        string = ('Stator frequency setpoint: 1000 Hz')
        
        self.assertEqual(hardware_output(q), string)    
        self.assertEqual(hardware_output(q, verbose=False), '')    
    
    
if __name__ == '__main__':
    unittest.main()