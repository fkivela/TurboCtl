import unittest
    
from turboctl import Telegram, TelegramWrapper, Query, Reply, ControlBits
from test_turboctl import dummy_parameter

class TestParameterMode(unittest.TestCase):
    
    def setUp(self):
        
        Query.parameters = {
            1: dummy_parameter(size=16),
            2: dummy_parameter(size=16, indices=range(5)),
            3: dummy_parameter(size=32),
            4: dummy_parameter(size=32, indices=range(5))}
        
        self.q_invalid = Query(parameter_number=0)
        self.q16 = Query(parameter_number=1)
        self.q16F = Query(parameter_number=2)
        self.q32 = Query(parameter_number=3)
        self.q32F = Query(parameter_number=4)
        
    def mode_test(self, name, code, query):
        query.parameter_mode = name
        self.assertEqual(query.parameter_access_type, code)
        self.assertEqual(query.parameter_mode, name)
        
    def test_none(self):        
        self.mode_test('none', '0000', self.q16)
        
    def test_read(self):
        self.mode_test('read', '0001', self.q16)
        
    def test_write_16(self):
        self.mode_test('write', '0010', self.q16)
        
    def test_write_32(self):
        self.mode_test('write', '0011', self.q32)
        
    def test_read_index(self):
        self.mode_test('read', '0110', self.q16F)
        
    def test_write_index_16(self):
        self.mode_test('write', '0111', self.q16F)
        
    def test_write_index_32(self):
        self.mode_test('write', '1000', self.q32F)
        
    def test_invalid(self):
        self.mode_test('invalid', '1111', self.q16)
        
    def test_default(self):
        self.assertEqual(self.q_invalid.parameter_access_type, '0000')
        self.assertEqual(self.q_invalid.parameter_mode, 'none')
        
    def test_invalid_parameter_number(self):

        self.q_invalid.parameter_mode = 'none'
        self.assertEqual(self.q_invalid.parameter_mode, 'none')

        self.q_invalid.parameter_mode = 'invalid'
        self.assertEqual(self.q_invalid.parameter_mode, 'invalid')
        
        with self.assertRaises(ValueError):
            self.q_invalid.parameter_mode = 'write'
            
        with self.assertRaises(ValueError):
            self.q_invalid.parameter_mode = 'read'
            
    def test_invalid_value_fails(self):
        with self.assertRaises(ValueError):
            self.q16.parameter_mode = 'test'
            
    def test_invalid_type_fails(self):
        with self.assertRaises(TypeError):
            self.q16.parameter_mode = 1

        
class TestControlSet(unittest.TestCase):
    
    def test_empty(self):
        q = Query()
        self.assertEqual(q.control_or_status_set, set())
        
    def test_set(self):
        q = Query(control_or_status_set=({ControlBits.START_STOP, 
                                          ControlBits.COMMAND}))
        self.assertEqual(q.control_or_status_bits, '1000000000100000')
        
    def test_get(self):
        q = Query(control_or_status_bits = '1000000000100000')
        self.assertEqual(q.control_or_status_set, {ControlBits.START_STOP, 
                                                   ControlBits.COMMAND})
            
    def test_add(self):
        q = Query(control_or_status_bits = '1000000000000000')
        q.control_or_status_set.add(ControlBits.COMMAND)
        self.assertEqual(q.control_or_status_set, {ControlBits.START_STOP, 
                                                   ControlBits.COMMAND})
        self.assertEqual(q.control_or_status_bits, '1000000000100000')
            
    def test_remove(self):
        q = Query(control_or_status_bits = '1000000000100000')
        q.control_or_status_set.remove(ControlBits.COMMAND)
        self.assertEqual(q.control_or_status_set, {ControlBits.START_STOP})
        self.assertEqual(q.control_or_status_bits, '1000000000000000')

            
class TestUtils(unittest.TestCase):
    
    def test_str(self):
        q = Query()
        string = ("Query(parameter_access_type='0000', "
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
                        "control_or_status_set=SynchronizedSet())")
        
        self.maxDiff=None #Print long strings.
        self.assertEqual(str(q), string)
                
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