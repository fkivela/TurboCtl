"""Unit tests for the parameter_component module."""

import unittest

from turboctl.telegram.codes import (AccessError, MinMaxError,
                                     ParameterIndexError, WrongNumError)
from turboctl.telegram.datatypes import Uint, Sint, Float
from turboctl.telegram.telegram import TelegramBuilder, TelegramReader
from turboctl.virtualpump.parameter_component import (ExtendedParameters,
                                                      ParameterComponent)
from test_turboctl.telegram.test_parser import dummy_parameter


class Base(unittest.TestCase):
    
    ### Set-up ###

    def setUp(self):
        self.parameters = self.set_up_parameters()
        self.extended_parameters = ExtendedParameters(self.parameters)
        self.pc = ParameterComponent(self.extended_parameters)
        
    def set_up_parameters(self):
        # Testing is easier with a custom parameter set instead of actual pump
        # parameters.
        
        def dp(number, datatype, bits, indexed, min_value, max_value, default):
            return dummy_parameter(
                number=number,
                indices=range(1,4) if indexed else range(0), 
                datatype=datatype,
                bits=bits,
                min_value=datatype(min_value, bits),
                max_value=datatype(max_value, bits),
                default=datatype(default, bits)
            )
        
        self.u16  = dp(1, Uint, 16, False, 10, 10**4, 123)
        self.u32  = dp(2, Uint, 32, False, 10, 10**8, 123456)
        self.u16F = dp(3, Uint, 16, True,  10, 10**4, 123)
        self.u32F = dp(4, Uint, 32, True,  10, 10**8, 123456)
        
        self.s16  = dp(5, Sint, 16, False, -10**4, 10**4, -123)
        self.s32  = dp(6, Sint, 32, False, -10**8, 10**8, -123456)
        self.s16F = dp(7, Sint, 16, True,  -10**4, 10**4, -123)
        self.s32F = dp(8, Sint, 32, True,  -10**8, 10**8, -123456)
        
        self.real  = dp( 9, Float, 32, False, -1e8, 1e8, 123.456)
        self.realF = dp(10, Float, 32, True,  -1e8, 1e8, 123.456)
        
        parameters = [self.u16, self.u32, self.u16F, self.u32F, self.s16, 
                      self.s32, self.s16F, self.s32F, self.real, self.realF]
        return {p.number: p for p in parameters}    
        
    ### Generic testing functionality ###
                
    def access_parameter(self, number, mode, value, index):
        if index == None:
            index = 2 if self.parameters[number].indices else 0
 
        builder = (TelegramBuilder(self.parameters)
                   .set_parameter_number(number)
                   .set_parameter_mode(mode)
                   .set_parameter_index(index)
                   .set_parameter_value(value))
            
        query = TelegramReader(builder.build('query'), 'query')
        # The reply initially contains the same data as the query, so we can
        # use the builder used to build the query as a basis for the reply.
        self.pc.handle_parameter(query, builder)
        reply = TelegramReader(builder.build('reply'), 'reply')
        
        return reply
    
    def check_response(self, reply, number, mode, value, index):
        if index == None:
            index = 2 if self.parameters[number].indices else 0
        
        self.assertEqual(reply.parameter_mode, mode)
        self.assertEqual(reply.parameter_number, number)
        self.assertEqual(reply.parameter_index, index)
        # assertAlmostEqual is used because the use of floats may cause a
        # slight difference between the values.
        self.assertAlmostEqual(reply.parameter_value, value, 5)
        
    def check_error(self, reply, number, error_class):
        self.assertEqual(reply.parameter_mode, 'error')
        self.assertEqual(reply.parameter_number, number)
        self.assertEqual(reply.parameter_error, error_class.member)
        
    ### Generic tests for different purposes ###
        
    def read_test(self, number, value, index=None):
        value_in = 0.0 if self.parameters[number].datatype == Float else 0
        reply = self.access_parameter(number, 'read', value_in, index)
        self.check_response(reply, number, 'response', value, index)
    
    def write_test(self, number, value, index=None):
        reply = self.access_parameter(number, 'write', value, index)
        self.check_response(reply, number, 'response', value, index)
        
    def no_write_access_test(self, number, value, index=None):
        reply = self.access_parameter(number, 'write', value, index)
        self.check_response(reply, number, 'no write', value, index)
        
    def write_error_test(self, number, value, error_class, index=None):
        reply = self.access_parameter(number, 'write', value, index)
        self.check_error(reply, number, error_class)
        
    def read_error_test(self, number, value, error_class, index=None):
        reply = self.access_parameter(number, 'read', value, index)
        self.check_error(reply, number, error_class)
        
        
