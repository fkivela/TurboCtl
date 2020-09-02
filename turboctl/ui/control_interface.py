import time
import threading
from dataclasses import dataclass, field 
from typing import Callable

import serial

from turboctl.telegram import api


@dataclass
class Status:
    """This class stores information about the current status of the pump."""
    
    frequency: float = 0.0
    """The stator frequency in Hz."""
    
    temperature: float = 0.0
    """The frequency converter temperature in °C."""
    
    current: float = 0.0
    """The motor current in A."""
    
    voltage: float = 0.0
    """The intermediate circuit voltage in V."""
    
    pump_on: bool = True
    """A boolean flag to keep track whether the pump is on or off."""
    
    status_bits: list = field(default_factory=list)
    """A list of the status conditions
    (:class:`~turboctl.telegram.codes.StatusBits` members) affecting the pump.
    """
    
    callback: Callable = None
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
    'port'    : '/dev/ttyUSB0',
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
        """
        self.status = Status()
        self.timestep = 1
        
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
            self.get_status()
            time.sleep(self.timestep)

    def pump_on(self):
        """Turn the pump on."""
        self.status.pump_on = True
        return self.get_status()
    
    def pump_off(self):
        """Turn the pump off."""
        self.status.pump_on = False
        return self.get_status()

    def get_status(self):
        """Ask pump status by sending an empty telegram."""
        # This is named "get_status" instead of "status", since "status" is
        # already an attribute.
        query, reply = api.status(self._connection, pump_on=self.status.pump_on)
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
    
    def test(self, *args, **kwargs):
        return api.test(self._connection, *args, **kwargs)
    
    def _update_status(self, reply):
        """Update self.status based on the reply from the pump
        (a TelegramReader object).
        """
        self.status.frequency = reply.frequency
        self.status.temperature = reply.temperature
        # The pump reports current and voltage in 0.1 A/V.
        self.status.current = reply.current / 10
        self.status.voltage = reply.voltage / 10
        self.status.status_bits = reply.flag_bits
