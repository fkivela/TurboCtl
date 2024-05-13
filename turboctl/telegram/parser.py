"""This module contains a parser that reads data about pump parameters, 
errors and warnings from text files.

Attributes:
    PARAMETERS:
        The pump has multiple parameters which affect its behaviour.
        This attribute holds a :class:`dict` of these parameters, represented 
        as :class:`Parameter` objects, with the numbers of the parameters as 
        the keys.
        
    ERRORS:
        A :class:`dict` of different error conditions which can affect the 
        pump, represented as :class:`ErrorOrWarning` objects, 
        with error numbers as the keys. 
        
    WARNINGS:
        Like :attr:`ERRORS`, but for warnings instead of errors.
"""

import re
import ast
import os.path
from dataclasses import dataclass
from collections import OrderedDict
from typing import Union, List

from turboctl.telegram.datatypes import Data, Uint, Sint, Float


@dataclass
class Parameter:
    """A class for representing pump parameters.
    
    This is a :obj:`~dataclasses.dataclass`, so the ``__init__``, ``__str__``
    and ``__repr__`` methods are generated automatically.
    """
    
    number: int
    """The number of the parameter."""
    
    name: str
    """The name of the parameter."""
    
    indices: range
    """A :class:`range` object describing the indices of the parameter; e.g.
    ``range(5)`` would mean the parameter has indices numbered 0 to 4.
    This is ``range(0)`` for unindexed parameters.
    """

    min_value: Union[Data, str]
    """The minimum value of the parameter.
    
    The minumum value of some parameters depends on the current value of
    another parameter. In that case, :attr:`min_value` is set to
    ``'P<number>'``; e.g. 'P18' means the value of parameter 18.
    """
    
    max_value: Union[Data, str]
    """The maximum value of the parameter.
    
    The maximum value of some parameters depends on the current value of
    another parameter. In that case, :attr:`max_value` is set to
    ``'P<number>'``; e.g. 'P18' means the value of parameter 18.
    """
    
    default: Union[Data, List[Data]]
    """The default value of the parameter.
    
    If the parameter is indexed and different indices have different default
    values, :attr:`default` will be a :class:`list` of default values
    corresponding to the different indices.
    """

    unit: str
    """The unit of the parameter; e.g. ``'°C'`` for degrees Celsius."""
    
    writable: bool
    """Signifies whether the value of the parameter can be changed."""
    
    datatype: type
    """The type of the value of the parameter; a
    :class:`~turboctl.telegram.datatypes.Data` subclass
    (but not :class:`~turboctl.telegram.datatypes.Bin`).
    """
    
    bits: int
    """The size of the parameter in bits; ``16`` or ``32``."""
    
    description: str
    """A string describing the parameter."""
    
    @property
    def fields(self):
        """Return an :class:`~collections.OrderedDict` with the attribute
        names of this objects as keys and their values as values.
        """
        fieldnames = ['number', 'name', 'indices', 'min_value', 'max_value', 
                      'default', 'unit', 'writable', 'datatype', 'bits', 
                      'description']
        return OrderedDict((name, getattr(self, name)) for name in fieldnames)
    
    
@dataclass
class ErrorOrWarning:
    """A class for representing pump errors and warnings."""
    
    number: int
    """The number of the error or warning."""
    
    name: str
    """The name of the error or warning."""
    
    possible_cause: str
    """A string describing the possible cause(s) of the error or warning."""
    
    remedy: str
    """A string describing possible remedies for the error or warning."""
    
    @property
    def fields(self):
        """Return an :class:`~collections.OrderedDict` with the attribute
        names of this object as keys and their values as values.
        """
        fieldnames = ['number', 'name', 'possible_cause', 'remedy']
        return OrderedDict((name, getattr(self, name)) for name in fieldnames)


# The special character used for comments:
_COMMENT_CHAR = '#'


def main():
    """Define :attr:`PARAMETERS`, :attr:`ERRORS` and :attr:`WARNINGS`.
    
    This function is automatically executed when this module is 
    imported or run as a script.
    """
    global PARAMETERS, ERRORS, WARNINGS
    PARAMETERS = load_parameters()
    ERRORS = load_errors()
    WARNINGS = load_warnings()

def _fullpath(filename):
    """Return of the full path of *filename*. 
    *filename* should be a file in the same directory as this module.
    """
    dirpath = os.path.dirname(__file__)
    return os.path.join(dirpath, filename)


