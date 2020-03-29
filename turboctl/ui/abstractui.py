"""This module contains generic functionality for creating a user 
interface for controlling a TURBOVAC vacuum pump.
"""
import serial

from .. data import ControlBits
from ..telegram import Query, Reply


class AbstractUI():
    """A class for connecting and sending telegrams to a TURBOVAC pump.
    
    This class can be used as an API for communicating with the pump, 
    and subclassed to create user interfaces.
    
    All methods in this class that access the pump will raise a 
    serial.SerialException if a connection to the pump can't be formed
    or if it is interrupted.
    """
    
    # Parameters for the RS 232/485 serial connection on the 
    # Leybold TURBOVAC i/iX.
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
        """Initialize a new AbstractUI and connect to the pump.
        
        Args:
            port: The device name for port that should be used for 
                the connection. Other parameters of the connection 
                are class attributes of this class.
        
        Raises:
            serial.SerialException: If *port* is not None and it can't 
                be connected to. If *port* is None, an exception will 
                be raised when a telegram should be sent to the pump.
        """
        self.pump_on = False
        self.port = port
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
                    
    def _send(self, query):
        """Send a query to the pump.
        
        If *self.pump_on* is True, a command to turn or keep the pump 
        on is added to *query*.
        
        Args:
            query: A Query object.
            
        Returns: A Query object detailing the message that was sent to 
            the pump and a  Reply object detailing the response from 
            the pump.
        """
        if self.pump_on:
            query.control_or_status_set.update({ControlBits.COMMAND, 
                                                ControlBits.ON})
        self.connection.write(query.data)
        return query, self._receive()
        
    def _receive(self):
        """Receive a reply from the pump.
        
        Returns: An instance of the Reply class.
            
        Raises:
            ValueError: If the pump sends an invalid response or no 
                response at all.
        """
        answer_bytes = self.connection.read(Reply.LENGTH)
        if not answer_bytes:
            raise ValueError('No reply received from the pump')
        return Reply(answer_bytes)
        
    def status(self):
        """Request pump status by sending an empty telegram.
        
        Returns: The Query object that was sent to the pump and the 
            Reply object that was received.
        """
        query = Query()
        return self._send(query)
                
    def read_parameter(self, number, index=0):
        """Read the value of a parameter from the pump.
        
        Args:
            number: Parameter number (an int).
            index=0: Parameter index (an int >= 0). This should be left 
                to 0 for unindexed parameters.
                
        Returns: The Query object that was sent to the pump and the 
            Reply object that was received.
        """
        query = Query(parameter_number=number)
        query.parameter_index = index
        query.parameter_mode = 'read'
        return self._send(query)
    
    def write_parameter(self, value, number, index=0):
        """Write a value to a pump parameter.
        
        Args:
            value: The value to be written. Its type (int or float) 
                should match the type of the parameter.
            number: Parameter number (an int).
            index=0: Parameter index (an int >= 0). This should be left 
                to 0 for unindexed parameters.
                
        Returns: The Query object that was sent to the pump and the 
            Reply object that was received.
        """
        query = Query(parameter_number=number)
        query.parameter_index = index
        query.parameter_value = value
        query.parameter_mode = 'write'        
        return self._send(query)
    
    def save_data(self):
        """Save pump parameters to nonvolatile memory.
                
        Returns: The Query object that was sent to the pump and the 
            Reply object that was received.
        """
        self.write_parameter(number=8, value=1)
        
    def set_frequency(self, frequency):
        """Set pump frequency setpoint to *frequency*.
                
        Args:
            frequency: The desired value in Hz.
        
        Returns: The Query object that was sent to the pump and the 
            Reply object that was received.
        """
        query = Query()
        query.control_or_status_set = {ControlBits.COMMAND, 
                                       ControlBits.SETPOINT}
        query.frequency = frequency        
        return self._send(query)
    
    def test(self, *args, **kwargs):
        """This method is intended for testing the pump and 
        debugging.
        
        Commands that can't be sent using the other functions can be 
        easily defined here.
        """
        q = Query()
        return self._send(q)        