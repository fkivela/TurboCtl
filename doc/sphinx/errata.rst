Errata to the user manual
=========================

The user manual of the pump seems to contain numerous errors and inaccuracies
regarding the behaviour of the pump. It also leaves some details about how the
pump works a bit unclear. This page contains some correction and clarifications
on how the pump works according to the tests that were conducted on it while
testing TurboCtl.


Errata
------

This section contains a list of errors that were found in the manual.

- The pump seems to automatically turn off if it doesn't receive any telegrams
  for about 10 seconds. I haven't found any mention of this behaviour in the
  manual.

- :class:`Status bit 8 <turboctl.telegram.codes.StatusBits>` is listed as
  "no function" in the manual, but is occasionally reported by the pump.

- According to the manual, telegrams contain the voltage of the pump in units
  of 0.1 V. However, V seems to be the correct unit, as that results in the
  pump reporting a value of 24 V, which matches the power supply of the pump.

- The frequency setpoint is controlled by parameter 24, which has a default
  value of 1000. Its minimum value is defined by parameter 19, and the maximum
  value by parameter 18. The manual and the tests conducted on the pump agree
  on these facts. However, according to the manual, parameters 19 and 18 have
  default values of 2000 and 1000 respectively, which leaves no valid values
  for the frequency, since the minimum value is larger than the maximum.
  The actual values of these parameters seem to be 750 and 1200, and unlike the
  manual suggests, cannot be changed.

- Parameter 1 isn't actually writable, even though according to the manual it
  should be. There are probably several parameters with the wrong writability
  listed in the manual, but most parameter's haven't been tested.
    
- The manual doesn't specify the writability of parameters 686 and 690.
  Both appear to be writable.

- In the manual, several parameters which have the "real" type (i.e. are
  floating-point numbers) have a default value of 0 and a minumum value of
  1.401E-42, which is larger than 0. Tests indicate that these parameters
  actually accept the full range of float values; i.e. -3.4E+38 to 3.4E+38
   
- There are at least three error codes (see
  :class:`~turboctl.telegram.codes.ParameterError`) which the pump may report
  when it fails to access a parameter, but which aren't documented in the
  manual.
  Error code 3 seems to signify an index error, error code 5 is raised
  when the parameter access mode doesn't match the parameter being accessed
  (e.g. a telegram tries to read a field value in an unindexed mode), and code
  102 is raised when the "save data to nonvolatile memory" command has been
  given by writing a value to parameter 8, and then a value that is being saved
  is accessed too soon after.  

- Parameters 8 and 134 are listed as having the type "s16" (i.e. a 16-bit
  signed integer) in the manual, but their minimum and maximum values are given
  as 0 and 65535. This suggests that they are actually unsigned integers
  instead of signed ones.
  

Notes and clarifications
------------------------   

The points listed in this section aren't errors, but simply elaborate on
details that the manual doesn't cover. Some of these details are useful
knowledge to any user, but most are only useful for making the
virtual pump (see :mod:`~turboctl.virtualpump.virtualpump`) work more
like the actual pump.

- The "pump on" and "pump off" commands sent via a telegram only affect whether
  the pump is pumping or not. The off state doesn't prevent the pump from
  communicating normally via telegrams or reset variables saved in volatile
  memory; only physically cutting off the power to the pump does this.

- The most common :class:`status bits <turboctl.telegram.codes.StatusBits>`
  seem to be reported in the following situations:
  
  **OPERATION**
    When the pump is in the on state.
    When the "pump off" command is issued, the reply will still contain this
    status bit, since the pump hasn't had any time to turn off.
  
  **READY**
    When the pump is in the off state.
    When the "pump on" command is issued, the reply will still contain this
    status bit, since the pump hasn't had any time to turn on.
  
  **PARAM_CHANNEL**
    The pump seems to include this status bit in every telegram.
  
  **DETAINED**
    The pump reports this status bit quite often, but the reason is unclear.
    
  **TURNING**
    When the pump is turning (i.e. the frequency is not 0).
  
  **PROCESS_CHANNEL**
    Whenever the ``ON`` and ``COMMAND`` command bits have been supplied
    (probably supplying just the ``COMMAND`` bit by itself would be enough to
    get this status bit, but that hasn't been tested).
    
  **ACCELERATION**
    When the pump is accelerating; i.e. the frequency is increasing.
    The reply to a "pump on" command doesn't include this bit, since the pump
    hasn't had any time to start accelerating.
  
  **DECELERATION**
    Like ``ACCELERATION``, but for deceleration instead of acceleration.

- When access to a parameter fails for whatever reason, the reply telegram
  will contain the original parameter number and index, but the parameter value
  will be replaced by an error code. The response code will be
  :class:`ERROR <turboctl.telegram.codes.ParameterResponse>`.

- If a telegram tries to write a value into an unwritable parameter, a
  :class:`CANNOT_CHANGE <turboctl.telegram.codes.ParameterError>` error code
  will be returned.
  Since error codes are always accompanied by the
  :class:`ERROR <turboctl.telegram.codes.ParameterResponse>` response code, the
  :class:`NO_WRITE <turboctl.telegram.codes.ParameterError>` response code
  doesn't seem to be used anywhere.

- When an unindexed parameter is accessed, the parameter index should be
  assigned to 0 in the telegram. Using another index will return an
  :class:`INDEX<turboctl.telegram.codes.ParameterError>` error.

- If a valid parameter number is specified but the parameter access code is
  :class:`NONE <turboctl.telegram.codes.ParameterAccess>`, the reply telegram
  will contain the :class:`NONE <turboctl.telegram.codes.ParameterResponse>`
  response code and the parameter number, index and value of the original
  telegram.
  However, if the parameter index is invalid, an
  :class:`INDEX <turboctl.telegram.codes.ParameterError>` error code will be
  returned instead of the parameter value, and the response code will be
  :class:`ERROR <turboctl.telegram.codes.ParameterResponse>` instead of
  :class:`NONE <turboctl.telegram.codes.ParameterResponse>`.

- Parameter access codes which the pump doesn't recognize seem to work exactly
  like the :class:`NONE <turboctl.telegram.codes.ParameterAccess>` access code.

- Accessing index 0 of an indexed parameter with an unindexed parameter access
  mode works just fine. The response will then contain an unindexed response
  code.
  The reverse doesn't work; unindexed parameters cannot be accessed with an
  indexed access mode (trying to do so results in an
  :class:`ACCESS <turboctl.telegram.codes.ParameterError>` error).
  
- Trying to access an invalid parameter number produces inconsistent results.
  Reading from or writing to parameter 321 (which doesn't exist) results in a
  :class:`WRONG_NUM <turboctl.telegram.codes.ParameterError>` error, regardless
  of parameter index.
  However, trying to read parameter 9 (which also doesn't exist) results in an
  :class:`ACCESS <turboctl.telegram.codes.ParameterError>` error, trying to
  write to it results in a
  :class:`WRONG_NUM <turboctl.telegram.codes.ParameterError>` error, and trying
  to write to an index larger than 0 results in an
  :class:`INDEX <turboctl.telegram.codes.ParameterError>` error.

- A frequency setpoint can be set by supplying the ``COMMAND`` and ``SETPOINT``
  :class:`control bits <turboctl.telegram.codes.ControlBits>` in a telegram
  and writing the desired value in the frequency field.
  This will override the setpoint defined by parameter 24, but only until the
  next telegram is sent. The minimum and maximum values of parameter 24
  also apply to these setpoints; trying to set an invalid value doesn't cause
  any errors, but the frequency will stop changing once it reaches the minimum
  or maximum value.
