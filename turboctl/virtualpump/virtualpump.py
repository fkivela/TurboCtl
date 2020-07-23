"""This module can be used to simulate the I/O behaviour of a TURBOVAC 
pump and thus enable testing the program without access to an actual pump.
"""
import threading

from turboctl.telegram.parser import PARAMETERS
from turboctl.telegram.telegram import TelegramBuilder, TelegramReader
from turboctl.virtualpump.virtualconnection import VirtualConnection
from turboctl.virtualpump.hardware_component import HardwareComponent
from turboctl.virtualpump.parameter_component import (ExtendedParameters,
                                                      ParameterComponent)

class VirtualPump():
    """
    VirtualPump(parameters=PARAMETERS)
    
    This class simulates a TURBOVAC pump and tries to respond to 
    signals the same way a physical pump would. This makes it possible
    to test the ``turboctl`` package without connecting to a physical pump.
    
    Attributes:
        
        parameters: The parameter set to be used (a :class:`dict` of
            :class:`~turboctl.telegram.parser.Parameter` objects, with
            parameter numbers as keys). The default value is
            :const:`~turboctl.telegram.parser.PARAMETERS`,
            but non-default values can be used for testing the class.
            This shouldn't be changed after initialization, unless the
            parameter dictionaries of :attr:`parameter_component` and
            :attr:`hardware_component` are also updated.
        
        connection(:class:`~turboctl.virtualpump.virtualconnection\
.VirtualConnection`):
            Simulates the serial connection.    
        
        parameter_component (:class:`~turboctl.virtualpump\
.parameter_component.ParameterComponent`):
            Handles access to pump parameters.
        
        hardware_component (:class:`~turboctl.virtualpump\
.hardware_component.HardwareComponent`):
            Simulates pump hardware.
    """
    # The first line of the docstring overrides the default signature generated
    # by Sphinx, and thus prevents PARAMETERS from being expanded.    
    
    def __init__(self, parameters=PARAMETERS):
        """
        __init__(parameters=PARAMETERS)
        
        Initialize a new :class:`VirtualPump`.
        
        Args:
            parameters: The object to be assigned to :attr:`parameters`.
        """
        self.parameters = parameters
        ext_parameters = ExtendedParameters(parameters)
        
        # The lock prevents two parallel threads from accessing the 
        # same data at the same time.
        self.lock = threading.Lock()
        
        self.connection = VirtualConnection(self.process)
        self.parameter_component = ParameterComponent(ext_parameters)
        self.hardware_component = HardwareComponent(ext_parameters, self.lock)
                        
    def __enter__(self):
        """Called at the beginning of a ``with`` block; returns
        *self*.
        """
        return self
    
    def __exit__(self, type_, value, traceback):
        """Called upon exiting a ``with`` block; calls
        :meth:`stop`.
        """
        self.stop()
                    
    def stop(self):
        """Close parallel threads by calling
        :attr:`connection`:meth:`.close()
        <turboctl.virtualpump.virtualconnection.VirtualConnection.close>`
        and
        :attr:`hardware_component`:meth:`.stop()
        <turboctl.virtualpump.hardware_component.HardwareComponent.stop>`.
        """
        self.connection.close()
        self.hardware_component.stop()
        
    def process(self, bytes_in):
        """Process incoming data.
        
        This function processes the data sent to the virtual pump by
        interpreting it as a telegram and performing any commands 
        specified by it (such as changing parameter values).
        
        A reply telegram is then formed and its contents returned.
        
        Args:
            bytes_in: The telegram sent to the pump as a :class:`bytes` object.
            
        Returns:
            The telegram sent back from the pump as a :class:`bytes` object.
        """
        builder = TelegramBuilder(self.parameters).from_bytes(bytes_in)
        query = TelegramReader(builder.build('query'), 'query')
        
        self.lock.acquire()
        # VirtualConnection runs this function in a parallel thread,
        # so attribute access from other threads is locked while this part is
        # executed in order to prevent race conditions.
        self.parameter_component.handle_parameter(query, builder)
        self.hardware_component.handle_hardware(query, builder)
        self.lock.release()
        
        return bytes(builder.build('reply'))
