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
        
        # Initialize the pump to an off state.
        self.store()
        self.off()
                
        # Start a parallel thread for continuously updating the pump 
        # frequency.
        self.thread = threading.Thread(target=self.run, args=[lock])
        self.stop_flag = threading.Event()
        self.thread.daemon = True
        self.thread.start()
        
    def set_errors(self, numbers, frequencies, hours):
        """Set pump error memory.
        
        Args:
            numbers: A list of error numbers.
            frequencies: A list of pump frequencies at the times of 
                errors.
            hours: A list of pump operating hours at the times of 
                errors.
        All lists should have length between 1 and 254, and all three 
        lengths should be equal.
        """
        
        def pad(list_):
            return list_ + (254 - len(list_))*[0]
        
        self.variables.error_list = pad(numbers)
        self.error_frequency_list = pad(frequencies)
        self.error_hour_list = pad(hours)
        
    def set_warnings(self, numbers):
        """Set active pump warnings.
        
        Args:
            numbers: An iterable of ints in range(16) representing the
                numbers of active warnings.
        """
        string = ''.join(['1' if i in numbers else '0' for i in range(16)])                
        self.variables.warnings = str_to_int(string)
        
    def store(self):
        """Save parameter data to nonvolatile memory.
        
        Parameters which are changed but not saved are reset when the 
        pump is turned off. Parameters which are not writable are 
        not affected by this method.
        """
        values = {}
        for i, p in self.parameters.items():
            if p.writable:
                try:
                    values[i] = p.value.copy()
                except AttributeError:
                    values[i] = p.value
                
        self.stored_values = values
        
    def restore(self):
        """Restore parameter values from nonvolatile memory.
        
        Current parameter values are discarded and replaced by values 
        previously saved with the *store* method. Parameters which are 
        not writable are not affected by this method.
        """
        for i, value in self.stored_values.items():
            try:
                self.parameters[i].value = value.copy()
            except AttributeError:
                self.parameters[i].value = value
        
    def on(self):
        """Turn the pump on."""
        self.is_on = True
        self.variables.voltage = 20
        self.variables.current = 10
        self.variables.temperature = 40
        self.variables.motor_power = 30
        self.variables.motor_temperature = 50
        
    def off(self):
        """Turn the pump off, discarding all parameter changes not 
        saved to nonvolatile memory.
        """
        if self.variables.save_data:
            self.store()
            self.variables.save_data = 0
        self.restore()
        
        self.variables.voltage = 0
        self.variables.current = 0
        self.variables.temperature = 0
        self.variables.motor_power = 0
        self.variables.motor_temperature = 0
        
        self.is_on = False
        
    def stop(self):
        """Order the parallel thread to stop."""
        self.stop_flag.set()
        
    def handle_control_bits(self, query):
        """Apply the effects of control bits in *query*.
        
        The following control bits are recognized; all others are 
        ignored:
            COMMAND
            START_STOP
            FREQ_SETPOINT
            RESET_ERROR
        """

        if not ControlBits.COMMAND in query.control_or_status_set:
            return
        
        if ControlBits.START_STOP in query.control_or_status_set:
            if self.is_on:
                self.off()
            else:
                self.on()
        
        if ControlBits.FREQ_SETPOINT in query.control_or_status_set:
            self.variables.frequency_setpoint = query.frequency
            
        if ControlBits.RESET_ERROR in query.control_or_status_set:
            self.set_errors([], [], [])
            
    def handle_status_bits(self, reply):
        """Write appropriate status bits to *reply*.
        
        The following status bits can be written; all others are 
        ignored:
            OPERATION
            READY
            TURNING
            ACCELERATION
            DECELERATION
            ERROR
            WARNING
        """
                                
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
            
        errors_present = any(self.variables.error_list)
        if errors_present:
            reply.control_or_status_set.add(StatusBits.ERROR)
        
        if self.variables.warnings:
            reply.control_or_status_set.add(StatusBits.WARNING)
        
    def handle_hardware(self, query, reply):
        """Write hardware data to *reply.*
        
        Apply the hardware-related commands specified by *query*, 
        change pump attributes accordingly, and write hardware data and
        status bits to *reply*.
        """

        self.handle_control_bits(query)
        self.handle_status_bits(reply)
        
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