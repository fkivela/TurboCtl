"""This module contains generic functionality for creating a user 
interface for controlling a TURBOVAC vacuum pump.

TODO:
    -Add a connect/disconnect function
"""
import serial

from .. data import StatusBits, ControlBits
from ..telegram import Query, Reply

class AbstractUI():
    
    # Parameters for the RS 232/485 serial connection on the 
    # Leybold TURBOVAC i/iX
    # TODO: Load parameters from a config file?
    BAUDRATE  = 19200
    PARITY    = serial.PARITY_EVEN
    STOPBITS  = serial.STOPBITS_ONE 
    BYTESIZE  = serial.EIGHTBITS
    TIMEOUT   = 1 
    RTSCTS    = False
    DSRDTR    = False 
    XONXOFF   = False
    EXCLUSIVE = True
     
    def __init__(self, port):
        self.port = port
        try:
            self.connection = serial.Serial(port      = self.port, 
                                            baudrate  = self.BAUDRATE,
                                            parity    = self.PARITY,
                                            stopbits  = self.STOPBITS,
                                            bytesize  = self.BYTESIZE,
                                            timeout   = self.TIMEOUT,
                                            rtscts    = self.RTSCTS,
                                            dsrdtr    = self.DSRDTR,
                                            xonxoff   = self.XONXOFF,
                                            exclusive = self.EXCLUSIVE)            
        except serial.SerialException:
            self.connection = None
                    
    def _send(self, query):
                
        if not self.connection:
            raise RuntimeError('There is no connection')
                        
        self.connection.write(query.data)        
        return query, self._receive()
        
    def _receive(self):
        # May raise a serial timeout exception
        # TODO: Add handling?
        answer_bytes = self.connection.read(Reply.LENGTH)

        if not answer_bytes:
            raise ValueError('No reply received')
            
        return Reply(answer_bytes)
        
    def on_off(self):
        query = Query()
        query.control_set = set([ControlBits.COMMAND, ControlBits.START_STOP])   
        
        return self._send(query)
        
    def status(self):
        query = Query()
        return self._send(query)
            
    def read_parameter(self, number, index=0):
        query = Query(parameter_number=number)
        query.index = index
        query.parameter_mode = 'read'
        
        return self._send(query)
    
    def write_parameter(self, value, number, index=0):
        query = Query(parameter_number=number)
        query.index = index
        query.parameter_value = value
        query.parameter_mode = 'write'
        
        return self._send(query)
    
    def save_data(self):
        self.write_parameter(number=8, value=1)
        
    def set_frequency(self, frequency):
        query = Query()
        query.control_set = set(ControlBits.FREQ_SETPOINT)   
        query.frequency = frequency
        
        return self._send(query)
        
    
        
        