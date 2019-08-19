"""This module can be used to simulate the I/O behaviour of a TURBOVAC 
pump and thus enable testing the program even without an actual 
physical pump.
"""
import threading

from ..data import PARAMETERS
from ..telegram import Query

from .virtualconnection import VirtualConnection
from .hardware_component import HardwareComponent
from .parameter_component import ExtendedParameters, ParameterComponent

# TODO
# Should a wrong parameter index raise a parameter number error or 
# other error (currently raise parameter number error)?
# Add command word handling.
# Don't access parameters if no parameter access is specified


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
            query = Query(input_)
        except ValueError:
            return bytes()
        
        reply = self.process_query(query)
        return reply.data
    
class VirtualPump():
    """This class simulates a TURBOVAC pump and tries to respond to 
    signals the same way a physical pump would. This makes it possible
    to test the turboctl package without connecting to a physical pump.
    """
    
    def __init__(self, parameters=PARAMETERS):
        """
        Initialize a new VirtualPump.
        
        Args:
            parameters=PARAMETERS: The parameter dictionary used.
                This may be set to a non-default value for easier 
                testing.
        """
        self.lock = threading.Lock()
        
        ext_parameters = ExtendedParameters(parameters)
        
        self.connection_component = ConnectionComponent(self.process)
        self.parameter_component = ParameterComponent(ext_parameters)
        self.hardware_component = HardwareComponent(ext_parameters, self.lock)
        
        self.port = self.connection_component.port
        
    def __getattr__(self):
        pass
    # observables: 0 vs constant vs random vs variable
    # observable mean and variance
    # command and status words (none/constant/realistic)
    # errors
    # warnings
        
        
    @property
    def random_observables(self):
        return self.hardware_component.random_observables
    
    @random_observables.setter
    def random_observables(self, value):
        self.hardware_component.random_observables = value
                
    def __enter__(self):
        return self
    
    def __exit__(self, type_, value, traceback):
        self.close()
                    
    def close(self):
        self.connection_component.close()
        self.hardware_component.stop()
        
    def process(self, query):
        """Process an input telegram.
        
        This function takes an input telegram, performs any commands 
        specified by its (such as changing parameter values),
        and then returns an output telegram based on the input telegram 
        and the state of the pump.
        
        Args:
            query: A Telegram object.
            
        Returns:
            A Telegram object.
        """
        self.lock.acquire()        
        reply = self.parameter_component.handle_parameter(query)
        self.hardware_component.handle_hardware(query, reply)
        self.lock.release()
        return reply