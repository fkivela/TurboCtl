"""This module provides a more user friendly intefrace to the Telegram 
class.
"""
from ..data import (Types, PARAMETERS, ParameterAccess, ParameterResponse, 
                    ParameterError, ControlBits, StatusBits)    

from .telegram import Telegram


class TelegramWrapper(Telegram):
    """An abstract superclass for Query and Reply objects.
    
    Query and Reply objects provide a layer of abstraction on top of 
    Telegram objects. Parameters can be accessed by setting the 
    *parameter_number* and *parameter_mode* properties of a 
    TelegramWrapper class, without knowing the size or type of the 
    parameter. Control and status bits can be defined as a set of 
    enum instances instead of a string of '1's and '0's.
    
    telegram_wrapper.control_or_status_set is a SynchronizedSet object 
    which behaves lika an ordinary set, but any changes to it are 
    instantly copied to telegram_wrapper.control_or_status_bits.
    """
        
    READABLE_PROPERTIES = Telegram.READABLE_PROPERTIES + [
        'parameter_type', 
        'parameter_size', 
        'parameter_unit',
        'parameter_indexed',
        'parameter_mode',
        'control_or_status_set'
    ]
    WRITABLE_PROPERTIES = Telegram.WRITABLE_PROPERTIES + [
        'parameter_mode', 
        'control_or_status_set']
    
    parameters = PARAMETERS
    # The set of parameters can be changed for testing purposes.
    enum = None
    # *enum* is set in subclasses.
    
    def __init__(self, *args, **kwargs):
        """Initialize a new TelegramWrapper.
        All arguments are passed to the Telegram class.
        """
        self._control_or_status_set = SynchronizedSet(self._update_cs_bits)
        self.cs_bit_lock = False
        
        # *parameter_number* can't be changed after initialization, 
        # because the values of other properties depend on it.
        self._parameter_number_is_set = False
        super().__init__(*args, **kwargs)
        self._parameter_number_is_set = True
        # Update cs set in case *self* was created from data.
        self._update_cs_set()
        
    def _set_kwargs(self, **kwargs):
        """Initialize properties given as keyword arguments."""
        try:
            # Set *parameter_number* before other kwargs.
            self.parameter_number = kwargs['parameter_number']
            kwargs.pop('parameter_number')
        except KeyError:
            pass
        super()._set_kwargs(**kwargs)
    
    @Telegram.parameter_number.setter        
    def parameter_number(self, value):
        """Set self.parameter_number, or raise a RuntimeError if this 
        method is called after initialization.
        """
        if self._parameter_number_is_set:
            raise RuntimeError(
                'parameter_number cannot be set after initialization')
        Telegram.parameter_number.fset(self, value)
    
    @property
    def _parameter(self):
        """Return a parameter object or None, if a parameter 
        corresponding to self.parameter_number doesn't exist.
        """
        try:
            return self.parameters[self.parameter_number]
        except KeyError:
            return None
        
    @property
    def parameter_type(self):
        """Return the type of the parameter (a Types enum instance), 
        or Types.UINT if a parameter corresponding to 
        self.parameter_number doesn't exist.
        """
        if not self._parameter:
            return Types.UINT
        return self._parameter.type
    
    @property
    def parameter_size(self):
        """Return the size of the parameter in bits, or 0 if a 
        parameter corresponding to self.parameter_number 
        doesn't exist.
        """
        if not self._parameter:
            return 0
        return self._parameter.size
    
    @property
    def parameter_unit(self):
        """Return the unit of the parameter (a string), or '' if a
        parameter corresponding to self.parameter_number doesn't exist.
        """
        if not self._parameter:
            return ''
        return self._parameter.unit
    
    @property
    def parameter_indexed(self):
        """Return a boolean describing whether the parameter is 
        indexed (return True) or not (return False), or False if a
        parameter corresponding to self.parameter_number doesn't exist.
        """
        if not self._parameter:
            return False
        return bool(self._parameter.indices)
        
    @property
    def parameter_value(self):
        """Get or set the value of the parameter.
        
        The getter returns a positive or negative int or a float; the 
        return type is set automatically according to the parameter.
        
        The setter raises a TypeError if the type of *value* doesn't 
        match the parameter.
        """
        return self.get_parameter_value(self.parameter_type)
    
    @parameter_value.setter
    def parameter_value(self, value):             
        try:
             typed_value = Types.to_type(value, self.parameter_type)
        except TypeError as e:
            raise TypeError(
                    f"The type of *value* (now {type(value)}) should match "
                    f"the type of the parameter "
                    f"({self.parameter_type.description})"
                    ) from e
        Telegram.parameter_value.fset(self, typed_value)
        
    @property        
    def parameter_mode(self):
        """Get or set parameter access or response mode. 
        This property is defined the subclasses of this class.
        """
        raise NotImplementedError('This is an abstract function left '
                                  'to be defined in subclasses.')
        
    @parameter_mode.setter
    def parameter_mode(self):
        raise NotImplementedError('This is an abstract function left '
                                  'to be defined in subclasses.')
    
    @property
    def control_or_status_set(self):
        """Get or set control or status bits as a set of enum 
        instances.
        
        The set returned by the getter is a SynchronizedSet object, 
        which updates self.control_or_status_set every time it is changed.
        
        Setting this property to a new set updates the SynchronizedSet 
        object instead of replacing it.
        """
        return self._control_or_status_set
    
    @control_or_status_set.setter
    def control_or_status_set(self, value):
        self.control_or_status_set.clear()
        self.control_or_status_set.update(value)
        self._update_cs_bits()
    
    @property
    def control_or_status_bits(self):
        """Get or set self.control_or_status_bits, and update 
        self.control_or_status_set accordingly.
        """
        return super().control_or_status_bits
    
    @control_or_status_bits.setter
    def control_or_status_bits(self, value):
        Telegram.control_or_status_bits.fset(self, value)
        self._update_cs_set()
    
    def _update_cs_bits(self):
        """Update self.control_or_status_bits to match 
        self.control_or_status_set.
        """
        if self.cs_bit_lock:
            return
        
        indices = [i.value for i in self.control_or_status_set]        
        bits = ''.join(['1' if i in indices else '0' for i in range(16)])
        
        # The lock prevents a recursive loop where accessing 
        # self.control_or_status_set calls this method again.
        self.cs_bit_lock = True
        self.control_or_status_bits = bits    
        self.cs_bit_lock = False
        
    def _update_cs_set(self):
        """Update self.control_or_status_set to match 
        self.control_or_status_bits.
        """
        if self.cs_bit_lock:
            return

        bits = self.control_or_status_bits
        set_ = {self.enum(i) for i, bit in enumerate(bits) if bit == '1'}
        
        # The lock prevents a recursive loop where accessing 
        # self.control_or_status_bits calls this method again.
        self.cs_bit_lock = True
        self.control_or_status_set.update(set_)
        self.cs_bit_lock = False    
        
        
