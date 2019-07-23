import unittest
import time
import os
from serial import Serial

from turboctl import VirtualConnection

class DummyVC(VirtualConnection):
    
    def process(self, input_):
        return b'reply to ' + input_
    
class Base(unittest.TestCase):
    
    def setUp(self):
        self.vc = DummyVC()
        
    def tearDown(self):
        self.vc.close()

class TestMessaging(Base):
    
    def setUp(self):
        super().setUp()
        self.vc.buffer_size = 6
        self.ser = Serial(port=self.vc.port, timeout=0.1)
        
    def tearDown(self):
        super().tearDown()
        self.ser.close()
        
    def test_message_smaller_than_vc_buffer(self):
        
        msg = b'hello'
        self.ser.write(msg)
        
        reply1 = self.ser.read(100)
        self.assertEqual(reply1, b'reply to hello')
        
        reply2 = self.ser.read(100)
        self.assertFalse(reply2)
            
    def test_message_larger_than_vc_buffer(self):
        
        msg = b'hello_there'
        self.ser.write(msg)
        
        reply = self.ser.read(100)
        self.assertEqual(reply, b'reply to hello_reply to there')
        
    def test_message_larger_than_vc_buffer_and_read_in_pieces(self):
        
        msg = b'hello_there'
        self.ser.write(msg)
        
        reply = self.ser.read(15)
        self.assertEqual(reply, b'reply to hello_')
        
        reply = self.ser.read(15)
        self.assertEqual(reply, b'reply to there')
        
        reply = self.ser.read(15)
        self.assertEqual(reply, b'')
        
    def test_multiple_messages(self):
        
        self.ser.write(b'hello')
        self.assertEqual(self.ser.read(100), b'reply to hello')
        
        self.ser.write(b'there')
        self.assertEqual(self.ser.read(100), b'reply to there')
                
        self.assertEqual(self.ser.read(100), b'')
        
class TestStartingAndStopping(Base):
        
    def test_init(self):
        self.assertTrue(self.vc.is_running)
        self.assertTrue(os.fstat(self.vc.user_end))
        self.assertTrue(os.fstat(self.vc.virtual_end))
        
    def test_close(self):
        self.vc.close()
        self.assertFalse(self.vc.is_running())
        
        # Asking the status of user_end and virtual_end should 
        # produce an error, since they are no longer valid file 
        # descriptors after they are closed.  
        with self.assertRaises(OSError):
            os.fstat(self.vc.user_end)
        with self.assertRaises(OSError):
            os.fstat(self.vc.virtual_end)
                    
    def test_close_all(self):
        
        vc1 = self.vc
        vc2 = DummyVC()
        vc3 = DummyVC()
        
        self.assertTrue(vc1.is_running())
        self.assertTrue(vc2.is_running())
        self.assertTrue(vc3.is_running())
        
        VirtualConnection.close_all()
        
        # It may take a nonzero amount of time for parallel threads to
        # finish executing. 
        time.sleep(0.01)        
        self.assertFalse(vc1.is_running())
        self.assertFalse(vc2.is_running())
        self.assertFalse(vc3.is_running())
        
    def test_init_after_close_all(self):
        VirtualConnection.close_all()
        vc = VirtualConnection()
        
        self.assertTrue(vc.is_running)
        self.assertTrue(os.fstat(vc.user_end))
        self.assertTrue(os.fstat(vc.virtual_end))
        
if __name__ == '__main__':
    unittest.main()