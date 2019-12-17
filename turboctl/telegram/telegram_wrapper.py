"""This module provides a more user friendly intefrace to the Telegram 
class.
"""

from collections import OrderedDict
from typing import Dict

from .codes import (ParameterAccess, ParameterResponse, ParameterError, 
                    ControlBits, StatusBits)    
from .parser import Parameter, PARAMETERS
from .numtypes import TurboNum, Uint, Sint, Bin
from .telegram import Telegram


class TelegramWrapper(Telegram):
    """An abstract superclass for Query and Reply objects.
    
    Query and Reply objects provide a layer of abstraction on top of 
    Telegram objects. By setting the parameter_mode attribute to a 
    value such as 'read' or 'write', the parameter access or response 
    code is set automatically to its correct value. Control and status 
    bits can be defined as a set of enum instances instead of a string 
    of '1's and '0's through the flag_set attribute. 
    
    flag_bits and parameter_code can still be accessed, and changes to
    them will also change flag_set and parameter_mode (and vice versa.)
    
    Unlike in the Telegram class, parameter_type is not changed when 
    parameter_value is set. Instead, it is updated each time 
    parameter_number is set to reflect the type of the parameter. 
    parameter_type can also be changed by hand.
    """
    Attribute = Telegram.Attribute
    attributes = OrderedDict((a.name, a) for a in [
        #         name                type       default bits printed writable 
        Attribute('parameter_mode',   str,       'none',   None, 1, 1),
        Attribute('parameter_code',   Bin,       '0000',      4, 0, 1),
        Attribute('parameter_number', Uint,      0,          11, 1, 1),
        Attribute('_parameter',       Parameter, None,     None, 0, 1),
        Attribute('parameter_index',  Uint,      0,           8, 1, 1),
        Attribute('parameter_value',  TurboNum,  0,          32, 1, 1),
        Attribute('_parameter_bytes', bytes,     bytes(4), None, 0, 1),
        Attribute('parameter_type',   type,      Uint,     None, 1, 1),
        Attribute('flag_set',         set,       set(),    None, 1, 1),
        Attribute('flag_bits',        Bin,       16*'0',     16, 0, 1),
        Attribute('frequency',        Uint,      0,          16, 1, 1),
        Attribute('temperature',      Sint,      0,          16, 1, 1),
        Attribute('current',          Uint,      0,          16, 1, 1),
        Attribute('voltage',          Uint,      0,          16, 1, 1),
    ])
    # parameter_code and flag_bits are left out of __repr__ and __str__
    # to keep them shorter. Use self.fullstr() to display them.
    
    enum = None
    
    def __init__(self, parameters: Dict[int, Parameter]=PARAMETERS, 
                 *args, **kwargs): 
        """Initialize a new TelegramWrapper.
       
        Args:
            parameters: The parameter dictionary to be used.
            All other args are passed to Telegram.__init__()
        """
        self.parameters = parameters
        super().__init__(*args, **kwargs)
            
    @property
    def parameter_number(self):
        """Setting parameter_number updates self._parameter and 
        self.parameter_type.
        """
        return self._parameter_number
    
    @parameter_number.setter
    def parameter_number(self, value):
        self._parameter_number = value
        try:
            self._parameter = self.parameters[value]
            self.parameter_type = self._parameter.type_
        except KeyError:
            self._parameter = self.attributes['_parameter'].default
            self.parameter_type = self.attributes['parameter_type'].default
    
    @Telegram.parameter_value.setter
    def parameter_value(self, value):
        """Changing parameter_value doesn't change parameter_type, 
        unlike in the Telegram class.
        """
        self.parameter_bytes = self.parameter_type(value, 32).to_bytes()
        
    @property
    def parameter_code(self):
        """parameter_code is generated from parameter_mode."""
        return Bin(self._mode_to_code(self.parameter_mode))
    
    @parameter_code.setter
    def parameter_code(self, value):
        """Setting parameter_code updates parameter_mode."""
        self.parameter_mode = self._code_to_mode(value)
                
    @property
    def flag_bits(self):
        """flag_bits are generated from flag_set."""
        return Bin(self._set_to_bits(self.flag_set))
    
    @flag_bits.setter
    def flag_bits(self, value):
        """Setting flag_bits updates flag_set.
        
        flag_set remains the same object, so flag_set.add() works.
        """
        self.flag_set.clear()
        self.flag_set.update(self._bits_to_set(value))
        
    def _bits_to_set(self, bits):
        """Convert flag_bits to flag_set."""
        return {self.enum(i) for i, bit in enumerate(bits) if bit == '1'}

    def _set_to_bits(self, set_):
        """Convert flag_set to flag_bits."""
        indices = [i.value for i in set_]        
        return ''.join(['1' if i in indices else '0' for i in range(16)])
    
    @staticmethod
    def _code_to_mode(code):
        """Convert parameter_code to parameter_mode.
        
        This method is properly defined in subclasses; it is included 
        here only to make this class initializable for testing.
        """
        return 'none'
    
    def _mode_to_code(self, mode):
        """Convert parameter_mode to parameter_code.
        
        This method is properly defined in subclasses; it is included 
        here only to make this class initializable for testing.
        """
        return '0000'

                     
