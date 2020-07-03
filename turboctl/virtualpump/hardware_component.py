"""This module handles the simulation of pump hardware in a
:class:~`turboctl.virtualpump.virtualpump.VirtualPump`.

TODO: Parameter values should be Data objects.

..
    Aliases for Sphinx.

.. |Uint| replace:: :class:`~turboctl.telegram.datatypes.Uint`
.. |Sint| replace:: :class:`~turboctl.telegram.datatypes.Sint`
.. |Float| replace:: :class:`~turboctl.telegram.datatypes.Float`
.. |Bin| replace:: :class:`~turboctl.telegram.datatypes.Bin`
"""
import threading
import time

from turboctl.telegram.codes import StatusBits, ControlBits


class HardwareComponent():
    """This class defines the part of a
    :class:`~turboctl.virtualpump.virtualpump.VirtualPump`
    that handles hardware data and command/status words.
    
    This class simulates the following pump properties:
        
        - The pump can be turned on and off.
        
        - Temperature, current and voltage are 0 when the pump is off, and
          have constant positive values when the pump is on. This is reflected 
          both in the reply telegrams and the values of corresponding
          parameters.
          
        - When the pump is on, the pump frequency moves towards the setpoint at
          a constant rate. When the pump is off, the frequency moves towards 0
          at the same rate.
          
        - The frequency setpoint is always read from the corresponding
          parameter, and cannot currently be set with the frequency field of
          a telegram.
          
        - Currently this class only recognizes the 'COMMAND' and 'ON'
          control bits (see :class:`~turboctl.telegram.codes.ControlBits`);
          all others are ignored.
          
        - The following status bits
          (see :class:`~turboctl.telegram.codes.ControlBits`)
          are applied to the reply telegram:
            
            ``'OPERATION'``: When the pump is on.
            ``'READY'``: When the pump is off.
            ``'TURNING'``: When the pump frequency is not 0.
            ``'ACCELERATION'``: When the pump acceleration is above 0.
            ``'DECELERATION'``: When the pump acceleration is below 0.
            ``'PARAM_CHANNEL'``: Always.
            ``'PROCESS_CHANNEL'``: When the COMMAND control bit is supplied.

    Attributes:
        parameters:
            The same dict of
            :class:`~turboctl.virtualpump.parameter_component
            .ExtendedParameter` objects as used by
            :class:`turboctl.virtualpump.parameter_component
            .ParameterComponent`. This is needed, since some hardware
            components affect the values of parameters.
            
        variables:
            A :class:`Variables` instance that contains the parameters that
            can be modified by this object.
            
        thread:
            A parallel thread (a :class:`threading.Thread` object) which runs
            the hardware simulation.
            
        step:
            The timestep of iteration; the parallel thread waits this amount
            in seconds between iterations.
            
        abs_acceleration:
            How fast the pump accelerates or decelerates, in Hz / second.
            
        is_on:
            A :class:`boolean` flag to keep track of whether the pump is on
            or off.
            
        stop_flag:
            A :class:`threading.Event` that can be used to stop the parallel
            thread.
    """
    
    def __init__(self, parameters, lock):
        """Initialize a new :class:`HardwareComponent`.
        
        Args:
            parameters:
                The value for :attr:`parameters`.
                
            lock: The same :class:`threading.Lock` object as used by 
                :meth:`turboctl.virtualconnection.connection_component
                .ConnectionComponent.process_query`. 
        """
        self.parameters = parameters
        self.variables = Variables(parameters)
        
        self.step = 0.1
        self.abs_acceleration = 100
        
        # The pump starts in an off state.
        self.is_on = False 
        # This sets some parameters to the off state.
        self.off()
                
        # Start a parallel thread for continuously updating the pump 
        # frequency.
        self.thread = threading.Thread(target=self._run, args=[lock])
        self.stop_flag = threading.Event()
        self.thread.daemon = True
        self.thread.start()
                                
    def handle_hardware(self, query, reply):
        """Write hardware data to *reply.*
        
        Apply the hardware-related commands specified by *query*, 
        change pump attributes accordingly, and write hardware data and
        status bits to *reply*.
        
        Args:
            query (class:`~turboctl.telegram.telegram.TelegramReader`):
                The telegram sent to the pump.
                
            reply(:class:`~turboctl.telegram.telegram.TelegramBuilder`):
                This will be used to build the telegram sent from the pump.                
        """
        self._handle_control_bits(query)
        self._handle_status_bits(query, reply)
        
        reply.frequency = round(self.variables.frequency)
        # The frequency parameter can have non-integer values; 
        # they are automatically rounded to ints when they are 
        # written to a Reply object.
        reply.temperature = self.variables.temperature
        reply.current = self.variables.current
        reply.voltage = self.variables.voltage
        
    def _handle_control_bits(self, query):
        """Apply the effects of control bits in *query*.
        
        Currently only the COMMAND and ON control bits are
        recognized; all others are ignored.
        """
        on_command = (ControlBits.COMMAND in query.flag_bits and
                      ControlBits.ON in query.flag_bits)
        if on_command:
            self.on()
        else:
            self.off()
            
    def _handle_status_bits(self, query, reply):
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
        # TODO: find out if this is correct by testing the real pump.
        
        bitlist = [StatusBits.PARAM_CHANNEL]
        
        if ControlBits.COMMAND in query.flag_bits:
            bitlist.append(StatusBits.PROCESS_CHANNEL)
          
        if self.is_on:
            bitlist.append(StatusBits.OPERATION)
        else:
            bitlist.append(StatusBits.READY)
            
        if self.variables.frequency:
            bitlist.append(StatusBits.TURNING)
            
        if self.acceleration > 0:
            bitlist.append(StatusBits.ACCELERATION)
            
        if self.acceleration < 0:
            bitlist.append(StatusBits.DECELERATION)
            
        reply.set_flag_bits(bitlist)
            
    def stop(self):
        """Order the parallel thread to stop."""
        self.stop_flag.set()        
        
    def on(self):
        """Turn the pump on and update parameters accordingly."""
        self.is_on = True
        self.variables.temperature = 30
        self.variables.current = 10
        self.variables.voltage = 24
        
    def off(self):
        """Turn the pump off and update parameters accordingly."""
        self.is_on = False
        self.variables.temperature = 0
        self.variables.current = 0
        self.variables.voltage = 0
     
    @property
    def _acceleration(self):
        """Return the current acceleration of the frequency in Hz/s.
        
        Deceleration is represented by a negative acceleration.
        """
        if self.variables.frequency < self.frequency_goal:
            return self.abs_acceleration
        elif self.variables.frequency > self.frequency_goal:
            return -self.abs_acceleration
        else:
            return 0
        
    @property
    def _frequency_goal(self):
        """Return the frequency setpoint if the pump is on, or 0 if 
        the pump is off.
        """
        return self.variables.frequency_setpoint if self.is_on else 0
    
    def _change_frequency(self):
        """Enact the frequency change during a single time-step."""
        change = self.step * self.acceleration            
        difference = self.frequency_goal - self.variables.frequency
        
        if abs(change) > abs(difference):
            change = difference

        self.variables.frequency += change
                
    def _run(self, lock):
        """Run the parallel thread by continuously updating the 
        frequency.
        """
        while not self.stop_flag.is_set():
            time.sleep(self.step)        
            lock.acquire()
            self.change_frequency()
            lock.release()


