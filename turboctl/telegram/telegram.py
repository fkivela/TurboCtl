from __future__ import annotations
from functools import singledispatch, update_wrapper

from turboctl.telegram.datatypes import Uint, Sint, Bin


# singledispatchmethod is included in Python 3.8, 
# but not earlier versions.
# Until support for Python 3.8 becomes more widespread,
# this implementation (copied from StackOverflow)
# has to work as a placeholder.
def singledispatchmethod(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kwargs):
        return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper


class DataDescriptor:
    datatype = None        
    
    def __init__(self, value=0, bits=8):
        self.value = self.datatype(value, bits)

    def __get__(self, obj, objtype=None):        
        if not objtype:
            return self        
        return self.value.to_builtin()

    def __set__(self, obj, value):
        self.value = self.datatype(value, self.value.bits)


class UintDescriptor(DataDescriptor):
    datatype = Uint


class SintDescriptor(DataDescriptor):
    datatype = Sint


class BinDescriptor(DataDescriptor):
    datatype = Bin


class DescriptorAccessor:
    
    def __init__(self, object_):
        self.object_ = object_
    
    def __getattr__(self, name):
        class_ = type(self.object_)
        descriptor = getattr(class_, name)
        return descriptor.value


class Telegram:
    
    LENGTH = 24
    
    parameter_code   = BinDescriptor( value='0000', bits=4),
    parameter_number = UintDescriptor(value=0,      bits=11),
    parameter_index  = UintDescriptor(value=0,      bits=8),
    parameter_value  = UintDescriptor(value=0,      bits=32),
    flag_bits        = BinDescriptor( value=set(),  bits=16),
    frequency        = UintDescriptor(value=0,      bits=16),
    temperature      = SintDescriptor(value=0,      bits=16),
    current          = UintDescriptor(value=0,      bits=16),
    voltage          = UintDescriptor(value=0,      bits=16),
    
    @property
    def data(self):
        return self._data
    
    @singledispatchmethod
    def __init__(self, bytes_=None, **kwargs):
        self._data = DescriptorAccessor(self)
        self.parameter_type = Uint
        
        for name, value in kwargs.items():
            
            name_does_not_exist = not hasattr(self, name)
            name_is_private = name[0] == '_'
            
            if name_does_not_exist or name_is_private:
                raise TypeError(f'invalid keyword: {name}')
            
            setattr(self, name, value)
        
    @__init__.register
    def from_bytes(self, bytes_: bytes):
        self._check_valid_telegram(bytes_)
        
        code_and_number_bits = Bin(bytes_[3:5])
        self.parameter_code = Bin(code_and_number_bits[0:4])
        self.parameter_number = Uint(code_and_number_bits[5:16])
        
        self.parameter_index = Uint(bytes_[6])
        self.parameter_value_uint = Uint(bytes_[7:11])
        self.flag_bits = Bin(bytes_[11:13][::-1])
        
        self.frequency = Uint(bytes_[13:15])
        self.temperature = Sint(bytes_[15:17])
        self.current = Uint(bytes_[17:19])
        self.voltage = Uint(bytes_[21:23])        
        
    @classmethod
    def _check_valid_telegram(cls, bytes_):
        
        if len(bytes_) != 24:
            raise ValueError(f'len(bytes_) should be 24, not {len(bytes_)}')
        
        if bytes_[0] != 2:
            raise ValueError(f'bytes_[0] should be 2, not {bytes_[0]}')
            
        if bytes_[1] != 22:
            raise ValueError(f'bytes_[1] should be 22, not {bytes_[1]}')
            
        checksum = cls.checksum(bytes_[0:23])[0]
        if bytes_[23] != checksum:
            raise ValueError(
                f'bytes_[23] (the checksum) should be '
                f'{checksum}, not was {bytes_[23]}')
    
    def to_bytes(self):      
        data = [
            Uint(2, 8),                 # STX
            Uint(22, 8),                # LGE
            Uint(0, 8),                 # ADR
            self.data.parameter_code,   # PKE
            Bin('0'),
            self.data.parameter_number[-11:], 
            Uint(0, 8),                 # Reserved
            self.data.parameter_index,  # IND 
            self.data.parameter_value,  # PWE
            self.data.flag_bits[::-1],  # PZD1    
            self.data.frequency,        # PZD2
            self.data.temperature,      # PZD3
            self.data.current,          # PZD4 
            Uint(0, 16),                # Reserved
            self.data.voltage           # PZD6
        ]
        bytes_ = bytes(data)
        return bytes_ + self.checksum(bytes_)
        
    @property
    def parameter_value(self):
        return self.parameter_type(self.parameter_value_uint)
    
    @parameter_value.setter
    def parameter_value(self, value):
        actual_value = self.parameter_type(value, bits=32)
        self.parameter_value = Uint(actual_value)
        
    @staticmethod
    def checksum(bytes_):
        numbers = tuple(bytes_)        
        checksum = 0
        for i in numbers:
            checksum = checksum ^ i  
        return bytes([checksum])
    
    def __str__(self):
        pass

    def __eq__(self, other):
        pass
