import unittest

from turboctl import Types, Telegram, TelegramWrapper
from test_turboctl import dummy_parameter

class TestInit(unittest.TestCase):
    
    def setUp(self):
        self.data = Telegram(current=1).data
        self.telegram = Telegram(self.data)
        TelegramWrapper.parameters = {1: dummy_parameter(type_=Types.SINT)}
                        
    def test_invalid_parameter_number(self):
        tw = TelegramWrapper(parameter_number=0)
        self.assertEqual(tw.parameter_number, 0)






from turboctl import Query             
        
class Test2(unittest.TestCase):
    
    def test(self):
        Query(parameter_number=2, parameter_mode = 'write')
        
if __name__ == '__main__':
    unittest.main()