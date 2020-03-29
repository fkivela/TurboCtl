"""This module handles parameter access in a VirtualPump."""

from ..telegram import Reply, Parameter, ParameterError


class ParameterComponent():
    """This class defines the part of a VirtualPump that handles 
    parameter access.
    """
    
    def __init__(self, parameters):
        """Initialize a new ParameterComponent.
        
        Args:
            parameters: The parameter dictionary to be used.
                The keys should be parameter numbers and values 
                ExtendedParameter objects.
        """        
        self.parameters = parameters
        self.latest_error = None 
        # This can be used for debugging or testing.
        
    def handle_parameter(self, query):
        """Handle *query* by accessing parameters and returning a 
        Reply object.
        
        Args:
            query: A Query object.
            
        Returns:
            A Reply object. Only parameter access data is written to 
            the reply; handling other data is left to other classes.        
        """
        
        reply = Reply(parameter_number=query.parameter_number,
                      parameter_index=query.parameter_index,
                      parameter_value=query.parameter_value)
        
        if query.parameter_mode == 'none':
            return reply
        
        try:
            reply.parameter_value = self._access_parameter(query)
            reply.parameter_mode = 'response'
            return reply
        
        except CannotChangeError as error:
            # CannotChangeError also contains an error code, 
            # but the 'no write' parameter response option 
            # seems to be the option more likely used by the pump.
            self.latest_error = error
            reply.parameter_mode = 'no write'
            return reply
        
        except ParameterAbstractError as error:
            self.latest_error = error                
            reply.parameter_mode = 'error'
            reply.error_code = error.CODE
            return reply

    def _access_parameter(self, query):
        """Write or read the value of a parameter.
        
        Args:
            query: A Query object.
                
            Raises:
                RuntimeError: If query.parameter_mode is not any of 
                    the values it should be.
        """
        
        try:
            parameter = self.parameters[query.parameter_number]
        except KeyError:
            raise ParameterNumberError(
                f'Invalid parameter number: {query.parameter_number}')
        
        if query.parameter_mode == 'read':
            #TODO: Fix
            return parameter.get_value(indexed=bool(query._parameter.indices), 
                                       index=query.parameter_index)
        
        if query.parameter_mode == 'write':
            parameter.set_value(new_value=query.parameter_value,
                                bits=query._parameter.bits, 
                                indexed=bool(query._parameter.indices), 
                                index=query.parameter_index)
            return query.parameter_value
        
        if query.parameter_mode == 'invalid':
            raise OtherError(
                f'Invalid parameter mode; '
                f'access code = {query.parameter_access_type}')
        
        raise RuntimeError(
            f"query.parameter_mode should be 'none', 'read', 'write' or "
            f"'invalid', not {query.parameter_mode}")


class ExtendedParameters(dict):
    """A dictionary of extended parameters with some functionality 
    added on top of that provided by the dict class."""

    def __init__(self, parameters):
        """Initialize a new ExtendedParameters based on *parameters* 
        (a dict of Parameter objects).
        """
        
        extended_parameters = {}
        max_iters = 5
        # The min and max values of some parameters depend on the 
        # values of other parameters, and so some parameters cannot be 
        # initialized on the first iteration, or the first several 
        # iterations, in case their dependencies also have 
        # dependencies.
        # In practice two iterations seems to be enough if real pump 
        # parameters are used, but there could in theory be long 
        # dependency chains that need more iterations.
        for i in range(max_iters):
            for num, p in parameters.items():
                if num not in extended_parameters.keys():
                    try:
                        extended_parameters[num] = ExtendedParameter(p, self)
                    # A KeyError is raised if a parameter's dependency 
                    # has not been initialized.
                    except KeyError:
                        pass
                    
        super().__init__(extended_parameters)
        

