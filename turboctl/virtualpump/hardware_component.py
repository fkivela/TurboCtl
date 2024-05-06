"""This module handles the simulation of pump hardware in a
:class:`~turboctl.virtualpump.virtualpump.VirtualPump`.

..
    Aliases for Sphinx.

.. |Uint| replace:: :class:`~turboctl.telegram.datatypes.Uint`
.. |Sint| replace:: :class:`~turboctl.telegram.datatypes.Sint`
.. |Float| replace:: :class:`~turboctl.telegram.datatypes.Float`
.. |Bin| replace:: :class:`~turboctl.telegram.datatypes.Bin`
.. |ExtendedParameter| replace::
    :class:`~turboctl.virtualpump.parameter_component.ExtendedParameter`
.. |ParameterComponent| replace::
    :class:`~turboctl.virtualpump.parameter_component.ParameterComponent`
.. |ParameterComponent.handle_parameter| replace::
    :meth:`ParameterComponent.handle_parameter()
    <turboctl.virtualpump.parameter_component.ParameterComponent\
.handle_parameter>`
"""

import threading
import time

from turboctl.telegram.codes import StatusBits, ControlBits


class HardwareComponent():
    """This class defines the part of a
    :class:`~turboctl.virtualpump.virtualpump.VirtualPump`
    that handles hardware data and command/status bits.
    
    The following pump properties are simulated:
        
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
          
        - Currently this class only recognizes the ``COMMAND`` and ``ON``
          control bits (see :class:`~turboctl.telegram.codes.ControlBits`);
          all others are ignored.
          
        - The following status bits
          (see :class:`~turboctl.telegram.codes.StatusBits`)
          are applied to the reply telegram:
            
              - ``OPERATION'``: When the pump is on.
              - ``READY``: When the pump is off.
              - ``TURNING``: When the pump frequency is not 0.
              - ``ACCELERATION``: When the pump acceleration is above 0.
              - ``DECELERATION``: When the pump acceleration is below 0.
              - ``PARAM_CHANNEL``: Always.
              - ``PROCESS_CHANNEL``: When the ``COMMAND`` control bit is
                supplied.

    Attributes:
        variables:
            A :class:`Variables` instance that contains the parameters that
            can be modified by this object.
            
        step:
            The timestep of iteration; the parallel thread that updates
            :attr:`frequency` waits this amount of seconds between iterations.
            
        abs_acceleration:
            How fast the pump accelerates or decelerates, in Hz / second.
            
        frequency:
            The exact frequency of the pump as a :class:`float`.
            This is needed to correctly simulate gradual changes in the
            frequency, because the frequency parameter only saves integer
            values.
            
        is_on:
            A :class:`bool` flag to keep track of whether the pump is on
            or off.
    """
    
    TEMPERATURE = 30
    """The pump reports this constant temperature when it's on.
    The unit is °C."""
    
    CURRENT = 10
    """The pump reports this constant temperature when it's on.
    The unit is 0.1 A.
    """
    
    VOLTAGE = 24
    """The pump reports this constant temperature when it's on.
    The unit is 0.1 V.
    """
    
    def __init__(self, parameters, lock):
        """Initialize a new :class:`HardwareComponent`.
        
        Args:
            parameters: The same :class:`dict` of |ExtendedParameter|
                objects as used by |ParameterComponent|.
                This is needed because some hardware components affect the
                values of parameters and vice versa.
                Note that these need to be the actual parameters of the pump;
                dummy values cannot be used even for testing purposes, since
                all hardware-related parameters (see :class:`HWParameters` for
                a list of those) need to be present for this class to function.
                
            lock: A :class:`threading.Lock` object that can be used to
                temporarily freeze the parallel thread which updates
                :attr:`frequency`.
                The purpose of this is to prevent race conditions between that
                thread and the :meth:`handle_hardware` and
                |ParameterComponent.handle_parameter| methods, since they all
                can access and modify the value of the frequency parameter.
        """
        self.parameters = parameters
        self.variables = Variables(parameters)
        
        self.step = 0.1
        self.abs_acceleration = 100
        self.frequency = 0.0
        
        # The pump starts in an off state.
        self.is_on = False 
        # This sets some parameters to the off state.
        self.off()
                
        # Start a parallel thread for continuously updating the pump 
        # frequency.
        thread = threading.Thread(target=self._run, args=[lock])
        self._stop_flag = threading.Event()
        thread.daemon = True
        thread.start()
                                
    def handle_hardware(self, query, reply):
        """Write hardware data to *reply.*
        
        Apply the hardware-related commands specified by *query*, 
        change pump attributes accordingly, and write hardware data and
        status bits to *reply*.
        
        Args:
            query (:class:`~turboctl.telegram.telegram.TelegramReader`):
                The telegram sent to the pump.
                
            reply(:class:`~turboctl.telegram.telegram.TelegramBuilder`):
                This will be used to build the telegram sent from the pump.                
        """
        self._handle_control_bits(query)
        self._handle_status_bits(query, reply)
        
        (reply.set_frequency(self.variables.frequency)
              .set_temperature(self.variables.temperature)
              .set_current(self.variables.current)
              .set_voltage(self.variables.voltage))
        
    def _handle_control_bits(self, query):
        """Apply the effects of control bits in *query*.

        Currently only the COMMAND and ON control bits are
        recognized; all others are ignored.
        """
        on_command = (ControlBits.COMMAND in query.flag_bits and
                      ControlBits.ON in query.flag_bits)

        off_command = (ControlBits.COMMAND in query.flag_bits and
                       ControlBits.ON not in query.flag_bits)

        if on_command:
            self.on()

        if off_command:
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
            
        if self._acceleration > 0:
            bitlist.append(StatusBits.ACCELERATION)
            
        if self._acceleration < 0:
            bitlist.append(StatusBits.DECELERATION)
            
        reply.set_flag_bits(bitlist)
            
    def stop(self):
        """Order the parallel thread to stop."""
        self._stop_flag.set()        
        
    def on(self):
        """Turn the pump on and update parameters accordingly."""
        self.is_on = True
        self.variables.temperature = self.TEMPERATURE
        self.variables.current = self.CURRENT
        self.variables.voltage = self.VOLTAGE
        
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
        if self.frequency < self._frequency_goal:
            return self.abs_acceleration
        elif self.frequency > self._frequency_goal:
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
        change = self.step * self._acceleration
        difference = self._frequency_goal - self.frequency
        
        # Make sure the change never takes the frequency to the other side of
        # the frequency goal.
        if abs(change) > abs(difference):
            change = difference
            
        self.frequency += change
        self.variables.frequency = int(self.frequency)
                
    def _run(self, lock):
        """Run the parallel thread by continuously updating the 
        frequency.
        """
        while not self._stop_flag.is_set():
            time.sleep(self.step)
            lock.acquire()
            self._change_frequency()
            lock.release()


