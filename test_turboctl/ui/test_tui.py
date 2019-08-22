import unittest

#from turboctl.ui.tui import AbstractTUI
#from turboctl.ui.output import output
#from turboctl.virtualpump import VirtualPump


#class DummyTUI(AbstractTUI):
#    
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.output = ''
#            
#    def _print_output(self, query, reply):
#        self.output = '\n' + output(query, reply) + '\n'
#        
#    def run(self, string):
#        self.output = ''
#        super().process_input(string)
#        
#        
#class TestTUI(unittest.TestCase):
#    
#    @classmethod
#    def setUpClass(cls):
#        cls.vp = VirtualPump()
#        cls.ui = DummyTUI(cls.vp.port)
#        
#    @classmethod
#    def tearDownClass(cls):
#        cls.vp.close()
#    
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
#
#
#if __name__ == '__main__':
#    unittest.main()