class ExtendedParameter(Parameter):
    """This class represents a parameter that has a value which can 
    change, while the regular Parameter class only describes the 
    immutable attributes of a parameter. 
    
    Changing the value of an extended parameter raises one of the 
    custom parameter errors (ParameterNumberError, CannotChangeError, 
    MinMaxError or OtherError), if the real TURBOVAC pump would do so 
    in that situation. E.g. if an indexed parameter is accessed in 
    unindexed mode, an error is raised, because the TURBOVAC access 
    codes for indexed and unindexed parameters are different.
    """
    
    def __init__(self, parameter, extended_parameters):
        """Initialize a new ExtendedParameter.
        
        Args:
            parameter: The attributes of *parameter* are copied to 
                *self*, and some new attributes are added based on the
                existing ones. 
            extended_parameters: A dictionary of extended parameters 
                (with numbers as keys and objects as values). This 
                is needed, because the min and max values of some 
                parameters depend on the values of other parameters. 
                
        Raises:
            ValueError: If *parameter* has one or more invalid values.
                (See the Parameter class for a description of its valid 
                attribute values.)
        """
        self.__dict__.update(parameter.__dict__)
        self.parameters = extended_parameters
        self.value = self.default_value
        
    def __str__(self):
        """Returns 'ExtendedParameter(attribute1=value1, ...)'."""
        fields = [
            'number', 'name', 'indices', 'indexed', 'min', 'max', 'default', 
            'min_value', 'max_value', 'default_value', 'value', 'unit', 
            'writable', 'type', 'size', 'description']
        
        strings = [f'{f}={repr(getattr(self, f))}' for f in fields]
        string = ', '.join(strings)
        return f'{type(self).__name__}({string})'
        
    @property
    def default_value(self):
        """Return the default value of this parameter.
        
        Returns:
            - An int or a float, if *self* is an unindexed parameter.
            - A list of ints or floats, if *self* is an indexed 
                parameter.
                
        Raises:
            ValueError: If self.default has an invalid value.
        """
        indexed, indices, default = self.indexed, self.indices, self.default
         
        if not indexed and isinstance(default, (int, float)):             
            return default
         
        if indexed and isinstance(default, (int, float)):             
            return len(indices) * [default]
         
        if indexed and isinstance(default, list):
                 
             if len(default) != len(indices):
                 raise ValueError(
                     f'self.default (={default}) should have the '
                     f'same len() as as self.indices (={indices})')                         
             
             return default

        raise ValueError(f'Invalid self.default: {default}')
                    
    @property
    def indexed(self):
        """Returns True IFF *self* is an indexed parameter 
        (i.e. indices != range(0).
        """
        return bool(self.indices)
            
    @property
    def min_value(self):
        """Returns the minimum value of this parameter (int or float).
        
        If self.min returns a reference to the value of another 
        parameter (e.g. 'P18'), this attribute will return the 
        numerical value of that attribute.
        
        Raises:
            ValueError: If self.min has an invalid value.
        """
        return self._get_true_value(self.min_)
    
    @property
    def max_value(self):
        """Returns the maximum value of this parameter (int or float).
        
        If self.max returns a reference to the value of another 
        parameter (e.g. 'P18'), this attribute will return the 
        numerical value of that attribute.
        
        Raises:
            ValueError: If self.max has an invalid value.
        """
        return self._get_true_value(self.max_)
    
    def _get_true_value(self, value):
        """Returns the numerical value (int or float) of *value*.
        
        If *value* is a reference to the value of another 
        parameter (e.g. 'P18'), this attribute will return the 
        numerical value of that attribute.
        
        Args:
            value: int or float; or a string in the format 'P<number>'.
        
        Returns:
            An int or a float.
        
        Raises:
            ValueError: If *value* has an invalid value.
        """
        
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str) and value[0] == 'P':
            
            try:
                num = int(value[1:])
            except (TypeError, ValueError, IndexError):
                raise ValueError(f'Invalid value: {value}')
            
            try:
                return self.parameters[num].value
            except (IndexError):
                raise ValueError(f'Invalid parameter number: {num}')
        
        raise ValueError('Invalid value: {value}')
        
    def get_value(self, indexed, index=0):
        """Return the value (of an index) of this parameter.
        
        Args:
            indexed: True, IFF this is an indexed parameter.
            index=0: The index of the value to be read 
                (ignored for unindexed parameters). 
        
        Returns:
            Value: An int or a float.
        
        Raises:
            OtherError:
                -If the parameter doesn't have the requested index 
                    (in indexed mode).
                -If an unindexed parameter is accessed in indexed mode
                    or vice versa. 
        """
        
        # This only checks *indexed*; all the other arguments are set 
        # to values that automatically pass.
        # The access code for read access doesn't specify the size of 
        # the parameter.
        self._check_access_mode(write_access=False, bits=self.bits, 
                                indexed=indexed)
        
        if indexed:
            # Parameter indices don't always begin at 0,
            # but list indices do.
            list_index = index - self.indices[0]
            try:
                if list_index < 0:
                    raise IndexError()
                return self.value[list_index]
            except IndexError:
                raise OtherError('Index error')
        else:
            return self.value
        
    def set_value(self, new_value, bits, indexed, index=0):
        """Set the value (of an index) of this parameter.
        
        Args:
            indexed: True IFF this is an indexed parameter.
            new_value: The value to be set.
            bits: Size of the parameter in bits.
            index=0: The index of the value to be read 
                (ignored for unindexed parameters).
        
        Raises:
            CannotChangeError: If the parameter isn't writable.
            MinMaxError: If *new_value* is out of range.
            OtherError:
                -If the parameter doesn't have the requested index 
                    (in indexed mode).
                -If *bits* doesn't match the parameter size.
                -If an unindexed parameter is accessed in indexed mode
                    or vice versa.
        """
        
        self._check_access_mode(write_access=True, bits=bits, indexed=indexed, 
                                value=new_value)
     
        if indexed:
            # Parameter indices don't always begin at 0,
            # but list indices do.
            list_index = index - self.indices[0]            
            try:
                if list_index < 0:
                    raise IndexError()
                self.value[list_index] = new_value
            except IndexError:
                raise OtherError('Index error')
        else:
            self.value = new_value
        
    def _check_access_mode(self, write_access, bits, indexed, value=0):
        """Raise an error if the parameter is accessed with a wrong 
        mode.
        
        Args:
           write_access: A boolean. True if a value is being written to
               the parameter; false if the value is only read.
           bits: Size of the parameter in bits.
           indexed: True, IFF this is an indexed parameter.
           value=0: The value that is being written; ignored, 
               if writeAccess is False.
                    
        Raises:
            CannotChangeError: If the parameter isn't writable.
            MinMaxError: If *new_value* is out of range.
            OtherError:
                -If the parameter doesn't have the requested index 
                    (in indexed mode).
                -If *bits* doesn't match the parameter size.
                -If an unindexed parameter is accessed in indexed mode
                    or vice versa.
        """
        if write_access and not self.writable:
            raise CannotChangeError('Parameter is not writable')
        
        if write_access and not self.min_value <= value <= self.max_value:
            raise MinMaxError('Value out of range')
        
        if bits != self.bits:
            raise OtherError(f'Bits should be {self.size}, not {bits}')
        
        if indexed != self.indexed:
            raise OtherError('Accessing indexed parameter with unindexed mode '
                             'or vice versa')
            
            
class ParameterAbstractError(Exception):
    """A superclass for all parameter-related errors."""
    pass

class ParameterNumberError(ParameterAbstractError):
    """Raised when a parameter number doesn't match any parameters."""
    CODE = ParameterError.WRONG_NUM.value
 
class CannotChangeError(ParameterAbstractError):
    """Raised when trying to write to a parameter without write 
    access.
    """
    CODE = ParameterError.CANNOT_CHANGE.value
 
class MinMaxError(ParameterAbstractError):
    """Raised when assigning a value too large oŕ too small to a  
    parameter.
    """
    CODE = ParameterError.MINMAX.value
 
class OtherError(ParameterAbstractError):
    """Raised when a parameter cannot be accessed for any other 
    reason.
    """
    CODE = ParameterError.OTHER.value