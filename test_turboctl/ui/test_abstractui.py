import unittest
import enum as e
from collections import namedtuple

from turboctl.ui.abstractui import AbstractUI
from turboctl.virtualpump import VirtualConnection
from turboctl.telegram.test.test_parameters import TEST_PARAMETERS
from turboctl.telegram import telegram_wrapper

telegram_wrapper.PARAMETERS = TEST_PARAMETERS
Query = telegram_wrapper.Query
Reply = telegram_wrapper.Reply

        
class ReplyMode(e.Enum):
    
    MIRROR = e.auto()
    NO_REPLY = e.auto()
    WRONG_LENGTH = e.auto()
    INVALID_CONTENT = e.auto()
    CONSTANT = e.auto()

class DummyVC(VirtualConnection):
    
    def __init__(self, *args, **kwargs):
        self.mode = ReplyMode.MIRROR
        super().__init__(*args, **kwargs)
        
    def process(self, input_):
        
        if self.mode == ReplyMode.MIRROR:
            return super().process(input_)
        
        if self.mode == ReplyMode.NO_REPLY:
            return b''
        
        if self.mode == ReplyMode.WRONG_LENGTH:
            return bytes(10)
        
        if self.mode == ReplyMode.INVALID_CONTENT:
            return bytes(24)
        
        if self.mode == ReplyMode.CONSTANT:
            return self.reply.data
        
        raise ValueError(f'Invalid mode: {self.mode}')
        
class Base(unittest.TestCase):
    
    def setUp(self):
        self.vc = DummyVC(buffer_size=Query.LENGTH)
        self.port = self.vc.port
        self.invalid_port = 'invalid_port'
        self.ui = AbstractUI(self.port)
        self.ui_invalid_port = AbstractUI(self.invalid_port)
        self.maxDiff = None # Print long strings when comparing them
        
    def tearDown(self):
        self.vc.close()

class TestInit(Base):
    
    def test_initial_attributes_for_valid_port(self):
        self.assertTrue(self.ui.connection)
        self.assertEqual(self.ui.port, self.port)
        
    def test_initial_attributes_for_invalid_port(self):
        self.assertEqual(self.ui_invalid_port.connection, None)
        self.assertEqual(self.ui_invalid_port.port, self.invalid_port)
                
class TestSend(Base):
    
    def test_success(self):
        query, reply = self.ui._send(Query())
        
        self.assertTrue(isinstance(query, Query))
        self.assertTrue(isinstance(reply, Reply))
        self.assertEqual(query, Query())
        
    def test_failure(self):
        
        for mode in ['NO_REPLY', 'WRONG_LENGTH', 'INVALID_CONTENT']:
            with self.subTest(i=mode):
                self.vc.mode = ReplyMode[mode]
        
                with self.assertRaises(ValueError):
                    q, r = self.ui._send(Query())

class TestCommands(Base):
    
    def test_pump_on(self):
        query, reply = self.ui.on_off()
        
        correct_bits = [2,22,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,0,0,0,0,17]
        correct_query = Query(correct_bits)
        
        self.assertEqual(query, reply, correct_query)
        
        
    def test_status(self):
    
        query, reply = self.ui.status()
        
        correct_bits = [2,22,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20]
        correct_query = Query(correct_bits)
        
        self.assertEqual(query, reply, correct_query)
        
        
        
        
        
        
        
        
        
        
        
        
        # No.  Designation                      Min.    Max.    Default                     Unit     r/w Format Description
1      "Test parameter 1"               0       100     10                          "0.1 Â°C" r/w u16    "Test description 1" 
2[1:5] "Test parameter 2\nAnother line" 0       100     1                           ""       r   u16    "Test description 2\nwith two lines"
3       ""                              0       100     0                           ""       r/w u16    ""
4[1:5]  ""                              0       100     [1,2,3,4,5]                 ""       r   u16    ""
5       ""                              0       100     0                           ""       r/w u32    ""
6[1:5]  ""                              0       100     0                           ""       r   u32    ""
7       ""                              0       100     0                           ""       r/w u32    ""
8[1:5]  ""                              0       100     0                           ""       r   u32    ""
9       ""                              -50     50      -10                         ""       r/w s16    ""
10[1:5] ""                              -50     50      [-1,-2,-3,-4,-5]            ""       r   s16    ""
11      ""                              -50     50      0                           ""       r/w s16    ""
12[1:5] ""                              -50     50      0                           ""       r   s16    ""
13      ""                              -50     50      0                           ""       r/w s32    ""
14[1:5] ""                              -50     50      0                           ""       r   s32    ""
15      ""                              -50     50      0                           ""       r/w s32    ""
16[1:5] ""                              -50     50      0                           ""       r   s32    ""
17      ""                              -1.2e-3 1.2e3   -1.0                        ""       r/w real32 ""
18[1:5] ""                              -1.2e-3 1.2e3   1.0                         ""       r   real32 ""
19      ""                              P17     P18     0                           ""       r/w real32 ""
20[1:5] ""                              -1.2e-3 1.2e3   [1.0,2.0,3.0,4.0,5.0]       ""       r   real32 ""
        
        
        
        
        
        
        
        
        
    def test_write_parameter(self):
        
        TestParameter = namedtuple('TestParameter', 'format, number, index, value, uint_value')
        TestParameter(
        
        
        [
        ('u16',      1, 0,  5,            5),
        ('u16F',     2, 1,  5,            5),
        ('u32',      5, 0,  5,            5),
        ('u32F'      6, 1,  5,            5),
        ('s16'       9, 0, -5,   4294967291),
        ('s16F'     10, 1, -5,   4294967291),
        ('s32'      13, 0, -5,   4294967291),
        ('s32F'     14, 1, -5,   4294967291),
        ('real32',  17, 0,  5.5, 1085276160),
        ('real32F', 18, 1,  5.5, 1085276160)
        ]


        [2, 22, 0, 10, 96] + 18*[0] + [106]

        for p in parameters:
            with self.subTest(i=p):
                if index:
                    query, _ = self.ui.write_parameter(value=p.value, number=p.number)
                else:
                    query, _ = self.ui.write_parameter(value=p.value, number=p.number)
                
                
                
                
                
                self.assertEqual(i % 2, 0)
        
        
        self.ui.write_parameter(value=10, number=1) #u16 u16F u32 u32F 
            
            
            
            
            
            
            pass
            
        
        
        
        
        
        
#    def test_read_parameter(self):
        
        
        
        
        
    
        
if __name__ == '__main__':
    unittest.main()