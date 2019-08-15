import unittest
    
from turboctl import (Telegram, Types, TelegramWrapper, Query, Reply, 
                      StatusBits)
from test_turboctl import dummy_parameter

class TestParameterMode(unittest.TestCase):

    def setUp(self):
        Reply.parameters = {
            1: dummy_parameter(size=16),
            2: dummy_parameter(size=16, indices=range(5)),
            3: dummy_parameter(size=32),
            4: dummy_parameter(size=32, indices=range(5))}
        
        self.r_invalid = Reply(parameter_number=0)
        self.r16 = Reply(parameter_number=1)
        self.r16F = Reply(parameter_number=2)
        self.r32 = Reply(parameter_number=3)
        self.r32F = Reply(parameter_number=4)

    def mode_test(self, name, code, query):
        query.parameter_mode = name
        self.assertEqual(query.parameter_access_type, code)
        self.assertEqual(query.parameter_mode, name)

    def test_none(self):
        self.mode_test('none', '0000', self.r16)
                
    def test_response_16(self):
        self.mode_test('response', '0001', self.r16)
        
    def test_response_32(self):
        self.mode_test('response', '0010', self.r32)
        
    def test_response_index_16(self):
        self.mode_test('response', '0100', self.r16F)
        
    def test_response_index_32(self):
        self.mode_test('response', '0101', self.r32F)
        
    def test_error(self):
        self.mode_test('error', '0111', self.r16)
        
    def test_no_write(self):
        self.mode_test('no write', '1000', self.r16)
        
    def test_invalid(self):
        self.mode_test('invalid', '1111', self.r16)
        
        
class TestStatusSet(unittest.TestCase):
    
    def test_empty(self):
        r = Reply()
        self.assertEqual(r.control_or_status_set, set())
        
    def test_set(self):
        r = Reply(control_or_status_set = {StatusBits.OPERATION, 
                                StatusBits.ACCELERATION})
        self.assertEqual(r.control_or_status_bits, '0010100000000000')
        
    def test_get(self):
        r = Reply(control_or_status_bits = '0010100000000000')
        self.assertEqual(r.control_or_status_set, {StatusBits.OPERATION, 
                                        StatusBits.ACCELERATION})     
            
    def test_add(self):
        r = Reply(control_or_status_bits = '0010000000000000')
        r.control_or_status_set.add(StatusBits.ACCELERATION)
        self.assertEqual(r.control_or_status_set, {StatusBits.OPERATION, 
                                        StatusBits.ACCELERATION})     
        self.assertEqual(r.control_or_status_bits, '0010100000000000')
            
    def test_remove(self):
        r = Reply(control_or_status_bits = '0010100000000000')
        r.control_or_status_set.remove(StatusBits.ACCELERATION)
        self.assertEqual(r.control_or_status_set, {StatusBits.OPERATION})
        self.assertEqual(r.control_or_status_bits, '0010000000000000')

            
class TestErrorMessage(unittest.TestCase):
    
    def setUp(self):
        
        Reply.parameters = {
            1: dummy_parameter(type_=Types.UINT),
            2: dummy_parameter(type_=Types.SINT),
            3: dummy_parameter(type_=Types.FLOAT)}
        
        self.r_uint = Reply(parameter_number=1, parameter_mode='error')
        self.r_sint = Reply(parameter_number=2, parameter_mode='error')
        self.r_float = Reply(parameter_number=3, parameter_mode='error')

    def test_error_message(self):
        
        for r in [self.r_uint, self.r_sint, self.r_float]:
            with self.subTest(i=r):
                string = 'impermissible parameter number'
                self.assertEqual(r.error_message, string)
        
                r.error_code=1
                string = 'parameter cannot be changed'
                self.assertEqual(r.error_message, string)

    def test_error_code(self):
        
        for r in [self.r_uint, self.r_sint, self.r_float]:
            with self.subTest(i=r):
                r.error_code = 5                
                self.assertEqual(r.error_code, 5)
                # Error code is the same as parameter value, but 
                # must always be read as an uint regardless of 
                # parameter type.
                self.assertEqual(Telegram.parameter_value.fget(r), 5)
                
    def test_invalid_code(self):
        self.r_uint.error_code = 99
        string = 'invalid error code: 99'
        self.assertEqual(self.r_uint.error_message, string)
        
    def test_invalid_type(self):
        # This raises a TypeError instead of ValueError since 
        # Types considers UINT and SINT to be different types.
        with self.assertRaises(TypeError):
            self.r_uint.error_code = -1
        
    def test_no_error_mode(self):
        r = Reply()
        self.assertEqual(r.error_message, '')
        
        
class TestUtils(unittest.TestCase):        
    
    def test_str(self):
        r = Reply()
        string = ("Reply(parameter_access_type='0000', "
                        "parameter_number=0, "
                        "parameter_index=0, "
                        "parameter_value=0, "
                        "control_or_status_bits='0000000000000000', "
                        "frequency=0, "
                        "temperature=0, "
                        "current=0, "
                        "voltage=0, "
                        "checksum=20, "
                        "parameter_type=Types.UINT, "
                        "parameter_size=0, "
                        "parameter_unit='', "
                        "parameter_indexed=False, "
                        "parameter_mode='none', "
                        "control_or_status_set=SynchronizedSet(), "
                        "error_code=0, "
                        "error_message='')"
        )
        
        self.maxDiff=None #Print long strings.
        self.assertEqual(str(r), string)
                
    def test_eq(self):
        
        self.assertEqual(Query(), Query())
        self.assertEqual(Query(), Reply())
        self.assertEqual(Query(), TelegramWrapper())
        self.assertEqual(Query(), Telegram())
        
        self.assertNotEqual(Query(), Query(parameter_number=1))
        self.assertNotEqual(Query(), Reply(parameter_number=1))
        self.assertNotEqual(Query(), TelegramWrapper(parameter_number=1))
        self.assertNotEqual(Query(), Telegram(parameter_number=1))
        
        
if __name__ == '__main__':
    unittest.main()