class SynchronizedSet(set):
    """Objects of this class behave like a set, but call 
    self.upon_update every time the contents of the set are changed.
    """
    
    def __init__(self, upon_update, *args, **kwargs):
        """Initialize a new SynchronizedSet.
        
        Args:
            upon_update: A function to be run whenever a method that 
                can change the contents of this set is called.
            Other arguments are passed to the set class.
        """
        super().__init__(*args, **kwargs)
        self.upon_update = upon_update

        update_methods = [
            'add', 'clear', 'difference_update', 'discard', 
            'intersection_update', 'pop', 'remove', 
            'symmetric_difference_update', 'update'
        ]
        for name in update_methods:
            method = getattr(self, name)
            new_method = self._add_upon_update(method)
            setattr(self, name, new_method)
        
    def _add_upon_update(self, method):
        """Add a call to self.upon_update to the end of *method* and 
        return the result.
        """
        def new_method(*args, **kwargs):
            method(*args, **kwargs)
            self.upon_update()
        return new_method

                                    
class Query(TelegramWrapper):
    """This class provides a user-friendly interface to telegrams sent 
    to the pump.
    """
    
    enum = ControlBits
    
    @property
    def parameter_mode(self):
        """Get or set parameter access mode. 
        
        Setting this parameter automatically sets
        self.parameter_access_type to the correct access code,
        and the getter returns a word corresponding to that code.
        
        Valid values are 'none', 'read', 'write' and 'invalid'. 
        A value of 'invalid' signifies an unrecognized parameter 
        access code.
        """
        code = self.parameter_access_type
        try:
            mode_ = ParameterAccess(code)
        except ValueError:
            return 'invalid'
            
        if mode_ in ParameterAccess.read_modes():
            return 'read'
        
        if mode_ in ParameterAccess.write_modes():
            return 'write'
        
        return 'none'
    
    @parameter_mode.setter
    def parameter_mode(self, value):
        if value == 'none':
            self.parameter_access_type = ParameterAccess.NONE.value
            return
        
        if value == 'invalid':
            self.parameter_access_type = ParameterAccess.invalid_code()
            return
           
        if self.parameter_indexed:
            modes_by_index = ParameterAccess.indexed_modes()
        else: 
            modes_by_index = ParameterAccess.unindexed_modes()
            
        if self.parameter_size == 16:
            modes_by_size = ParameterAccess.sixteen_bit_modes()
        elif self.parameter_size == 32:
            modes_by_size = ParameterAccess.thirty_two_bit_modes()
        elif self.parameter_size == 0:
            raise ValueError(
                f'self.parameter_mode cannot be set because '
                'self.parameter_number (self.parameter_number) is invalid')
        else:
            raise RuntimeError(
                f'self.parameter_size should be 0, 16 or 32, not '
                f'{self.parameter_size}')
                        
        if value == 'read':
            modes_by_access = ParameterAccess.read_modes()
        elif value == 'write':
            modes_by_access = ParameterAccess.write_modes()
        else:
            if not isinstance(value, str):
                raise TypeError(f'*value* should be a str, not {type(value)}')
            
            raise ValueError(
                f"*value* should be 'read', 'write', 'none' ot 'invalid', "
                f"not {value}")
            
        mode_set = modes_by_access & modes_by_index & modes_by_size
        
        if len(mode_set) != 1:
            raise RuntimeError(
                    f'len(mode_set) should be 1, not {len(mode_set)}')
        
        mode = mode_set.pop()
        self.parameter_access_type = mode.value
        

