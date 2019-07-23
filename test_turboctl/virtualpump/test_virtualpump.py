import unittest
import serial
import time
from copy import copy

from turboctl import (
    VirtualPump, 
    ParameterNumberError, 
    #CannotChangeError, 
    MinMaxError, 
    OtherError,
    Telegram, 
    Types, 
    TelegramWrapper, 
    Query, 
    Reply
)

from test_turboctl import dummy_parameter
    
class Base(unittest.TestCase):

    def setUp(self):
        
        parameter_dict = self.set_up_parameters()     
        TelegramWrapper.parameters = parameter_dict
        self.set_up_virtualpump(parameter_dict)     
        
    def set_up_parameters(self):
        
        def dp(number, type_, size, indexed, min_, max_, default):
            indices = range(1,4) if indexed else range(0)
            return dummy_parameter(number=number, indices=indices, 
                                   type_=type_, size=size, min_=min_, 
                                   max_=max_, default=default)
                   
        self.u16  = dp(1, Types.UINT, 16, True,  10, 10**4, 123)
        self.u32  = dp(2, Types.UINT, 32, True,  10, 10**8, 123456)
        self.u16F = dp(3, Types.UINT, 16, False, 10, 10**4, 123)
        self.u32F = dp(4, Types.UINT, 32, False, 10, 10**8, 123456)
        
        self.s16  = dp(5, Types.SINT, 16, True,  -10**5, 10**4, -123)
        self.s32  = dp(6, Types.SINT, 32, True,  -10**8, 10**8, -123456)
        self.s16F = dp(7, Types.SINT, 16, False, -10**4, 10**4, -123)
        self.s32F = dp(8, Types.SINT, 32, False, -10**8, 10**8, -123456)
        
        self.real  = dp( 9, Types.FLOAT, 32, True,  -1e8, 1e8, 123.456)
        self.realF = dp(10, Types.FLOAT, 32, False, -1e8, 1e8, 123.456)
        
        self.parameters = [self.u16, self.u32, self.u16F, self.u32F, self.s16, 
                          self.s32, self.s16F, self.s32F, self.real, 
                          self.realF]
        
        return {p.number: p for p in self.parameters}        
        
    def set_up_virtualpump(self, parameter_dict):
        
        self.vp = VirtualPump(parameter_dict)
        self.pc = self.vp.parameter_component

        self.connection = serial.Serial(
            port=self.vp.connection_component.port,
            timeout=0.1) 
        # A timeout has to be defined to prevent blocking.
        # The timeout is nonzero, since it takes a nonzero amount of 
        # time for the virtual pump to send data.

    def tearDown(self):
        self.vp.connection_component.close()
        self.connection.close()
    
    def read_test(self, parameter, value):
        index = 3 if parameter.indices else 0
        reply = self.access_parameter(parameter, 'read', index)
        self.check_response(reply, parameter, 'response', value, index)
    
    def write_test(self, parameter, value):
        index = 3 if parameter.indices else 0
        reply = self.access_parameter(parameter, 'write', index, value)
        self.check_response(reply, parameter, 'response', value, index)
        
    def write_error_test(self, parameter, value, error_class):
        index = 3 if parameter.indices else 0
        reply = self.access_parameter(parameter, 'write', index, value)
        self.check_error(reply, parameter, error_class)
        
    def read_error_test(self, parameter, value, error_class):
        index = 3 if parameter.indices else 0
        reply = self.access_parameter(parameter, 'read', index, value)
        self.check_error(reply, parameter, error_class)
            
    def access_parameter(self, parameter, mode, index, value=0):       
        q = Query(parameter_number=parameter.number)
        q.parameter_mode = mode
        q.parameter_index = index
        q.parameter_value = value
        self.connection.write(q.data)
        bytes_out = self.connection.read(q.LENGTH)

        return Reply(bytes_out)
    
    def check_response(self, reply, parameter, mode, value, index):
        r = reply
        
        #if r.parameter_mode == 'error':
        #    print(self.pc.latest_error)
        
        self.assertEqual(r.parameter_mode, mode)
        self.assertEqual(r.parameter_number, parameter.number)
        self.assertEqual(r.parameter_index, index)
        self.assertAlmostEqual(r.parameter_value, value, 5)
        
    def check_error(self, reply, parameter, error_class):
        r = reply
        self.assertEqual(r.parameter_mode, 'error')
        self.assertEqual(r.parameter_number, parameter.number)
        self.assertEqual(r.error_code, error_class.CODE)
        
        
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
            self.assertTrue(vp.connection_component.is_running())
        
        time.sleep(0.1)
        # The parallel thread must finish the current iteration before
        # stopping.
        self.assertFalse(vp.connection_component.is_running())

    def test_empty_telegram(self):
        
        parameter = dummy_parameter(number=0)
        reply = self.access_parameter(dummy_parameter(number=0), 'none', 0)       
        
        self.check_response(reply, parameter, 'none', 0, 0)
        self.assertFalse(reply.status_list)
        
        # Since a virtual pump returns random values for these,
        # one of these might be 0 by chance, and this test 
        # would fail. In this case, the test should be run again.
        self.assertTrue(reply.frequency)
        self.assertTrue(reply.temperature)
        self.assertTrue(reply.current)
        self.assertTrue(reply.voltage)

        
