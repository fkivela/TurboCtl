import threading
import time

from ..data import StatusBits, ControlBits
from ..telegram import str_to_int    


class HWParameters():
    """A small class to group together and give names to parameters 
    related to pump hardware.
    """
    def __init__(self, parameters):
        """Initializer.
        
        Args:
            parameters: A dict of ExtendedParameters.
        """
        self.frequency_setpoint = parameters[24]
        self.frequency = parameters[3]
        self.voltage = parameters[4]
        self.current = parameters[5]
        self.temperature = parameters[11]
        self.motor_power = parameters[6]
        self.motor_temperature = parameters[7]
        self.save_data = parameters[8]
            
        self.error_counter = parameters[40]
        self.overload_error_counter = parameters[41]
        # Overload error = Error #106
        self.power_failure_error_counter = parameters[43]
        # Power supply error = Error #603
        self.error_list = parameters[171] #254 indices
        self.error_frequency_list = parameters[174]
        self.error_hour_list = parameters[176]
        self.operating_hours = parameters[184]
        self.warnings = parameters[227]

        
class Variables():
    """A small class to allow the simpler syntax 
    "variables.parameter_name = value" instead of 
    "hwparameters.parameter_name.value = value".
    """
    
    def __init__(self, parameters):
        """Initializer.
        
        Args:
            parameters: The same dict of ExtendedParameter objects as 
                used by ParameterComponent.
        """

        self.parameters = HWParameters(parameters)
        
    def __setattr__(self, name, value):
        """Set the attribute *name* to *value*.
        
        The *parameters* attribute is handled as a special case and
        is accessed normally without delegation.
        For all other attributes, the value of parameter *name* is set 
        to *value*.
        """
        if name == 'parameters':
            self.__dict__[name] = value
            return
        
        parameter = getattr(self.parameters, name)
        parameter.value = value
        
    def __getattr__(self, name):
        """Return the the value of the attribute *name*.
        
        The *parameters* attribute is handled as a special case and
        is accessed normally without delegation.
        For all other attributes, the value of parameter *name* is 
        returned.
        """
        if name == 'parameters':
            return self.__dict__[name]
        
        parameter = getattr(self.parameters, name)
        return parameter.value
    
        
class HardwareComponent():
    """This class defines the part of a VirtualPump that handles 
    hardware data and command/status words.
    """
    
    def __init__(self, parameters, lock):
        """Initialize a new HardwareComponent.
        
        Args:
            parameters: The same dict of ExtendedParameter objects as 
                used by ParameterComponent.
            lock: The same threading.Lock object as used by 
                ConnectionComponent.process_query. 
        """
        self.parameters = parameters
        self.variables = Variables(parameters)
        
        # The timestep of iteration in seconds.
        self.step = 0.1
        # The rate of pump acceleration and deceleration in Hz/s.
        self.abs_acceleration = 100
        
        # The pump starts in an off state.
        self.is_on = False 
        self.off()
                
        # Start a parallel thread for continuously updating the pump 
        # frequency.
        self.thread = threading.Thread(target=self.run, args=[lock])
        self.stop_flag = threading.Event()
        self.thread.daemon = True
        self.thread.start()
                        
    def off(self):
        """Turn the pump off."""
        self.is_on = False
        self.variables.temperature = 0
        self.variables.current = 0
        self.variables.voltage = 0

         
    def on(self):
        """Turn the pump on."""
        self.is_on = True
        self.variables.temperature = 30
        self.variables.current = 10
        self.variables.voltage = 24
                
    def stop(self):
        """Order the parallel thread to stop."""
        self.stop_flag.set()
        
    def handle_control_bits(self, query):
        """Apply the effects of control bits in *query*.
        
        Currently only the COMMAND and ON control bits are recognized; 
        all others are ignored.
        """
        
        if {ControlBits.COMMAND, ControlBits.ON}.issubset(
        query.control_or_status_set):
            self.on()
        else:
            self.off()
            
    def handle_status_bits(self, query, reply):
        """Write appropriate status bits to *reply*.
        
        The following status bits are supported:
            OPERATION
            READY
            TURNING
            ACCELERATION
            DECELERATION
            PARAM_CHANNEL
            PROCESS_CHANNEL
        """
            
        reply.control_or_status_set.add(StatusBits.PARAM_CHANNEL)
        
        if ControlBits.COMMAND in query.control_or_status_set:
            reply.control_or_status_set.add(StatusBits.PROCESS_CHANNEL)
          
        if self.is_on:
            reply.control_or_status_set.add(StatusBits.OPERATION)
        else:
            reply.control_or_status_set.add(StatusBits.READY)
            
        if self.variables.frequency:
            reply.control_or_status_set.add(StatusBits.TURNING)
            
        if self.acceleration > 0:
            reply.control_or_status_set.add(StatusBits.ACCELERATION)
            
        if self.acceleration < 0:
            reply.control_or_status_set.add(StatusBits.DECELERATION)
            
    def handle_hardware(self, query, reply):
        """Write hardware data to *reply.*
        
        Apply the hardware-related commands specified by *query*, 
        change pump attributes accordingly, and write hardware data and
        status bits to *reply*.
        """

        self.handle_control_bits(query)
        self.handle_status_bits(query, reply)
        
        reply.frequency = int(self.variables.frequency)
        # The frequency parameter can have non-integer values; 
        # they are automatically rounded to ints when they are 
        # written to a Reply object. 
        reply.temperature = self.variables.temperature
        reply.current = self.variables.current
        reply.voltage = self.variables.voltage

    @property
    def acceleration(self):
        """Return the current acceleration (>0) or deceleration (<0) 
        of the frequency in Hz/s.
        """
        if self.variables.frequency < self.frequency_goal:
            return self.abs_acceleration
        elif self.variables.frequency > self.frequency_goal:
            return -self.abs_acceleration
        else:
            return 0
        
    @property
    def frequency_goal(self):
        """Return the frequency setpoint if the pump is on, or 0 if 
        the pump is off.
        """
        return self.variables.frequency_setpoint if self.is_on else 0
    
    def change_frequency(self):
        """Enact the frequency change during a single time-step."""
        change = self.step * self.acceleration            
        difference = self.frequency_goal - self.variables.frequency
        
        if abs(change) > abs(difference):
            change = difference

        self.variables.frequency += change
                
    def run(self, lock):
        """Run the parallel thread by continuously updating the 
        frequency.
        """
        while not self.stop_flag.is_set():
            time.sleep(self.step)        
            lock.acquire()
            self.change_frequency()
            lock.release()