class HWParameters():
    """A small class to group together and give names to parameters 
    related to pump hardware.
    
    Each of the attributes of this class is an :class:`ExtendedParameter`
    object that corresponds to the hardware variable described by the
    attribute name.
    
    Note that most of the parameters corresponding to the attributes of this
    class aren't currently modified by :class:`HardwareComponent`. 
    
    Attributes:
        
        frequency:
            Parameter 3. Current rotor frequency in Hz.
            This value is included in every reply telegram.
            
            Type: 16-bit |Uint|.
            
        voltage:
            Parameter 4. Current intermediate circuit voltage in 0.1 V.
            This value is included in every reply telegram.
            
            Type: 16-bit |Uint|.
            
        current:
            Parameter 5. Current motor current in 0.1 A.
            This value is included in every reply telegram.
            
            Type: 16-bit |Uint|.
            
        motor_power:
            Parameter 6. Current motor input power in 0.1 W.
            
            Type: 16-bit |Uint|.
            
        motor_temperature:
            Parameter 7. Current motor temperature in 0.1 °C.
            
            Type: 16-bit |Sint|.
            
        save_data:
            Parameter 8. Writing any value to this parameter saves all
            changed parameter values into nonvolatile memory. Otherwise all
            changes are lost when power to the pump is cut off.
            
            Type: 16-bit |Sint|.
            
        temperature:
            Parameter 11. Current frequency convertertemperature in °C.
            This value is included in every reply telegram.
            
            Type: 16-bit |Sint|.
            
        frequency_setpoint:
            Parameter 24. Setpoint for the rotor frequency in Hz.
            The pump tries to keep the frequency at this number.
            
            Type: 16-bit |Uint|.
                
        error_counter:
            Parameter 40. Counts the total number of error conditions that
            have occurred to the pump.
            
            Type: 16-bit |Uint|.
            
        overload_error_counter:
            Parameter 41. Counts the number of error conditions caused by an
            overload. An overload error is represented by the error code 106.
            
            Type: 16-bit |Uint|.
            
        power_failure_error_counter: 
            Parameter 43. Counts the number of error conditions caused by a
            disturbance in power supply. A power supply error is reprsented
            by the error code 603.
            
            Type: 16-bit |Uint|.
            
        error_list:
            Parameter 171. This parameter has 254 indices, each of which
            stores an error code. The most recent error is located at index 0
            and the oldest at index 253.
            
            Type: 16-bit |Uint|, 254 indices.
            
        error_frequency_list:
            Parameter 174. The indices of this parameter contain the frequency
            of the pump at the time of the corresponding error in
            :attr:`error_list`.
            
            Type: 16-bit |Uint|, 254 indices.
            
        error_hour_list:
            Parameter 176. This parameter works analogously to
            :attr`error_frequency_list`:, but contains the number of
            operational hours of the pump instead of the frequency. 
            
            Type: 32-bit |Sint|, 254 indices.
            
        operating_hours: 
            Parameter 184. Counts the total number of operational hours for
            the pump.
            
            Type: 32-bit |Sint|, 254 indices.
            
        warning_list:
            Parameter 227. Works analogously to :attr:`error_list`, but lists
            warnings instead of errors.
            
            Type: 16-bit |Uint|, 254 indices.
    """
    # Parameter 6 is listed as "drive power" in the manual, but this is
    # probably more or less the same as the motor.
    
    def __init__(self, parameters):
        """Initializer.
        
        Args:
            parameters: A :class:`dict` of :class:`ExtendedParameters` objects,
                which needs to include at least all the parameters which are
                attributes for this class.
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
        self.power_failure_error_counter = parameters[43]
        self.error_list = parameters[171]
        self.error_frequency_list = parameters[174]
        self.error_hour_list = parameters[176]
        self.operating_hours = parameters[184]
        self.warnings = parameters[227]

        
class Variables():
    """This class encapsulates :class:`HWParameters` in order to allow the
    simpler syntax
    ::
        
        variables.parameter_name = value
        
    instead of
    ::
        
        
        hwparameters.parameter_name.value = value
        
    Attributes:
        parameters: The encapsulated :class:`HWParameters` object.
    """
    
    def __init__(self, parameters):
        """Initialize a new :class:`Variables` instance.
        
        Args:
            parameters: Passed on to :meth:`HWParameters.__init__`.
        """
        self.parameters = HWParameters(parameters)
        
    def __setattr__(self, name, value):
        """Set the attribute *name* to *value*.
        
        The *parameters* attribute is handled as a special case and
        is accessed normally without delegation.
        For all other attributes, the value of the parameter in
        :attr:`parameters` with the name *name* is set to *value*.
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
        For all other attributes, the value of the parameter in
        :attr:`parameters` with the name *name* * is returned.
        """
        if name == 'parameters':
            return self.__dict__[name]
        
        parameter = getattr(self.parameters, name)
        return parameter.value
