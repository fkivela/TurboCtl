"""This module handles parameter access in a
:class:~`turboctl.virtualpump.virtualpump.VirtualPump`.
"""

from turboctl.telegram.codes import (ParameterAccess, ParameterException,
                                     WrongNumError, AccessError,
                                     CannotChangeError, MinMaxError)
from turboctl.telegram.datatypes import Data
from turboctl.telegram.parser import Parameter


class ParameterComponent():
    """This class defines the part of a
    :class:~`turboctl.virtualpump.virtualpump.VirtualPump` that holds the
    values of pump parameters and handles access to them.
    """
    
    def __init__(self, parameters):
        """Initialize a new :class:`ParameterComponent`.
        
        Args:
            parameters: The parameter dictionary to be used.
                The keys should be parameter numbers and values 
                :class:`ExtendedParameter` objects.
        """
        self.parameters = parameters
        
    def handle_parameter(self, query, reply):
        """Access a parameter as commanded by *query*.
        
        The data to be returned to the user is written to *reply*.
        
        Args:
            query: A :class:`~turboctl.telegram.telegram.TelegramReader`
                object, which represents the telegram sent to the pump.
            
            reply: A :class:`~turboctl.telegram.telegram.TelegramBuilder`
                object, which is used to construct the telegram sent back
                from the pump.
        """
        
        if query.parameter_mode != 'none':
            try:
                reply.set_parameter_value(self._access_parameter(query))
                reply.set_parameter_mode('response')
            except ParameterException as error:
                # TODO: Find out how CannotChangeError is used?
                # Should it return 'error' with an error code, or 'no write'.        
                reply.set_parameter_mode('error')
                reply.set_error_code(error.MEMBER)
            
        return reply

    def _access_parameter(self, query):
        """Access a parameter as commanded by *query* and return the return
        value.
        
        Args:
            query: A TelegramReader object.
                
            Raises:
                A subclass of ParameterException: If the parameter cannot be
                    accessed due to a valid readon (i.e. one that can happen
                    to the real pump).
                
                ValueError: If query.parameter_mode is not 'read' or 'write'.
        """
        # Check that the parameter number is valid, and find that parameter.         
        try:
            parameter = self.parameters[query.parameter_number]
        except KeyError:
            raise WrongNumError(
                f'invalid parameter number: {query.parameter_number}')
                        
        # Check that the access mode matches the size of the parameter.
        bits = ParameterAccess(query.telegram.parameter_code).bits
        if bits != parameter.bits:
            raise AccessError(f'bits should be {parameter.bits}, not {bits}')
        
        # Check that the access mode matches the indices of the parameter.
        indexed = ParameterAccess(query.telegram.parameter_code).indexed
        if indexed != parameter.indexed:
            raise AccessError('wrong value of *indexed*')
        
        mode = query.parameter_mode
        if mode == 'write':
            # Check that the parameter is writable.
            if not parameter.writable:
                raise CannotChangeError('parameter is not writable')
            # Check that the new value is within range.
            value = query.parameter_value
            if not parameter.min_value <= value <= parameter.max_value:
                raise MinMaxError('value out of range')

            # Write the new value.
            parameter.values[query.parameter_index] = query.parameter_value

        if mode not in ['read', 'write']:
            raise ValueError(f'invalid parameter_mode: {mode}')

        return parameter.value
        

class ExtendedParameter(Parameter):
    """This class represents a parameter that has a value which can 
    change, while the regular :class:`~turboctl.telegram.parser.Parameter`
    class only describes the immutable attributes of a parameter. 
    
    Attributes:
        
        value (:class:`turboctl.telegram.datatypes.Data`):
            The current values of the indices of the parameter as a list.
            This will be a list even for unindexed parameters, but in that
            case the length of the list will be 1. The values of the list
            will be instances of :attr:`datatype`.
            
        parameters: A :class:`dict` of all extended parameters 
            (with numbers as keys and objects as values).
            This is needed, because the :attr:`min_value` and
            :attr:`max_value` of some parameters depend on the values of
            other parameters. 
    
    """
    
    def __init__(self, parameter, extended_parameters):
        """Initialize a new :class:`ExtendedParameter`.
                
        Args:
            parameter (:class:`~turboctl.telegram.parser.Parameter`):
                This object copies the attributes of *parameter*.
                
                If :attr:`parameter.min_value
                <turboctl.telegram.parser.Parameter.min_value>`,
                :attr:`parameter.max_value
                <turboctl.telegram.parser.Parameter.max_value>` or
                If :attr:`parameter.default
                <turboctl.telegram.parser.Parameter.default>`
                are references to the values of other parameters
                (e.g. ``'P18'``), they will be replaced with numberical values
                copied from the referenced parameters.
                
                If a referenced parameter cannot be found in
                *extended_parameters*, a :class:`KeyError` will be raised. 
                
            extended_parameters:
                The object to be assigned to :attr:`parameters. 
        """
        # Copy attributes from *parameter*.
        self.__dict__.update(parameter.__dict__)

        self.parameters = extended_parameters
        self.min_value = self._get_true_value(parameter.min_value)
        self.max_value = self._get_true_value(parameter.max_value)        
        self.default = self._get_true_value(parameter.default)
        self.value = self.default_value
        
    def _get_true_value(self, value):
        """Returns the numerical value  of *value*.
        
        If *value* is a reference to the value of another 
        parameter (e.g. 'P18'), this attribute will return the 
        numerical value of that attribute.
        
        The return value will match the format of :attr:`value`.
        
        Args:
            value: An instance of a :class:`turboctl.telegram.datatypes.Data`
                subclass or a string with the format ``'P<number>'``.
        
        Raises:
            ValueError: If *value* is invalid.
        """
        if isinstance(value, Data):
            return value
        
        if isinstance(value, str) and value[0] == 'P':
            # Extract the number.
            num = int(value[1:])
            return self.parameters[num].value
        
        raise ValueError(f'invalid *value*: {value}')
        
    def __str__(self):
        """Returns 'ExtendedParameter(attribute1=value1, ...)'.
        
        The string includes the values of read-only properties.
        """
        fields = [
            'number', 'name', 'indices', 'indexed', 'min', 'max', 'default', 
            'min_value', 'max_value', 'default_value', 'value', 'unit', 
            'writable', 'datatype', 'size', 'description']
        
        strings = [f'{f}={repr(getattr(self, f))}' for f in fields]
        string = ', '.join(strings)
        return f'{type(self).__name__}({string})'


class ExtendedParameters(dict):
    """A :class:`dict` of :class:`ExtendedParameter` objects."""

    def __init__(self, parameters):
        """Initialize a new :class:`ExtendedParameters` object from
        *parameters* (a :class:`dict` of :class:`Parameter` objects).
        
        The data from each :class:`Parameter` object is copied into an
        :class:`ExtendedParameter` object. The objects are initialized in such
        an order that no errors will be raised because of references to
        uninitialized parameters.
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
