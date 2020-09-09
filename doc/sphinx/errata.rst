Errata to the user manual
=========================

The user manual of the pump seems to contain numerous errors and inaccuracies
regarding the behaviour of the pump. It also leaves some details about how the
pump works a bit unclear. This page contains some correction and clarifications
on how the pump works according to the tests that were conducted on it while
testing TurboCtl.

This page contains a list of inaccuracies
that were discovered while testing the pump, as well as clarifications on
matters which the manual leaves unclear.

Errata
------

This section contains a list of errors that were found in the manual.

- Status bit 8 is listed as "No function" in the manual, but is occasionally
  reported by the pump.

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
  manual suggests, cannot be changed (i.e. parameters 18 and 19 aren't
  writable).

- Parameter 1 isn't actually writable, even though according to the manual it
  should be. There are probably several parameters wirth the wrong writability
  listed in the manual, but most parameter's havent been tested.
    
- The manual doesn't specify the writability of parameters 686 and 690.
  Both appear to be writable.

- In the manual, several parameters which have the real type (i.e. are
  floating-point numbers) have a default value of 0 and a minumum value of
  1.401E-42, which is larger than 0. Tests indicate that these parameters
  actually accept the full range of float values; i.e. -3.4E+38 to 3.4E+38.
  All real-valued parameters are listed as having these limits in the info
  command, but not all are actually tested.
   
- There are at least three error codes which the pump may report when it fails
  to access a parameter, but which aren't documented in the manual.
  Error code 3 seems to signify an index error, error code 5 is raised
  when the parameter access mode doesn't match the parameter being accessed
  (i.e. a field value is read in unindexed mode), and code 102 is raised when
  the "save data to nonvolatile memory" command has been given by writing a
  value to parameter 8, and then a value that is being saved is accessed too
  soon after.  

- Parameters 8 and 134 are listed as having the type s16 (i.e. a 16-bit signed
  integer) in the manual, but their minimum and maximum values are given as
  0 and 65535. This suggests that they are actually unsigned integers instead of
  signed ones, since that is the range for 16-bit unsigned integers.
  

Notes and clarifications
------------------------   

The points listed in this section aren't errors, but simply elaborate on
details that the manual doesn't cover. Some of these details are useful
knowledge to any user, but most are only useful for making the
:mod:`virtualpump` package work more like the actual pump.  

  
- Notes about when different status bits are reported:
  OPERATION: When the pump is on, including when the off command is given
  READY: When the pump is off, including when the on command is given
  PARAM_CHANNEL: Always.
  DETAINED: This is displayed frequently, but it is unclear why.
  TURNING: When the pump is turning (i.e. frequency is not 0).
  PROCESS CHANNEL: Whenever the ON and COMMAND command bits have been supplied (probably the COMMAND bit is enough).
  ACCELERATION and DECELERATION: Self-evident. Pump only starts accelerating/decelerating after an on/off command has been supllied,
  so the reply to the command wont include these bits.

- When an unindexed parameter is accessed, the parameter index should be
  assigned to 0 in the telegram. Using another index will raise an INDEX_ERROR.

- When access to a parameter fails for whatever reason, the return telegram
  will contain the original parameter number and index, but the parameter value
  will be replaced by the error code.

- If a telegram tries to write a value into an unwritable parameter, a
  CANNOT_CHANGE error code will be returned. The 'no change' reply code
  doesn't seem to be used anywhere.

- The on/off commands sent via a telegram only affect whether the pump is
  pumping or not. The off state doesn't prevent the pump from communicating
  normally via telegrams or reset variables saved in volatile memory; only
  physically cutting off the power to the pump does this.

- Tests:
  write 9: Error 5: ACCESS
  read 9 Error 1: CANNOT_CHANGE
  write 321: Error 0: WRONG NUM
  read 321: WRONG NUM
  write 321[5]: WRONG NUM
  write 9[5]: INDEX ERROR

- If a parameter number is specified but there is no parameter access, 
  will the parameter data be included in the return telegram?
  INDEX ERROR will still be raised, index and number will be returned
  number and value will be mirrored back if there is no access
  also tested with indexed parameter, in which case index is also mirrored

- Does the pump return a parameter error if the parameter access code is 
  invalid?
  It returns INDEX ERROR if the index is wrong. Otherwise it will return reply mode 'none', value 0, number and index are mirrored.

- What happens when accessing index 0 of an indexed parameter in unindexed mode etc.
  It works; the response mode will be unindexed. This doesn't work vice versa (inindexed parameters cvan't be accesses in indexed mode.)

- What happens if the frequency setpoint is set to an illegal value through 
  the setpoint command (without accessing parameters)?
  Telegram Setpoint only applies until the next telegram is sent (at which point the contro is set back to the parameter).
  Thew frequency doesn't change below 750 Hz. 

- What is the hierarchy of parameter errors? If there are multiple things
  wrong with a telegram, which error is returned?
  No time for extensive testing, but INDEX ERROR seems to take priority.

- Does parameter 227 (warnings) work analogously compared to parameter 171 (error list).
  No, it seems to be a word of 16 boolean flags.
