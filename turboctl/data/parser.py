"""This module contains a parser that reads data about pump parameters, 
error and warnings from text files.
"""

import re
import ast
import os.path
from dataclasses import dataclass
from collections import OrderedDict
from typing import Union, List

#from turboctl.telegram import Types
from .types import Types

@dataclass
class Parameter:
    """A class for representing pump parameters."""
    
    # Type hints have to be used with dataclasses.
    number: int
    name: str
    indices: range
        # indices=range(0) for unindexed parameters.
    min: Union[int, float, str]
    max: Union[int, float, str]
        # min and max can have a value of 'P<number>' (e.g. 'P18'), 
        # if their value equals the value of another parameter.
    default: Union[int, float, List[int], List[float]]
        # default is a list, if the parameter is indexed and the 
        # indices have different default values.
    unit: str
    writable: bool
    type: Types
    size: int
    description: str
    
    @property
    def fields(self):
        """Return an OrderedDict with parameter attribute names as 
        keys and their values as values.
        """
        fieldnames = ['number', 'name', 'indices', 'min', 'max', 'default', 
                      'unit', 'writable', 'type', 'size', 'description']
        
        return OrderedDict((name, getattr(self, name)) for name in fieldnames)
    
@dataclass
class ErrorOrWarning:
    """Class for representing pump errors ans warnings."""
    
    number: int
    name: str
    possible_cause: str
    remedy: str
    
    @property
    def fields(self):
        """Return an OrderedDict with error/warning attribute names as 
        keys and their values as values.
        """
        fieldnames = ['number', 'name', 'possible_cause', 'remedy']
        return OrderedDict((name, getattr(self, name)) for name in fieldnames)

# The special character used for comments:
_COMMENT_CHAR = '#'

def main():
    """Define the PARAMETERS, ERRORS and WARNINGS dictionaries.
    
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
    """
    default = 'parameters.txt'
    filename = path if path else _fullpath(default)
    return load_data(filename, 'parameter')
    
def load_errors(path=None):
    """Parse the error file and return a dictionary of 
    errors.
    """
    default = 'errors.txt'
    filename = path if path else _fullpath(default)
    return load_data(filename, 'error')

def load_warnings(path=None):
    """Parse the warning file and return a dictionary of 
    errors.
    """
    default = 'warnings.txt'
    filename = path if path else _fullpath(default)
    return load_data(filename, 'warning')

def load_data(filename, type_):
    """Return a dictionary of parameters, errors or warnings.
    
    Args:
        filename: A text file containing parameter/error/warning data.
            The syntax used in the text file is explained in 
            parameters.txt.
        type_: 'parameters', 'errors' or 'warnings'.
            
    Returns:
        A dictionary with numbers (int) as keys and Parameter 
        or ErrorOrWarning objects as values.
            
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
            parsed = parse(line, type_)
        except ValueError as e:
            raise RuntimeError(
                f'Line {i+1} of {filename} could not be parsed: ' + str(e))
        
        # *parsed* is None for empty lines; skip those.
        if parsed:
            object_list.append(parsed)
    
    return {p.number: p for p in object_list}

def parse(line, type_):
    """Parse data from *line* and form a Parameter or 
    ErrorOrWarning object.
    
    Args:
        line: A string with no line breaks.
        type_: 'parameter', 'error' or 'warning'.
    
    Returns:
        A Parameter or ErrorOrWarning object.
    
    Raises:
        ValueError: If *line* cannot be parsed.
    """
    
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
        line: A string with no linebreaks.
        
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
    
    Args:
        fields: A list of strings.
        
    Returns:
        A Parameter object.
        
    Raises:
        ValueError: If any of the data fields cannot be parsed into 
            values of the correct type.
    """    
    
    number, indices = _parse_number(  fields[0])
    name            =                 fields[1]
    min_            = _parse_minmax(  fields[2])
    max_            = _parse_minmax(  fields[3])
    default         = _parse_default( fields[4])
    unit            =                 fields[5]
    writable        = _parse_writable(fields[6])
    type_, size     = _parse_format(  fields[7])
    description     =                 fields[8]
    
    return Parameter(number, name, indices, min_, max_, default, unit, 
                     writable, type_, size, description)
    
def _form_error_or_warning(fields):
    """Construct an ErrorOrWarning object from given data fields.
    
    Args:
        fields: A list of strings.
        
    Returns:
        An ErrorOrWarning object.
        
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
    
    Args:
        string: The data field to be parsed.
    
    Returns:
        A tuple of:
            -number: An int.
            -indices: A range object; range(0) for unindexed 
                parameters and errors or warnings.
    
    """
    
    any_number = '([0-9]+)'
    no_capture = '?:'
    one_or_zero_times = '?'
    
    index_numbers = f'\[{any_number}:{any_number}\]'
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

def _parse_minmax(string):
    """Parse a data field containg the minimum or maximum parameter
        value.
    
    Args:
        string: The data field to be parsed.
    
    Returns:
        -An int, if the value is an integer.
        -A float, if the value is a real number.
        -A string in the format P<number>, if *string* matches that
            format.    
    """
    
    try:
        return int(string)
    except ValueError:
        pass
    
    try:
        return float(string)
    except ValueError:
        pass
    
    any_number = '([0-9]+)'
    P_number = f'^P{any_number}$'
    
    if re.match(P_number, string):
        return string
    else:
        raise ValueError(f'invalid min/max value: {string}')    
        
def _parse_default(string):
    """Parse the data field containg the default parameter value.
    
    Args:
        string: The data field to be parsed.
    
    Returns:
        An int or float, or a list of ints or floats, if parameter 
        indices have different default values.
    """
    
    try:
        value = ast.literal_eval(string) # Unlike eval(), this is safe.
    except (SyntaxError, ValueError):
        raise ValueError(f'invalid default value: {string}')

    if type(value) in (int, float):
        return value
    
    is_ints = all([isinstance(i, int) for i in value])
    is_floats = all([isinstance(i, float) for i in value])
    
    if isinstance(value, list) and (is_ints or is_floats):
        return value
    
    raise ValueError(f'invalid default value: {string}')

def _parse_format(string):
    """Parse the data field containg the parameter number format.
    
    Args:
        string: The data field to be parsed.
    
    Returns:
        A tuple of:
            -type_: An instance of the Types enum.
            -size: A int (16 or 32).
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
    size_part = parts[1]
    
    if type_part == 'u':
        type_ = Types.UINT
    elif type_part == 's':
        type_ = Types.SINT
    elif type_part == 'real':
        type_ = Types.FLOAT
    else:
        raise ValueError(f'invalid type: {string}')
    
    try:
        size = int(size_part)
        
    except ValueError:
        raise ValueError(f'invalid size: {string}')
        
    return type_, size

def _parse_writable(string):
    """Parse the data field indicating whether the parameter can be 
    written to.
    
    Args:
        string: The data field to be parsed.
    
    Returns:
        A boolean (True if the parameter is writable; False if not).
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
    """Returns True, if *line* consists only of whitespace."""
    empty_regex = '^\s*$' # \s = whitespace character
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