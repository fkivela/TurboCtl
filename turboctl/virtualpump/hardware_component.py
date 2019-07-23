import numpy as np
import threading
import time
from dataclasses import dataclass

from ..data import StatusBits, ControlBits
from ..telegram import str_to_int    


class HWParameters():
    
    def __init__(self, parameters):
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
        # Overload error = error 106
        # Power supply error = error 603
        self.power_failure_error_counter = parameters[43]
        self.error_list = parameters[171] #254 indices
        self.error_frequency_list = parameters[174]
        self.error_hour_list = parameters[176]
        self.operating_hours = parameters[184]
        self.warnings = parameters[227]

        
class Variables():
    
    def __init__(self, parameters):
        self.parameters = HWParameters(parameters)
        
    def __setattr__(self, name, value):
        
        if name == 'parameters':
            self.__dict__[name] = value
            return
        
        getattr(self.parameters, name).value = value
        
    def __getattr__(self, name):
        
        if name == 'parameters':
            return self.__dict__[name]
        
        return getattr(self.parameters, name).value
    
        
class HardwareComponent():
    """This class defines the part of a VirtualPump that handles 
    hardware data and command/status words.
    """
    
    def __init__(self, parameters, lock):
        
        self.parameters = parameters
        self.variables = Variables(parameters)
        
        self.step = 0.1 
        self.abs_acceleration = 100
        
        self.dynamic_status = True # TODO
        self.status_set = set()
        
        self.store()
        self.off()
                
        self.thread = threading.Thread(target=self.run, args=[lock])
        self.stop_flag = threading.Event()
        self.thread.daemon = True
        self.thread.start()
        
    def set_errors(self, numbers, frequencies, hours):
        
        def pad(list_):
            return list_ + (254 - len(list_))*[0]
        
        self.variables.error_list = pad(numbers)
        self.error_frequency_list = pad(frequencies)
        self.error_hour_list = pad(hours)
        
    def set_warnings(self, numbers):
        string = ''.join(['1' if i in numbers else '0' for i in range(16)])                
        self.variables.warnings = str_to_int(string)
        
    def store(self):
        values = {}
        for i, p in self.parameters.items():
            if p.writable:
                try:
                    values[i] = p.value.copy()
                except AttributeError:
                    values[i] = p.value
                
        self.stored_values = values
        
    def restore(self):
        for i, value in self.stored_values.items():
            try:
                self.parameters[i].value = value.copy()
            except AttributeError:
                self.parameters[i].value = value
        
    def on(self):
        self.is_on = True
        self.variables.voltage = 20
        self.variables.current = 10
        self.variables.temperature = 40
        self.variables.motor_power = 30
        self.variables.motor_temperature = 50
        
    def off(self):
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
        #self.parameters.reset() #TODO: add reset to factory defaults
        
    def stop(self):
        self.stop_flag.set()
        
    def handle_control_bits(self, query):

        if not ControlBits.COMMAND in query.control_set:
            return
        
        if ControlBits.START_STOP in query.control_set:
            if self.is_on:
                self.off()
            else:
                self.on()
            
        if ControlBits.FREQ_SETPOINT in query.control_set:
            self.variables.frequency_setpoint = query.frequency
            
        if ControlBits.RESET_ERROR in query.control_set:
            self.set_errors([], [], [])
            
    def handle_status_bits(self, reply):
        
        if not self.dynamic_status:
            reply.status_set = self.status_set
            return
                
        if self.is_on:
            reply.status_set = reply.status_set | {StatusBits.OPERATION}
        else:
            reply.status_set = reply.status_set | {StatusBits.READY}
            
        if self.variables.frequency:
            reply.status_set = reply.status_set | {StatusBits.TURNING}
            
        if self.acceleration > 0:
            reply.status_set = reply.status_set | {StatusBits.ACCELERATION}
            
        if self.acceleration < 0:
            reply.status_set = reply.status_set | {StatusBits.DECELERATION}
            
        errors_present = any(self.variables.error_list)
        if errors_present:
            reply.status_set = reply.status_set | {StatusBits.ERROR}
        
        if self.variables.warnings:
            reply.status_set = reply.status_set | {StatusBits.WARNING}
        
            
    def handle_hardware(self, query, reply):
        """Write hardware data to *reply.*"""

        self.handle_control_bits(query)
        self.handle_status_bits(reply)
        
        reply.frequency = int(self.variables.frequency)
        reply.temperature = self.variables.temperature
        reply.current = self.variables.current
        reply.voltage = self.variables.voltage

    @property
    def acceleration(self):
        if self.variables.frequency < self.frequency_goal:
            return self.abs_acceleration
        elif self.variables.frequency > self.frequency_goal:
            return -self.abs_acceleration
        else:
            return 0
        
    @property
    def frequency_goal(self):
        return self.variables.frequency_setpoint if self.is_on else 0
    
    def change_frequency(self):
        change = self.step * self.acceleration            
        difference = self.frequency_goal - self.variables.frequency
        
        if abs(change) > abs(difference):
            change = difference

        self.variables.frequency += change
                
    def run(self, lock):
        while not self.stop_flag.is_set():
            time.sleep(self.step)        
            lock.acquire()
            self.change_frequency()
            lock.release()