"""This module handles parameter access in a
:class:`~turboctl.virtualpump.virtualpump.VirtualPump`.
"""

from turboctl.telegram.codes import (ParameterAccess, ParameterException,
                                     AccessError, CannotChangeError,
                                     MinMaxError, ParameterIndexError,
                                     WrongNumError)
from turboctl.telegram.datatypes import Data
from turboctl.telegram.parser import Parameter


class ParameterComponent():
    """This class defines the part of a
    :class:`~turboctl.virtualpump.virtualpump.VirtualPump` that holds the
    values of pump parameters and handles access to them.
    
    Attributes:
        parameters: A :class:`dict` that represents pump parameters.
            The keys should be parameter numbers (:class:`int`) and values
            corresponding :class:`ExtendedParameter` objects.
    """
    
    def __init__(self, parameters):
        """Initialize a new :class:`ParameterComponent`.
        
        Args:
            parameters: The object to be assigned to :attr:`parameters`.
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
                reply.set_parameter_mode('response')
                reply.set_parameter_value(self._access_parameter(query))
            except ParameterException as error:
                # TODO: Find out how CannotChangeError is used?
                # Should it return 'error' with an error code, or 'no write'.        
                reply.set_parameter_mode('error')
                reply.set_parameter_value(error.member.value)
            
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
        # The parameter error messages here are written to descriptive to aid
        # debugging, even though they should never propagate beyond this
        # method. 
            
        # Extract the parameter access code as a string.            
        parameter_code = query.telegram.parameter_code.value
        # Find the corresponding ParameterAccess member.
        access_member = ParameterAccess(parameter_code)
        
        # Check that the access mode matches the size of the parameter.
        bits = access_member.bits
        # The ellipsis means this mode doesn't care about parameter size.
        if bits not in [parameter.bits, ...]:
            raise AccessError(f'bits should be {parameter.bits}, not {bits}')
        
        # Check that the access mode matches the indices of the parameter.
        indexed = access_member.indexed
        # The ellipsis is again a "wild card" value.
        if indexed not in [bool(parameter.indices), ...]:
            raise AccessError('wrong value of *indexed*')
        
        # Some parameters start their indices from some other number than 0.
        # "parameter.indices[0]" is only evaluated here if parameter.indices
        # is not range(0).
        offset = parameter.indices[0] if parameter.indices else 0
        # Example: A parameter has the indices [1, 2, 3] and the values
        # [4, 5, 6]. query.parameter_index is 3.
        # offset is then 1 and index is 3 - 1 = 2, so the value that is
        # returned is parameter.value[2] = 6.
        index = query.parameter_index - offset
                
        # Make sure the index is within range. A try-catch-block could be used
        # instead, but that wouldn't be ideal, since parameter.value is
        # accessed at two different points in the code.
        # This also catches negative indices, but a try-catch-block wouldn't,
        # since negative indices are perfectly valid in Python. 
        if not 0 <= index < len(parameter.value):
            raise ParameterIndexError(
                f'parameter index ({query.parameter_index}) out of range '
                f'({parameter.indices})')
        
        # Write the new value, if the mode is 'write'.
        mode = query.parameter_mode
        if mode == 'write':
            # Check that the parameter is writable.
            if not parameter.writable:
                raise CannotChangeError(
                    f'parameter {query.parameter_number} is not writable')
            
            # Check that the new value is within range.
            
            min_value = parameter.min_value.value
            max_value = parameter.max_value.value
            value = query.parameter_value
            
            if not (min_value <= value <= max_value):
                raise MinMaxError(f'value ({value}) out of range'
                                  f'([{min_value}, {max_value}])')

            # Write the new value as a Data subclass instance of the
            # appropriate type and size.
            parameter.value[index] = (
                parameter.datatype(query.parameter_value, parameter.bits))

        if mode not in ['read', 'write']:
            raise ValueError(f'invalid parameter_mode: {mode}')

        return parameter.value[index].value


class ExtendedParameter():
    """This class represents a parameter that has a value which can 
    change, while the regular :class:`~turboctl.telegram.parser.Parameter`
    class only describes the immutable attributes of a parameter.
    
    Attributes:
        
        number:
            See :attr:`Parameter.number
            <turboctl.telegram.parser.Parameter.number>`.
        
        indices:
            See :attr:`Parameter.indices
            <turboctl.telegram.parser.Parameter.indices>`.
        
        default:
            See :attr:`Parameter.default
            <turboctl.telegram.parser.Parameter.number>`.

        writable:
            See :attr:`Parameter.writable
            <turboctl.telegram.parser.Parameter.number>`.
        
        datatype:
            See :attr:`Parameter.datatype
            <turboctl.telegram.parser.Parameter.number>`.
        
        bits:
            See :attr:`Parameter.bits
            <turboctl.telegram.parser.Parameter.number>`.
            
        value (:class:`turboctl.telegram.datatypes.Data`):
            The current values of the indices of the parameter as a list.
            This will be a list even for unindexed parameters, but in that
            case the length of the list will be 1. The values of the list
            will be instances of
            :attr:`~turboctl.telegram.parser.Parameter.datatype`.
            
        parameters: A :class:`dict` of all instances of this class, 
            with parameter numbers as keys and objects as values.
            This is needed, because the :attr:`min_value` and
            :attr:`max_value` attributes of some parameters depend on the
            values of other parameters.
    """
    
    def __init__(self, parameter, extended_parameters):
        """Initialize a new :class:`ExtendedParameter`.
                
        Args:
            parameter (:class:`~turboctl.telegram.parser.Parameter`):
                The non-extended version of this parameter. Most attributes
                of this object are copied from *parameter*.

            extended_parameters:
                The object to be assigned to :attr:`parameters`. 
        """
        # Copy attributes from *parameter*.
        copied_attributes = [
            'number', 'indices', 'default', 'writable', 'datatype', 'bits'
        ]
        for name in copied_attributes:
            value = getattr(parameter, name)
            setattr(self, name, value)

        self.parameters = extended_parameters
        
        # Save the min and max values of the original parameter.
        # These can be either Data subclass instances or references to the
        # values of other parameters (e.g. 'P18').
        self._raw_min_value = parameter.min_value
        self._raw_max_value = parameter.max_value
        
        # Set self.value based on self.default.
        if type(parameter.default) == list:
            # parameter.default is a list -> indices have different values.
            self.value = parameter.default
        else:
            # parameter.default is a single value -> all indices have the same
            # value.
            if parameter.indices:
                # Indexed parameter.
                self.value = [parameter.default for i in parameter.indices]
            else:
                # Unindexed parameter: parameter.indices = range(0).
                self.value = [parameter.default]
                
    @property
    def min_value(self):
        """Return the minimum value of the parameter.
        
        This is always a :class:`~turboctl.telegram.datatypes.Data` subclass
        instance. If the :attr:`~turboctl.telegram.parser.Paramete.min_value`
        of the original non-extended parameter is a reference to the value of
        another parameter, this property returns that value.
        
        Raises:
            KeyError: If a referenced parameter cannot be found in
                :attr:`parameters`.
        """
        return self._get_true_value(self._raw_min_value)
        
    @property
    def max_value(self):
        """Return the maximum value of the parameter.
        
        This is always a :class:`~turboctl.telegram.datatypes.Data` subclass
        instance. If the :attr:`~turboctl.telegram.parser.Parameter.max_value`
        of the original non-extended parameter is a reference to the value of
        another parameter, this property returns that value.
        
        Raises:
            KeyError: If a referenced parameter cannot be found in
                :attr:`parameters`.
        """
        return self._get_true_value(self._raw_max_value)
        
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
            # Even the values of unindexed parameters are lists.
            # The index is always 0, since there should be no references to
            # unindexed parameters.
            return self.parameters[num].value[0]
        
        raise ValueError(f'invalid *value*: {value}')
                
    def __str__(self):
        """Returns a :class:`str` with the following format:
            
        ::
            
            ExtendedParameter(
                number=<number>,   
                indices=<indices>,
                min_value=<min_value>,
                max_value=<max_value>,
                default=<default>,
                writable=<writable>,
                datatype=<datatype>,
                bits=<bits>,
                value=<value>
            )
            
        If the :attr:`~turboctl.telegram.parser.Parameter.min_value` or 
        :attr:`~turboctl.telegram.parser.Parameter.max_value` attributes of the
        original parameter are references, both the reference and the actual
        value are displayed. The following is an example of the format:
        
        ::
            
            ...
            min_value='P18' (Uint(1, 16)),
            ...
        """
        
        if isinstance(self._raw_min_value, str):
            min_str = repr(self._raw_min_value) + f' ({self.min_value})'
        else:
            min_str = str(self.min_value)
            
        if isinstance(self._raw_max_value, str):
            max_str = repr(self._raw_max_value) + f' ({self.max_value})'
        else:
            max_str = str(self.max_value)
        
        return f"""
ExtendedParameter(
    number={self.number},   
    indices={self.indices},
    min_value={min_str},
    max_value={max_str},
    default={self.default},
    writable={self.writable},
    datatype={self.datatype.__name__},
    bits={self.bits},
    value={self.value}
)
"""[1:-1]


class ExtendedParameters(dict):
    """A :class:`dict` of :class:`ExtendedParameter` objects.
    
    This class can be used to avoid the need to manually initialize a
    :class:`dict` of :class:`ExtendedParameter` objects. After initialization
    instances of this class behave like regular :class:`dict` objects.  
    """

    def __init__(self, parameters):
        """Initialize a new :class:`ExtendedParameters` object from
        *parameters* (a :class:`dict` of
        :class:`~turboctl.telegram.parser.Parameter` objects).
        
        The data from each :class:`~turboctl.telegram.parser.Parameter` object
        is copied into an :class:`ExtendedParameter` object. The objects are
        initialized in such an order that no errors will be raised because of
        references to uninitialized parameters.
        """
        super().__init__()        

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
                if num not in self.keys():
                    try:
                        self[num] = ExtendedParameter(p, self)
                    # A KeyError is raised if a parameter's dependency 
                    # has not been initialized.
                    except KeyError:
                        pass