def load_parameters(path=None):
    """Parse the parameter file and return a dictionary of 
    parameters.
    
    This function is automatically called by :func:`main`, but it can also be
    called separately in order to create another set of parameters for testing
    purposes.  
    
    Args:
        path: A text file containing parameter/error/warning data.
            If *path* isn't specified, the file will be ``'parameters.txt'``,
            located in the same directory as this module.
            The syntax used to define the parameters is explained in
            ``parameters.txt``.
            
    Returns:
        A :class:`dict` with numbers as keys and :class:`Parameter` objects as
        values.
            
    Raises:
        FileNotFoundError: If *filename* cannot be found.
        RuntimeError: If a line in *filename* cannot be parsed.
    """
    default = 'parameters.txt'
    filename = path if path else _fullpath(default)
    return _load_data(filename, 'parameter')
    

def load_errors(path=None):
    """Parse the error file and return a dictionary of 
    errors.
    
    This works like :func:`load_parameters`, but the default file is
    ``'errors.txt'``, and the returned :class:`dict` contains
    :class:`ErrorOrWarning` objects.
    """
    default = 'errors.txt'
    filename = path if path else _fullpath(default)
    return _load_data(filename, 'error')


def load_warnings(path=None):
    """Parse the warning file and return a dictionary of 
    warnings.
    
    This works like :func:`load_parameters`, but the default file is
    ``'warnings.txt'``, and the returned :class:`dict` contains
    :class:`ErrorOrWarning` objects.
    """
    default = 'warnings.txt'
    filename = path if path else _fullpath(default)
    return _load_data(filename, 'warning')


def _load_data(filename, type_):
    """Return a dictionary of parameters, errors or warnings.
    
    Args:
        filename: A text file containing parameter/error/warning data.
            The syntax used in the text file is explained in 
            ``parameters.txt``.
        type_: ``'parameters'``, ``'errors'`` or ``'warnings'``.
            
    Returns:
        A dictionary with numbers as keys and :class:`Parameter` 
        or :class:`ErrorOrWarning` objects as values.
            
    Raises:
        FileNotFoundError: If *filename* cannot be found.
        RuntimeError: If a line in *filename* cannot be parsed.
    """
    
    with open(filename, 'r') as file:        
        contents = file.read()
        
    lines = contents.split('\n')
    
    object_list = []
    for i, line in enumerate(lines):
        try:
            parsed = _parse(line, type_)
        except ValueError as e:
            raise RuntimeError(
                f'Line {i+1} of {filename} could not be parsed: ' + str(e))
        
        # *parsed* is None for empty lines; skip those.
        if parsed:
            object_list.append(parsed)
    
    return {p.number: p for p in object_list}


def _parse(line, type_):
    """Parse data from *line* and form a Parameter or ErrorOrWarning object.
    
    Args:
        line: A string with no line breaks.
        type_: 'parameter', 'error' or 'warning'.
    
    Raises:
        ValueError: If *line* cannot be parsed.
    """
    # This method is private since it's only used internally by this module,
    # but it cannot be removed/renamed without changing the tests, since a
    # lot of them use this.
    
    line = _remove_comments(line)
    
    if _is_empty(line):
        return None
    
    number_of_fields = {'parameter': 9, 'error': 4, 'warning': 4}
    fields = _separate_fields(line)
    
    if len(fields) != number_of_fields[type_]:
        raise ValueError(
            f'{len(fields)} fields instead of {number_of_fields[type_]}')
    
    fields = [_add_linebreaks(_remove_quotes(field)) for field in fields]
    
    try:
        return _form_object(fields, type_)
    except ValueError as e:
        raise ValueError('invalid values: ' + str(e)) from e


