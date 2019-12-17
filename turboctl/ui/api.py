import threading
import time
from dataclasses import dataclass
from typing import Callable

import serial

from turboctl.telegram import Query, Reply, ControlBits, serial_kwargs


@dataclass
class Status:
    frequency: float = 0.0
    temperature: float = 0.0
    current: float = 0.0
    voltage: float = 0.0
    pump_on: bool = True
    callback: Callable = None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self.callback:
            self.callback(self)


class API():
     
    def __init__(self, port=None, auto_update=False):
        self.status = Status()
        self.timestep = 1
        
        if not port:
            port = serial_kwargs['port']

        serkwargs = {
            k: v for k, v in serial_kwargs.items() if k != 'port'}

        self._connection = serial.Serial(port=port, **serkwargs)

        self._stop_flag = threading.Event()
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run_autoupdate,
                                        daemon=True)

        if auto_update:
            self._thread.start()
            
    def __enter__(self):
        return self

    def close(self):
        self._stop_flag.set()
        self._connection.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
            
    def _run_autoupdate(self):
        while not self._stop_flag.is_set():
            self.full_status()
            time.sleep(self.timestep)
           
    def send(self, telegram):
        self._connection.write(bytes(telegram))
        answer_bytes = self.connection.read(Reply.LENGTH)
        return Reply.from_bytes(answer_bytes)
    
    def get_control_bits(self):
        if self.status.pump_on:
            return {ControlBits.COMMAND, ControlBits.ON}
        else:
            return {}
    
    def status(self):
        query = Query(control_bits=self.get_control_bits())
        reply = self.send(query)
        return {'frequency': reply.frequency,
                'temperature': reply.temperature,
                'current': reply.current,
                'voltage': reply.voltage}
                
    def read_parameter(self, number, index=0):
        query = Query(
            parameter_number=number,
            parameter_index=index,
            parameter_mode='read',
            control_bits = self.get_control_bits()
        )
        reply = self.send(query)
        return reply.parameter_value
    
    def write_parameter(self, value, number, index=0):
        query = Query(
            parameter_number=number,
            parameter_index=index,
            parameter_mode='write',
            control_bits=self.get_control_bits()
        )
        reply = self.send_and_receive(query)
        return reply.parameter_value