class Reply(TelegramWrapper):
                
    WRITABLE_PROPERTIES = TelegramWrapper.WRITABLE_PROPERTIES + [
        'error_code'
    ]
    READABLE_PROPERTIES = TelegramWrapper.READABLE_PROPERTIES + [
        'error_code', 
        'error_message'
    ] 
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
        the parameter value. This means that the error code will be 
        nonsensical if the parameter value is defined and vice versa.
        
        Setter raises:
            TypeError: If *value* is not a valid unsigned integer.
        """
        return self.get_parameter_value(Types.UINT)
        
    @error_code.setter
    def error_code(self, value):
        
        if not Types.is_type(value, Types.UINT):
            raise TypeError(f'*value* ({value}) should be an unsigned integer')
        
        # Use the telegram setter, so that *value* will not be 
        # converted into the type of the parameter.
        Telegram.parameter_value.fset(self, value)
    
    @property
    def parameter_mode(self):
        """Get or set parameter response mode. 
        
        Setting this parameter automatically sets
        self.parameter_access_type to the correct response code,
        and the getter returns a word corresponding to that code.

        Valid values are 'none', 'response', 'error', 'no write' and 
        'invalid'. A value of 'invalid' signifies an unrecognized 
        parameter response code.
        """

        code = self.parameter_access_type
        try:
            mode_ = ParameterResponse(code)
        except ValueError:
            return 'invalid'
        
        if mode_ is ParameterResponse.NONE:
            return 'none'
                
        if mode_ is ParameterResponse.ERROR:
            return 'error'
        
        if mode_ is ParameterResponse.NO_WRITE:
            return 'no write'
        
        return 'response'
    
    @parameter_mode.setter
    def parameter_mode(self, value):
        if value == 'none':
            self.parameter_access_type = ParameterResponse.NONE.value
            return
        
        if value == 'invalid':
            self.parameter_access_type = ParameterResponse.invalid_code()
            return
        
        if value == 'error':
            self.parameter_access_type = ParameterResponse.ERROR.value
            return
        
        if value == 'no write':
            self.parameter_access_type = ParameterResponse.NO_WRITE.value
            return
           
        if value != 'response':
            raise ValueError(
                    f"*value* should be 'none', 'error', 'no write' or "
                    f"'response', not {value}")    
        
        if self.parameter_indexed:
            modes_by_index = ParameterResponse.indexed_modes()
        else: 
            modes_by_index = ParameterResponse.unindexed_modes()
            
        if self.parameter_size == 16:
            modes_by_size = ParameterResponse.sixteen_bit_modes()
        elif self.parameter_size == 32:
            modes_by_size = ParameterResponse.thirty_two_bit_modes()
        elif self.parameter_size == 0:
            raise ValueError(
                f'self.parameter_mode cannot be set because '
                'self.parameter_number (self.parameter_number) is invalid')
        else:
            raise RuntimeError(
                f'self.parameter_size should be 0, 16 or 32, not '
                f'{self.parameter_size}')
                            
        mode_set = modes_by_index & modes_by_size
        
        if len(mode_set) != 1:
            raise RuntimeError(
                    f'len(mode_set) should be 1, not {len(mode_set)}')
        
        mode = mode_set.pop()
        self.parameter_access_type = mode.value