def _separate_fields(line):
    """Separate the data fields contained in *line*.
    
    Args:
        line: A string with no line breaks.
        
    Returns:
        A list containing the data fields.
        E.g. _separate_fields('1 2 "3 4"') -> ['1', '2', "3 4"].
    """
    
    start = '(?: |^)' 
    # A regex that begins a data field.
    # A space or start of string.
    
    # ?: makes groups non-capturing. Example: 
    # re.findall('(?:abc)(?:def)', 'abcdef') -> ['abcdef'], but
    # re.findall('(abc)(def)', 'abcdef') -> [('abc', 'def')]
    
    end = '(?=(?:$| ))' 
    # A regex that ends a data field.
    # A space or end of string
    
    # ?= makes a regexp non-consuming; i.e. a space can here match both 
    # the end of one word and the start of another, since the end match 
    # doesn't consume it.
    
    word = '(?:[^ "]+)'
    # A regex representing a string without any spaces.
    # Any character except space or quote, 1 or more times.
    
    many_words = '(?:"[^"]*")' 
    # A regex representing a string consisting of multiple words 
    # separated by spaces; all enclosed in double quotes.
    # Any character except quote, 1 or more times, between quotes.
    
    one_or_many_words = f'({word}|{many_words})'
    field = start + one_or_many_words + end
    return re.findall(field, line)


def _form_object(fields, type_):
    """Return a Parameter or ErrorOrWarning object.
    
    Args:
        fields: A list containing the attribute values of the 
            object as strings.
        type_: 'parameter', 'error' or 'warning'.
        
    Raises:
        ValueError: If type_ is not any of the above.
    """
    
    if type_ == 'parameter':
         return _form_parameter(fields)
    if type_ in ('error', 'warning'):
         return _form_error_or_warning(fields)
     
    raise ValueError(
        f"*type_* should be 'parameter', 'error' or 'warning', not {type_}")


def _form_parameter(fields):
    """Construct a Parameter object from given data fields.
        
    Raises:
        ValueError: If any of the data fields cannot be parsed into 
            values of the correct type.
    """    
    
    number, indices = _parse_number(  fields[0])
    name            =                 fields[1]
    unit            =                 fields[5]
    writable        = _parse_writable(fields[6])
    datatype, bits  = _parse_format(  fields[7])
    description     =                 fields[8]
        
    min_value       = _parse_minmax(  fields[2], datatype, bits)
    max_value       = _parse_minmax(  fields[3], datatype, bits)
    default         = _parse_default( fields[4], datatype, bits)
    
    return Parameter(number, name, indices, min_value, max_value, default, 
                     unit, writable, datatype, bits, description)
    

def _form_error_or_warning(fields):
    """Construct an ErrorOrWarning object from given data fields.
        
    Raises:
        ValueError: If any of the data fields cannot be parsed into 
            values of the correct type.
    """  
    number, _      = _parse_number(fields[0])
    name           =               fields[1]
    possible_cause =               fields[2]
    remedy         =               fields[3]
    
    return ErrorOrWarning(number, name, possible_cause, remedy)
        

def _parse_number(string):
    """Parse the data field containg the parameter/error/warning 
    number and possible indices.
    
    Returns:
        A tuple of the number (an int) and the indices (a range object;
        range(0) for unindexed parameters/errors/warnings).
    """
    any_number = '([0-9]+)'
    no_capture = '?:'
    one_or_zero_times = '?'
    
    index_numbers = f'\\[{any_number}:{any_number}\\]'
    # [<number>:<number>]
    maybe_index_numbers = f'({no_capture}{index_numbers}){one_or_zero_times}'
    # [<number>:<number>] or nothing
    
    numbers = f'^{any_number}{maybe_index_numbers}$'
    # <number>[<number>:<number>] or <number>

    try:
        parts = re.findall(numbers, string)[0]
        # If re.findall is successful, it will return 
        # [('<num>', '<num>', '<num>')] or [('<num>', '', '')].
        # If it's unsuccessful, it will return [].
        
    except IndexError:
        raise ValueError(f'invalid number or indices: {string}')
        
    number = int(parts[0])
    
    if parts[1] == parts[2] == '':
        indices = range(0)
    else:
        try:
            indices = range(int(parts[1]), int(parts[2]) + 1)
            # parts[2] is the last index, so 1 has to be added to it 
            # for it to be included in the range.
        except ValueError:
            raise ValueError(f'invalid indices: {string}')

    return number, indices    


def _parse_minmax(string, datatype, bits):
    """Parse a data field containg the minimum or maximum parameter
    value.
    
    Args:
        string: The field to be parsed.
        datatype: The datatype (a Data subclass) of the parameter.
        bits: The size of the parameter in bits.
    
    Returns:
        -An object of type *datatype*, if the value is numeric.
        -A string in the format P<number>, if *string* matches that
            format.    
    """
    # Try to parse the string as an int or a float first.
    try:
        return _parse_value(string, datatype, bits)
    except ValueError:
        pass
    
    # If that doesn't work, try to interpret the string as a reference.     
    any_number = '([0-9]+)'
    P_number = f'^P{any_number}$'
    
    if re.match(P_number, string):
        return string
    else:
        raise ValueError(f'invalid min/max value: {string}')    
        
        
