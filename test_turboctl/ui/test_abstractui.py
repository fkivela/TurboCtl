import unittest

from turboctl import AbstractUI, VirtualPump, Query, Reply, Types, PARAMETERS, ParameterError
from test_turboctl import dummy_parameter

new_parameters = [
    dummy_parameter(number=2001, type_=Types.UINT),
    dummy_parameter(number=2002, type_=Types.SINT, min_ = -1000),
    dummy_parameter(number=2003, type_=Types.FLOAT, min_ = -1000),
    dummy_parameter(number=2004, indices=range(5)),
    dummy_parameter(number=2005, writable=False),
    # 2006: wrong num
    # 2007: cannot change
    dummy_parameter(number=2008, max_=10),
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
        self.read_and_write(123.456, 2003, 0)
        
    def test_indexed(self):
        self.read_and_write(123, 2004, 3)
        
    def test_no_write(self):
        q, r = self.ui.write_parameter(123, 2005, 0)
        
        self.assertEqual(r.parameter_mode, 'no write')
        self.assertEqual(r.parameter_number, 2005)
        self.assertEqual(r.parameter_index, 0)
        self.assertEqual(r.parameter_value, 123)
        
    def test_error_wrong_num(self):
        q, r = self.ui.write_parameter(123, 2006, 0)
        self.assertEqual(r.parameter_mode, 'error')
        self.assertEqual(r.error_code, ParameterError.WRONG_NUM)
        
    def test_error_minmax(self):
        q, r = self.ui.write_parameter(11, 2008, 0)
        self.assertEqual(r.parameter_mode, 'error')
        self.assertEqual(r.error_code, ParameterError.MINMAX)
        
    # Cannot change
    
    def test_error_other(self):
        q, r = self.ui.write_parameter(11, 2008, 0)
        self.assertEqual(r.parameter_mode, 'error')
        self.assertEqual(r.error_code, ParameterError.MINMAX)

    
        
        
        
        
#    WRONG_NUM     = (0, 'impermissible parameter number')
#    CANNOT_CHANGE = (1, 'parameter cannot be changed')
#    MINMAX        = (2, 'min./max. restriction')
#    OTHER         = (18, 'all other errors')


        
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

#class TestCommands(Base):
#    
##    def test_pump_on(self):
##        query, reply = self.ui.on_off()
##        
##        correct_bits = [2,22,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,17]
##        correct_query = Query(correct_bits)
##        
##        self.assertEqual(query, reply, correct_query)
#    
#    def test_turn_on_and_off(self):
#        q, r = read_parameter(args)
#        val = r.parameter_value
#
#    
#    def test_status(self):
#    
#        query, reply = self.ui.status()
#        
#        correct_bits = [2,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20]
#        correct_query = Query(correct_bits)
#        
#        self.assertEqual(query, reply, correct_query)
        
        
        
        
        
        
#    def test_read_parameter(self):
        
        
        
        
        
    
        
if __name__ == '__main__':
    unittest.main()