"""This module can be used to simulate the I/O behaviour of a TURBOVAC 
pump and thus enable testing the program without access to an actual 
physical pump.
"""
import threading

from ..telegram import PARAMETERS, Query

from .virtualconnection import VirtualConnection
from .hardware_component import HardwareComponent
from .parameter_component import ExtendedParameters, ParameterComponent


class VirtualPump():
    """This class simulates a TURBOVAC pump and tries to respond to 
    signals the same way a physical pump would. This makes it possible
    to test the turboctl package without connecting to a physical pump.
    """
    
    def __init__(self, parameters=PARAMETERS):
        """
        Initialize a new VirtualPump.
        
        Args:
            parameters=PARAMETERS: The parameter dictionary to be used.
                This may be set to a non-default value for easier 
                testing.
        """
        # The lock prevents two parallel threads from accessing the 
        # same data at the same time.
        self.lock = threading.Lock()
        
        ext_parameters = ExtendedParameters(parameters)
        
        self.connection_component = ConnectionComponent(self.process)
        self.parameter_component = ParameterComponent(ext_parameters)
        self.hardware_component = HardwareComponent(ext_parameters, self.lock)
        
        self.port = self.connection_component.port
                
    def __enter__(self):
        return self
    
    def __exit__(self, type_, value, traceback):
        self.close()
                    
    def close(self):
        self.connection_component.close()
        self.hardware_component.stop()
        
    def process(self, query):
        """Process a query.
        
        This function takes a Query object, performs any commands 
        specified by it (such as changing parameter values),
        and then returns a Reply object based on the query and the 
        state of the pump.
        
        Args:
            query: A Query object.
            
        Returns:
            A Reply object.
        """
        # ConnectionComponent runs this function in a parallel thread,
        # so attribute access from other threads is locked for the 
        # duration of its execution.
        self.lock.acquire()        
        reply = self.parameter_component.handle_parameter(query)
        self.hardware_component.handle_hardware(query, reply)
        self.lock.release()
        return reply


class ConnectionComponent(VirtualConnection):
    """This class defines the part of a VirtualPump that handles the 
    virtual serial connection between the user and the pump.
    """
    
    def __init__(self, process_query):
        """Initialize a new ConnectionComponent.
        
        Args:
            process_query: The function that should be used
                to form a reply based on a query.
                The usage of the function must be
                >> reply = process_query(query)
        """
        super().__init__(24)
        self.process_query = process_query
    
    def process(self, input_):
        """Return output bytes based on input bytes.
        
        This function only converts between bytes-like objects and 
        queries/replies; the actual processing is done in 
        self.process_query().
        
        Args:
            input_: A bytes-like object.
            
        Returns:
            The data (a bytes-like object) of a reply, 
            or an empty bytes object, if a telegram cannot be 
            formed from *input_*.
        """
        
        try:
            query = Query.from_bytes(input_)
        except ValueError:
            return bytes()
        
        reply = self.process_query(query)
        return reply.to_bytes()