def _parse_default(string, datatype, bits):
    """Parse the data field containg the default parameter value.
    
    Args:
        string: The field to be parsed.
        datatype: The datatype (a Data subclass) of the parameter.
        bits: The size of the parameter in bits.
    
    Returns:
        An object of type *datatype*. If different parameter indices have
        different default values, a list of such objects is returned instead.
    """
    # Try to parse the string as an int or a float first.
    try:
        return _parse_value(string, datatype, bits)
    except ValueError:
        pass
    
    # If that doesn't work, try to interpret the string as a list of
    # ints/floats.     
    try:
        value_list = ast.literal_eval(string) # Unlike eval(), this is safe.
        # By converting i to a string first we can use _parse_value to
        # e.g. parse '0' into a Float, even though Float(0) raises an error. 
        return [_parse_value(str(i), datatype, bits) for i in value_list]
    except (SyntaxError, ValueError):
        raise ValueError(f'invalid default value: {string}')
    
    
def _parse_value(string, datatype, bits):
    """Parse *string* to an int or a float and the convert that into a *bits*
    bit instance of *datatype*.
    
    Raises:
        ValueError: If *string* isn't a valid int or a float.'
    """
    # This is needed, because Uint, Sint, and Float don't accept str arguments. 
    builtin_type = float if datatype == Float else int
    value = builtin_type(string)
    return datatype(value, bits)


def _parse_format(string):
    """Parse the data field containg the parameter number format.
    
    Returns: A tuple containing the type (a subclass of Data) 
    and bits (16 or 32) of the parameter.
    """
    numbers = '([0-9]+)'
    letters = '([a-z]+)'
    letters_and_numbers = f'^{letters}{numbers}$'
    
    try:
        parts = re.findall(letters_and_numbers, string)[0]
        # If re.findall is successful, it will return 
        # [('<letters>', '<number>')].
        # If it's unsuccessful, it will return [].
        
    except IndexError:
        raise ValueError(f'invalid format: {string}')
    
    type_part = parts[0]
    bits_part = parts[1]
    
    if type_part == 'u':
        type_ = Uint
    elif type_part == 's':
        type_ = Sint
    elif type_part == 'real':
        type_ = Float
    else:
        raise ValueError(f'invalid type: {string}')
    
    try:
        bits = int(bits_part)
        
    except ValueError:
        raise ValueError(f'invalid bits: {string}')
        
    return type_, bits


def _parse_writable(string):
    """Parse the data field indicating whether the parameter can be 
    written to an return a boolean (True for writable, False otherwise).
    """    
    if string == 'r/w':
        return True
    elif string in ('r', ''):
        return False
    else:
        raise ValueError(f'invalid r/w string: {string}')


def _remove_comments(line):
    """Removes everything after a comment symbol from *line*."""
    return line.split(_COMMENT_CHAR)[0]
            
          
def _is_empty(line):
    """Returns True if *line* consists only of whitespace."""
    empty_regex = '^\\s*$' # \s = whitespace character
    return bool(re.match(empty_regex, line))
              
        
def _remove_quotes(string):
    """If *string* is enclosed in double quotes, this function removes 
    them.
    
    E.g. both 'Lorem ipsum' and '"Lorem ipsum"' return 'Lorem ipsum'.
    """
    
    if string[0] == string[-1] == '"':
        return string[1:-1]
    else:
        return string


def _add_linebreaks(string):
    """Replaces occurrences of r'\n' in *string* with '\n'.
    
    Line breaks can be manually inserted inside data fields in a 
    text file by typing a backslash and a 'n'. These are two 
    separate characters, and need to be replaced by a single 
    line break character '\n'.
    """    
    
    # The Python interpreter and the re module seem to apply special
    # characters separately, so we need to escape the backslash 
    # character twice. 
    # r'\\' equals two backslashes (r denotes a raw string, where no 
    # special characters are applied) and the re module interprets 
    # this as a single backslash. 
    # '\\\\' also works, since it is equal to r'\\'.
    
    # Here r'\\n' is interpreted by the re module as a single 
    # backslash and the letter n.
    return re.sub(r'\\n', '\n', string)
           
 
main()