class HWParameters():
    """A collection of parameters related to pump hardware.
    
    Each of the attributes of this class is an |ExtendedParameter|
    object. This class gives these parameters descriptive names and makes it
    possible to access them without having to find out the parameter numbers.
    
    Note that :class:`HardwareComponent` currently cannot modify most of these
    parameters, but they are included in case :class:`HardwareComponent` is
    expanded in the future.
    
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
            Parameter 11. Current frequency converter temperature in °C.
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
            :attr:`error_frequency_list`, but contains the number of
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
            parameters: A :class:`dict` of |ExtendedParameter| objects,
                which needs to include at least all the parameters which are
                attributes of this class.
        """
        self.frequency = parameters[3]
        self.voltage = parameters[4]
        self.current = parameters[5]
        self.motor_power = parameters[6]
        self.motor_temperature = parameters[7]
        self.save_data = parameters[8]
        self.temperature = parameters[11]
        self.frequency_setpoint = parameters[24]
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
        
        parameter = hwparameters.parameter_name
        parameter.value[0] = parameter.datatype(value, parameter.bits)
        
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
        
        The :attr:`parameters` attribute is handled as a special case and
        is accessed normally.
        For all other attributes, the value of the parameter in
        :attr:`parameters` with the name *name* is set to *value*.
        
        *value* should be given as an instance of a built-in Python type, and
        will automatically be converted to a
        :class:`~turboctl.telegram.datatypes.Data` subclass instance.
        However, note that the type of *value* should match the type of the
        parameter; e.g. a :class:`float` can be converted into a |FLoat| but
        not into an |Uint|.
        """
        if name == 'parameters':
            self.__dict__[name] = value
            return
        
        parameter = getattr(self.parameters, name)
        # Even the values of unindexed parameters are lists.
        parameter.value[0] = parameter.datatype(value, parameter.bits)
        
    def __getattr__(self, name):
        """Return the the value of the attribute *name*.
        
        This method returns the value of the parameter in :attr:`parameters`
        with the name *name*.
        The value is automatically converted to a built-in type.
        
        Since ``__getattr__`` (unlike ``__getattribute__``) is only called if
        the attribute cannot be found through normal routes, there is no need
        to make :attr:`parameters` into a special case.
        """        
        parameter = getattr(self.parameters, name)
        return parameter.value[0].value