class Query(TelegramWrapper):
    """This class provides a user-friendly interface to telegrams sent 
    to the pump.
    """
    
    enum = ControlBits
    
    @staticmethod
    def _code_to_mode(code):
        """Convert parameter_code to parameter_mode."""
        try:
            mode_ = ParameterAccess(code)
        except ValueError:
            return f'invalid mode: {code}'
            
        if mode_ in ParameterAccess.read_modes:
            return 'read'
        
        if mode_ in ParameterAccess.write_modes:
            return 'write'
        
        return 'none'
    
    def _mode_to_code(self, mode):
        """Convert parameter_mode to parameter_code.
                
        Valid modes are 'none', 'read' and 'write'. 
        """
        
        if mode == 'none' or not self._parameter:
            return ParameterAccess.NONE.value            
           
        if mode == 'read':
            modes_by_access = ParameterAccess.read_modes
        elif mode == 'write':
            modes_by_access = ParameterAccess.write_modes
        else:        
            raise ValueError(
                f"*mode* should be 'read', 'write' or 'none', not {mode}")
        
        if self._parameter.indices:
            modes_by_index = ParameterAccess.indexed_modes
        else: 
            modes_by_index = ParameterAccess.unindexed_modes
            
        if self._parameter.bits == 16:
            modes_by_size = ParameterAccess.sixteen_bit_modes
        elif self._parameter.bits == 32:
            modes_by_size = ParameterAccess.thirty_two_bit_modes
        else:
            raise RuntimeError(f'self._parameter.bits should be 16 or 32, '
                               f'not {self._parameter.bits}')
                            
        mode_set = modes_by_access & modes_by_index & modes_by_size
        if len(mode_set) != 1:
            raise AssertionError(
                f'len(mode_set) should be 1, not {len(mode_set)}')
        
        return mode_set.pop().value
        

class Reply(TelegramWrapper):
    """This class provides a user-friendly interface to telegrams 
    received from the pump.
    """
    Attribute = TelegramWrapper.Attribute
    attributes = TelegramWrapper.attributes.copy()
    attributes['error_message'] = Attribute(
                                    # name type default bits printed writable 
                                    'error_message', str, None, None, 1, 0)
    attributes['error_code'] = Attribute(
                                    'error_code', Uint, 0, 32, 1, 1)
        
    enum = StatusBits    
    
    @property
    def error_message(self):
        """Return an error message corresponding to the parameter 
        error code, or '' if self.parameter_mode is not 'error'.
        """
        if self.parameter_mode != 'error':
            return ''
        
        try:
            return ParameterError(self.error_code).description
        except ValueError:
            return f'invalid error code: {self.error_code}'
        
    @property
    def error_code(self):
        """Set or get the parameter error code.
        
        The parameter error code is written to the same location as 
        the parameter value. This means that writing the error code 
        will replace the parameter value and vice versa.
        """
        return self.parameter_value.to(Uint)
    
    @error_code.setter
    def error_code(self, value):
        # __setattr__ has already converted *value* to an Uint, 
        # since the error_code attribute has that type.
        self.parameter_value = value.to(self.parameter_type)
    
    @staticmethod
    def _code_to_mode(code):
        """Convert parameter_code to parameter_mode."""
        try:
            mode_ = ParameterResponse(code)
        except ValueError:
            return f'invalid mode: {code}'
        
        if mode_ is ParameterResponse.NONE:
            return 'none'
                
        if mode_ is ParameterResponse.ERROR:
            return 'error'
        
        if mode_ is ParameterResponse.NO_WRITE:
            return 'no write'
        
        return 'response'
        
    def _mode_to_code(self, mode):
        """Convert parameter_mode to parameter_code.
                
        Valid modes are 'none', 'response' 'error' and 'no write'. 
        """        
        if mode == 'none':
            return ParameterResponse.NONE.value

        if mode == 'error':
            return ParameterResponse.ERROR.value
        
        if mode == 'no write':
            return ParameterResponse.NO_WRITE.value
           
        if mode != 'response':
            raise ValueError(
                    f"*mode* should be 'none', 'error', 'no write' or "
                    f"'response', not {mode}")    
        
        if self._parameter.indices:
            modes_by_index = ParameterResponse.indexed_modes
        else: 
            modes_by_index = ParameterResponse.unindexed_modes
            
        if self._parameter.bits == 16:
            modes_by_size = ParameterResponse.sixteen_bit_modes
        elif self._parameter.bits == 32:
            modes_by_size = ParameterResponse.thirty_two_bit_modes
        else:
            raise RuntimeError(f'self._parameter.bits should be 16 or 32, '
                               f'not {self._parameter.bits}')
                            
        mode_set = modes_by_index & modes_by_size        
        if len(mode_set) != 1:
            raise RuntimeError(
                    f'len(mode_set) should be 1, not {len(mode_set)}')
        
        return mode_set.pop().value