class TestDefaults(Base):
    """Make sure ExtendedParameter objects set their default values correctly.
    """

    def set_up_parameters(self):
        
        def dp(number, indexed, default):
            indices = range(1,4) if indexed else range(0)
            return dummy_parameter(number=number, indices=indices, 
                                   default=default)
                   
        self.unindexed = dp(1, False, Uint(1, 16))
        self.single = dp(2, True, Uint(2, 16))
        self.multiple = dp(3, True, [Uint(3, 16), Uint(4, 16), Uint(5, 16)])
        
        parameters = [self.unindexed, self.single, self.multiple]        
        return {p.number: p for p in parameters}        

    def test_unindexed(self):
        """Test an unindexed parameter."""
        self.assertEqual(self.pc.parameters[1].value, [Uint(1, 16)])
        self.read_test(self.unindexed.number, 1)
        
    def test_indexed_one(self):
        """Test an indexed parameter with one default value."""
        values = 3 * [Uint(2, 16)]
        self.assertEqual(self.pc.parameters[2].value, values)
        self.read_test(self.single.number, 2)
        
    def test_indexed_multiple(self):
        """Test an indexed parameter with multiple default values."""
        values = [Uint(x, 16) for x in (3, 4, 5)]
        self.assertEqual(self.pc.parameters[3].value, values)
        self.read_test(self.multiple.number, value=3, index=1)
        self.read_test(self.multiple.number, value=4, index=2)
        self.read_test(self.multiple.number, value=5, index=3)
        

