import unittest

from turboctl import AbstractUI, VirtualPump, Query, Reply

class Base(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.pump = VirtualPump()
        cls.ui = AbstractUI(cls.pump.port)
        
    @classmethod
    def tearDown(cls):
        cls.pump.close()
                
        
class TestReadAndWriteParameter(Base):
    
    def test_uint(self):
        q, r = self.ui.write_parameter(200, 1)
        
        self.assertEqual(q.parameter_mode, 'write')
        self.assertEqual(q.parameter_number, 1)
        self.assertEqual(q.parameter_index, 0)
        self.assertEqual(q.parameter_value, 200)
        
        self.assertEqual(r.parameter_mode, 'response')
        self.assertEqual(r.parameter_number, 1)
        self.assertEqual(r.parameter_index, 0)
        self.assertEqual(r.parameter_value, 200)
        
        q, r = self.ui.read_parameter(1)
        
        self.assertEqual(q.parameter_mode, 'read')
        self.assertEqual(q.parameter_number, 1)
        self.assertEqual(q.parameter_index, 0)
        self.assertEqual(q.parameter_value, 0)
        
        self.assertEqual(r.parameter_mode, 'response')
        self.assertEqual(r.parameter_number, 1)
        self.assertEqual(r.parameter_index, 0)
        self.assertEqual(r.parameter_value, 200)

        
    def test_sint(self):
        q, r = self.ui.read_parameter(1)

        
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