class TestBasic(Base):
            
    def test_read_defaults(self):
        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.read_test(p, value)

    def test_write_and_read(self):
        
        def half(value):
            return type(value)(value / 2)
        
        # Write a value to all parameters:
        for p in self.parameters:
            with self.subTest(i=p):
                value = half(p.default)
                self.write_test(p, value)
                
        # Read all written values:
        for p in self.parameters:
            with self.subTest(i=p):
                value = half(p.default)                
                self.read_test(p, value)
                
    def test_too_large_value_results_in_error(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = 2 * p.max
                self.write_error_test(p, value, MinMaxError)
                
    def test_too_small_value_results_in_error(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.min - abs(p.min)
                self.write_error_test(p, value, MinMaxError)
                
    def test_write_maximum_value(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.max
                self.write_test(p, value)
                
    def test_write_minimum_value(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.min
                self.write_test(p, value)


    
class TestNoWriteAccess(Base):
    
    def setUp(self):
        
        parameter_dict = self.set_up_parameters()    
        for p in self.parameters:
            p.writable = False    
            
        TelegramWrapper.parameters = parameter_dict
        self.set_up_virtualpump(parameter_dict)     
    
    def no_write_access_test(self, parameter, index, value):
        reply = self.access_parameter(parameter, 'write', index, value)
        self.check_response(reply, parameter, 'no write', value, index)

    def test_no_write_access(self):

        for p in self.parameters:
            p.writable = False            

            with self.subTest(i=p):                    
                index = 3 if p.indices else 0
                value = p.default                    
                self.no_write_access_test(p, index, value)
                
                
class TestInvalidNumber(Base):
    
    # access_parameter and check_error must be slightly modified 
    # for tests in this class.
    
    def access_parameter(self, parameter, mode, index, value=0):       
        
        q = Query(parameter_number=parameter.number)
        q.parameter_mode = mode
        q.parameter_index = index
        q.parameter_value = value
        
         # Set parameter number to 0 but keep 
        # everything else the same.
        t = Telegram(q.data)
        t.parameter_number = 0
        
        self.connection.write(t.data)
        bytes_out = self.connection.read(q.LENGTH)

        return Reply(bytes_out)
    
    def check_error(self, reply, parameter, error_class):
        r = reply
        self.assertEqual(r.parameter_mode, 'error')
        # Parameter number is 0 instead of parameter.number.
        self.assertEqual(r.parameter_number, 0)
        self.assertEqual(r.error_code, error_class.CODE)

    def test_read_invalid_parameter_number(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.read_error_test(p, value, ParameterNumberError)
                
    def test_write_invalid_parameter_number(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.write_error_test(p, value, ParameterNumberError)
                

class TestWrongSize(Base):
    
    def setUp(self):
        
        parameter_dict = self.set_up_parameters()     
        TelegramWrapper.parameters = parameter_dict
        
        sizes_wrong_dict = {}
        for key, parameter in parameter_dict.items():
            new_parameter = copy(parameter)
            
            if parameter.size == 16:
                new_parameter.size = 32
            elif parameter.size == 32:
                new_parameter.size = 16
            else:
                raise ValueError(f'Invalid parameter.size: {parameter.size}')
            
            sizes_wrong_dict[key] = new_parameter
        
        self.set_up_virtualpump(sizes_wrong_dict)

    def test_write_wrong_size(self):
        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.write_error_test(p, value, OtherError)
                
    def test_read_wrong_size(self):
        
        # Read access doesn't specify size, so reading parameters 
        # with a wrong size should succeed.
        
        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.read_test(p, value)
                
                
class TestIndexedParametersAsUnindexed(Base):
    
    def setUp(self):
        
        parameter_dict = self.set_up_parameters()     
        TelegramWrapper.parameters = parameter_dict
        
        indices_wrong_dict = {}
        for key, parameter in parameter_dict.items():
            new_parameter = copy(parameter)
            
            if parameter.indices:
                new_parameter.indices = range(0)
            else:
                new_parameter.indices = range(1, 4)
            
            indices_wrong_dict[key] = new_parameter
        
        self.set_up_virtualpump(indices_wrong_dict)

    def test_indexed_parameters_as_unindexed_and_vice_versa(self):
        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                self.write_error_test(p, value, OtherError)
                
                
class TestIndexError(Base):
    
    def read_index_test(self, parameter, value, index):
        reply = self.access_parameter(parameter, 'read', index)
        self.check_response(reply, parameter, 'response', value, index)
    
    def write_index_test(self, parameter, value, index):
        reply = self.access_parameter(parameter, 'write', index, value)
        self.check_response(reply, parameter, 'response', value, index)
    
    def read_index_error_test(self, parameter, value, index, error_class):
        reply = self.access_parameter(parameter, 'read', index, value)
        self.check_error(reply, parameter, error_class)
        
    def write_index_error_test(self, parameter, value, index, error_class):
        reply = self.access_parameter(parameter, 'write', index, value)
        self.check_error(reply, parameter, error_class)

    def test_write_index_too_large(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                index = 5
                
                if p.indices:
                    self.write_index_error_test(p, value, index, OtherError)
                else:
                    # Index doesn't matter for unindexed parameters.
                    self.write_index_test(p, value, index)
                    
    def test_write_index_too_small(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                index = 0
                
                if p.indices:
                    self.write_index_error_test(p, value, index, OtherError)
                else:
                    self.write_index_test(p, value, index)
                    
    def test_read_index_too_large(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                index = 5
                
                if p.indices:
                    self.read_index_error_test(p, value, index, OtherError)
                else:
                    self.read_index_test(p, value, index)
                    
    def test_read_index_too_small(self):

        for p in self.parameters:
            with self.subTest(i=p):
                value = p.default
                index = 0
                
                if p.indices:
                    self.read_index_error_test(p, value, index, OtherError)
                else:
                    self.read_index_test(p, value, index)
                    

class TestReferencesToOtherParameters(Base):
    
    def set_up_parameters(self):
        
        def dp(number, min_, max_, default):
            return dummy_parameter(number=number, type_=Types.SINT, min_=min_, 
                                   max_=max_, default=default)
                   
        self.lower = dp(1, -100, 100, -1)
        self.upper = dp(100, -100, 100, 1)
        # The number is 100 in order to make sure references can be 
        # more than 1 digit long.
        self.middle = dp(5, 'P1', 'P100', 0)        
        self.parameters = [self.lower, self.middle, self.upper]        
        return {p.number: p for p in self.parameters}        

    def test_min_reference(self):
        self.assertEqual(self.pc.parameters[5].min_value, -1)
        self.write_test(self.lower, -2)
        self.assertEqual(self.pc.parameters[5].min_value, -2)
        
    def test_max_reference(self):
        self.assertEqual(self.pc.parameters[5].max_value, 1)
        self.write_test(self.upper, 2)
        self.assertEqual(self.pc.parameters[5].max_value, 2)
        
    def test_changing_min_and_max(self):
        
        # The value 5 is out of range.
        self.write_error_test(self.middle, 5, MinMaxError)
        # Raise the maximum value.
        self.write_test(self.upper, 5)
        # The value is now allowed.
        self.write_test(self.middle, 5)
        
        # The same for the minimum value.
        self.write_error_test(self.middle, -5, MinMaxError)
        self.write_test(self.lower, -5)
        self.write_test(self.middle, -5)
        

class TestDefaults(Base):

    def set_up_parameters(self):
        
        def dp(number, indexed, default):
            indices = range(1,4) if indexed else range(0)
            return dummy_parameter(number=number, indices=indices, 
                                   default=default)
                   
        self.unindexed = dp(1, False, 1)
        self.single = dp(2, True, 2)
        self.multiple = dp(3, True, [3,4,5])
        
        self.parameters = [self.unindexed, self.single, self.multiple]        
        return {p.number: p for p in self.parameters}        

    def test_unindexed_default(self):
        self.assertEqual(self.pc.parameters[1].default_value, 1)
        self.read_test(self.unindexed, 1)
        
    def test_indexed_single_default(self):
        self.assertEqual(self.pc.parameters[2].default_value, [2,2,2])
        self.read_test(self.single, 2)
        
    def test_indexed_multiple_default(self):
        self.assertEqual(self.pc.parameters[3].default_value, [3,4,5])
        self.read_test(self.multiple, 5)
        
        
if __name__ == '__main__':
    unittest.main()