class TestReadWrite(Base):
    """Test the basic reading and writing functionality of ParameterComponent.
    """
    
    def test_no_access(self):
        # If the partameter isn't accessed, the reply will just be a copy of
        # the query.
        reply = self.access_parameter(0, 'none', 12, 34)
        self.check_response(reply, 0, 'none', 12, 34)
                    
    def test_read_defaults(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                self.read_test(parameter.number, parameter.default.value)

    def test_write_and_read_single_value(self):
        
        def half(value):
            return type(value)(value / 2)
        
        # Write and read a value for all parameters.
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = half(parameter.default.value)
                self.write_test(parameter.number, value)
                self.read_test(parameter.number, value)
                
    def test_write_and_read_all_indices(self):
        
        def half(value):
            return type(value)(value / 2)
        
        # Write and read a value for all parameters.
        for parameter in self.parameters.values():
            if parameter.indices:
                with self.subTest(i=parameter.number):
                    
                    value1 = half(parameter.default.value)
                    value2 = 2 * parameter.default.value
                    value3 = 4 * parameter.default.value
                    
                    self.write_test(parameter.number, value1, index=1)
                    self.write_test(parameter.number, value2, index=2)
                    self.write_test(parameter.number, value3, index=3)
                    
                    self.read_test(parameter.number, value1, index=1)
                    self.read_test(parameter.number, value2, index=2)
                    self.read_test(parameter.number, value3, index=3)
                
    # TODO: This needs testing with the real pump to implement correctly.
    # def test_no_write_access(self):
    #     # A 'no write' response isn't an error, so it's tested here.
    #     for parameter in self.parameters.values():
    #         self.pc.parameters[parameter.number].writable = False
    #         with self.subTest(i=parameter.number):                    
    #             self.no_write_access_test(parameter.number,
    #                                       parameter.default.value)
                

class TestLimits(Base):
    """Make sure min_value and max_value work correctly when they are costant
    values.
    """
                
    def test_value_too_large(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = 2 * parameter.max_value.value
                self.write_error_test(parameter.number, value, MinMaxError)
                
    def test_value_too_small(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                min_val = parameter.min_value.value
                value = min_val - abs(min_val)
                self.write_error_test(parameter.number, value, MinMaxError)
                
    def test_maximum_value(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = parameter.max_value.value
                self.write_test(parameter.number, value)
                
    def test_minimum_value(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = parameter.min_value.value
                self.write_test(parameter.number, value)
                
                
class TestLimitsAsReferences(Base):
    """Make sure min_value and max_value also work correctly when they are
    references to other parameters.
    """
    
    def set_up_parameters(self):
        
        def dp(number, min_value, max_value, default):
            if not isinstance(min_value, str):
                min_value = Sint(min_value, 16)
            
            if not isinstance(max_value, str):
                max_value = Sint(max_value, 16)
            
            return dummy_parameter(number=number, datatype=Sint,
                                   min_value=min_value, max_value=max_value,
                                   default=Sint(default, 16))
                   
        self.lower = dp(  1, -100, 100, -1)
        self.upper = dp(100, -100, 100,  1)
        # The number is 100 in order to make sure references can be 
        # more than 1 digit long.
        self.middle = dp(5, 'P1', 'P100', 0)        
        parameters = [self.lower, self.middle, self.upper]        
        return {p.number: p for p in parameters}

    def test_min_value_as_reference(self):
        self.assertEqual(self.pc.parameters[5].min_value, Sint(-1, 16))
        self.write_test(self.lower.number, -2)
        self.assertEqual(self.pc.parameters[5].min_value, Sint(-2, 16))
        
    def test_max_value_as_reference(self):
        self.assertEqual(self.pc.parameters[5].max_value, Sint(1, 16))
        self.write_test(self.upper.number, 2)
        self.assertEqual(self.pc.parameters[5].max_value, Sint(2, 16))
        
    def test_variable_min_and_max_value(self):
        
        # The value 5 is out of range.
        self.write_error_test(self.middle.number, 5, MinMaxError)
        # Raise the maximum value.
        self.write_test(self.upper.number, 5)
        # The value is now allowed.
        self.write_test(self.middle.number, 5)
        
        # The same for the minimum value.
        self.write_error_test(self.middle.number, -5, MinMaxError)
        self.write_test(self.lower.number, -5)
        self.write_test(self.middle.number, -5)


class TestStr(Base):
    """Test ExtendedParameter.__str__."""
    
    def set_up_parameters(self):
        # Copy the parameters from TestLimitsAsReferences.set_up_parameters,
        # since that class tests references too.
        return TestLimitsAsReferences.set_up_parameters(self)
        
    def test_str(self):
        correct_string = """
ExtendedParameter(
    number=5,   
    indices=range(0, 0),
    min_value='P1' (Sint(-1, bits=16)),
    max_value='P100' (Sint(1, bits=16)),
    default=Sint(0, bits=16),
    writable=True,
    datatype=Sint,
    bits=16,
    value=[Sint(0, bits=16)]
)
"""[1:-1]
        string = str(self.pc.parameters[self.middle.number])
        self.assertEqual(string, correct_string)
        
    def test_str_with_references(self):
        correct_string = """
ExtendedParameter(
    number=1,   
    indices=range(0, 0),
    min_value=Sint(-100, bits=16),
    max_value=Sint(100, bits=16),
    default=Sint(-1, bits=16),
    writable=True,
    datatype=Sint,
    bits=16,
    value=[Sint(-1, bits=16)]
)
"""[1:-1]
        string = str(self.pc.parameters[self.lower.number])
        self.assertEqual(string, correct_string)


class TestInvalidNumber(Base):
    """Make sure that an invalid parameter number results in the correct
    error code.
    """
    
    def setUp(self):
        super().setUp()
        # TelegramBuilder usually raises an error if it is told to build a
        # telegram that accesses an invalid parameter.
        # This can be circumvented by using different parameter dictionaries in
        # TelegramBuilder and ParameterComponent.
        new_parameters = {0: dummy_parameter(number=0)} 
        self.builder = TelegramBuilder(new_parameters).set_parameter_number(0)
    
    def test_read_invalid_parameter_number(self):  
        self.builder.set_parameter_mode('read')
        
        query = TelegramReader(self.builder.build('query'), 'query')
        self.pc.handle_parameter(query, self.builder)
        reply = TelegramReader(self.builder.build('reply'), 'reply')
        
        self.assertEqual(reply.parameter_error.exception, WrongNumError)
        
    def test_write_invalid_parameter_number(self):  
        self.builder.set_parameter_mode('write')
        
        query = TelegramReader(self.builder.build('query'), 'query')
        self.pc.handle_parameter(query, self.builder)
        reply = TelegramReader(self.builder.build('reply'), 'reply')
        
        self.assertEqual(reply.parameter_error.exception, WrongNumError)

                                
class TestWrongBits(Base):
    """Make sure that accessing a 16-bit parameter with a 32-bit mode or vice
    versa results in the correct error code.
    """
    
    def setUp(self):
        super().setUp()
        for parameter in self.pc.parameters.values():
            parameter.bits = 32 if parameter.bits == 16 else 16

    def test_write_wrong_size(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = parameter.default.value
                self.write_error_test(parameter.number, value, AccessError)
                
    def test_read_wrong_size(self):
        # Read access doesn't specify size, so reading parameters 
        # with a wrong size should succeed.
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = parameter.default.value
                self.read_test(parameter.number, value)
                
                
class TestWrongIndexed(Base):
    """Make sure that accessing an indexed parameter with an unindexed mode
    or vice versa results in the correct error code.
    """
    
    def setUp(self):
        super().setUp()
        # TODO: This might change if the implementation is changed
        for parameter in self.pc.parameters.values():
            parameter.indices = range(0) if parameter.indices else range(5)

    def test_wrong_indexed(self):
        for parameter in self.parameters.values():
            with self.subTest(i=parameter.number):
                value = parameter.default.value
                self.write_error_test(parameter.number, value, AccessError)
                
                
class TestIndexError(Base):
    """Make sure that accessing an invalid index of a parameter results in the
    correct error code.
    """
    
    def test_read_write_index_too_large(self):
        for parameter in self.parameters.values():
            if parameter.indices:
                with self.subTest(i=parameter.number):
                    value = parameter.default.value
                    index = 5
                    self.read_error_test(
                        parameter.number, value, ParameterIndexError, index)
                    self.write_error_test(
                        parameter.number, value, ParameterIndexError, index)
                    
    def test_read_write_index_too_small(self):
        for parameter in self.parameters.values():
            if parameter.indices:
                with self.subTest(i=parameter.number):
                    value = parameter.default.value
                    index = 0
                    self.read_error_test(
                        parameter.number, value, ParameterIndexError, index)
                    self.write_error_test(
                        parameter.number, value, ParameterIndexError, index)
                    

if __name__ == '__main__':
    unittest.main()