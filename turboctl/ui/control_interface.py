import time
import threading
from dataclasses import dataclass, field 
from typing import Callable, Optional

import serial

from turboctl.telegram import api, codes


@dataclass
class Status:
    """This class stores information about the current status of the pump.

    The values are based on those reported by the pump; if a command is sent to
    the pump to set a value to X, the value stored here should only be changed
    once the pump has reported the new changed value.

    Values of None indicate unknown values that the pump hasn't reported yet.
    """

    frequency: Optional[float] = None
    """The stator frequency in Hz."""
    
    temperature: Optional[float] = None
    """The frequency converter temperature in °C."""
    
    current: Optional[float] = None
    """The motor current in A."""
    
    voltage: Optional[float] = None
    """The intermediate circuit voltage in V."""

    pump_on: Optional[bool] = None
    """Indicates whether the pump is on or off."""

    status_bits: Optional[list] = None
    """A list of the status conditions
    (:class:`~turboctl.telegram.codes.StatusBits` members) affecting the pump.
    """

    callback: Optional[Callable] = None
    """A function that is called every time the contents of this object
    are changed. Its signature should be
    ::

        callback(status: Status) -> None
        
    so that it can be called with
    
    ::

        self.callback(self)
        
    Note that since this isn't a bound method, the *self* argument must be
    explicitly passed to the function. 
    """

    def __setattr__(self, name, value):
        """Call :attr:`callback(self) <callback>` whenever an attribute
        is set.
        """
        super().__setattr__(name, value)
        if self.callback:
            self.callback(self)


SERIAL_KWARGS = {
    'port'    : '/dev/ttyACM0',
    'baudrate': 19200,
    'bytesize': serial.EIGHTBITS,
    'parity'  : serial.PARITY_EVEN,
    'stopbits': serial.STOPBITS_ONE,
    'timeout' : 1
}
"""Keyword arguments for creating a :class:`serial.Serial` instance."""


class ControlInterface():
    """This class represents a connection to the pump and can be used to send
    commands to it.
    
    All methods that send commands to the pump return both the query sent to
    the pump and the reply received back as
    :class:`~turboctl.telegram.telegram.TelegramReader` instances.
    
    Attributes:
        status (Status):
            An object that stores the current state of the pump.
            Its attributes are updated every time the pump sends
            back a reply.

        timestep (int or float):
            If *self* was initialized with ``auto_update=True``, this
            determines the time (in seconds) between automatic telegrams.
            The default value is ``1``.

        on_command (bool):
            If this is ``True``, automatic telegrams send the ``pump_on``
            command to the pump instead of ``get_status''.

            See the ``auto_update`` argument of ``__init__`` for further
            details.
            
            The default value is ``None``, which gets updated by the ``status``
            method to match the current state of the pump.
    """

    def __init__(self, port=None, auto_update=False):
        """Initialize a new :class:`ControlInterface`.
        
        Args:
            port (str):
                The device name for the serial port through which the 
                connection is formed. If no value is given, the one defined in
                :const:`SERIAL_KWARGS` is used.

            auto_update (bool):
                If this is ``True``, this object will automatically send a 
                telegram to the pump every :attr:`timestep` seconds and
                update :attr:`status` accordingly. Otherwise :attr:`status`
                will only be updated whenever a command is sent by the user
                calling a method of this class.
                
                If ``self.status.pump_on`` is ``True``, the automatic telegram
                will be ``pump_on`` instead of ``get_status''.
                This is to prevent the pump from automatically switching off,
                which it does if it hasn't received a ``pump_on`` command for
                10 seconds. 
        """
        self.status = Status()
        self.timestep = 1
        self.on_command = None
        
        kwargs = SERIAL_KWARGS.copy()
        if port:
            kwargs['port'] = port

        # This may raise a serial.SerialException.
        self._connection = serial.Serial(**kwargs)

        # An event flag to close the parallel thread.
        self._stop_flag = threading.Event()

        # _lock prevents messages from being sent at the same time by
        # _run_autoupdate and the user.
        self._lock = threading.Lock()        
        self._thread = threading.Thread(target=self._run_autoupdate,
                                        daemon=True)
        
        # _thread and _lock are created even with auto_update=False,
        # since they are referenced by methods.
        if auto_update:
            self._thread.start()
            
    def __enter__(self):
        """Called upon entering a ``with`` block; returns *self*."""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Called upon exiting a ``with`` block; calls :meth:`close`.
        
        The arguments are ignored.
        """
        self.halt()

    def close(self):
        """Close the connection to the pump. If this object was created with
        ``auto_update=False``, the parallel thread sending the update
        telegrams is also closed.
        """
        self._stop_flag.set()
        self._connection.close()

    def _run_autoupdate(self):
        """Periodically send a telegram to the pump and update self.status
        based on the response.
        """
        while not self._stop_flag.is_set():
            if self.on_command:
                self.pump_on()
            else:    
                self.get_status()
            time.sleep(self.timestep)

    def pump_on(self):
        """Turn the pump on.

        This sets ``self.on_command`` to True.
        """
        query, reply = api.status(self._connection, pump_on=True)
        # Only set set self.pump_on=True if the pump actually reports turning
        # on.
        self._update_status(reply)
        self.on_command = True
        return query, reply

    def pump_off(self):
        """Turn the pump off.

        This sets ``self.on_command`` to False.
        """
        query, reply = api.status(self._connection, pump_on=False)
        self._update_status(reply)
        self.on_command = False
        return query, reply

    def get_status(self, pump_on=None):
        """Ask pump status by sending an empty telegram.
        
        If ``self.on_command`` is ``None``, this updates it to
        ``self.status.pump_on``.
        This means that a pump that is on when TurboCtl is started stays on,
        and a pump that is off stays off.
        """
        # This is named "get_status" instead of "status", since "status" is
        # already an attribute.
        query, reply = api.status(self._connection)
        self._update_status(reply)

        if self.on_command is None:
            self.on_command = self.status.pump_on

        return query, reply

    def reset_error(self):
        #TODO
        query, reply = api.reset_error(self._connection)
        self._update_status(reply)
        return query, reply

    def read_parameter(self, number, index=0):
        """Read the value of an index of a parameter.
        
        Args:
            number
                The number of the parameter.
                
            index
                The index of the parameter (0 for unindexed parameters).
                
        Raises:
            ValueError:
                If *number* or *index* have invalid values.
        """
        query, reply = api.read_parameter(self._connection, number, index, 
                                          pump_on=self.status.pump_on)
        self._update_status(reply)
        return query, reply
    
    def write_parameter(self, number, value, index=0):
        """Write a value to an index of a parameter.
        
        Args:
            number:
                The number of the parameter.
                                
            value:
                The value to be written.
                
            index:
                The index of the parameter (0 for unindexed parameters).
                
        Raises:
            ValueError:
                If *number*, *value* or *index* have invalid values.
        """
        query, reply = api.write_parameter(self._connection, number, value,
                                           index, pump_on=self.status.pump_on)
        self._update_status(reply)
        return query, reply
        
    def _update_status(self, reply):
        """Update self.status based on the reply from the pump
        (a TelegramReader object).
        """
        self.status.frequency = reply.frequency
        self.status.temperature = reply.temperature
        # The pump reports current in 0.1 A.
        self.status.current = reply.current / 10
        self.status.voltage = reply.voltage
        self.status.status_bits = reply.flag_bits
        if codes.StatusBits.OPERATION in reply.flag_bits:
            self.status.pump_on = True
        else:
            self.status.pump_on = False
