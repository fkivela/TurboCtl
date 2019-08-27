"""Create formatted output strings for the TUI."""

import textwrap
import tabulate
from textwrap import wrap

from ..data import ControlBits, StatusBits
from ..telegram import Query, Reply

INDENT = 4 * ' '

def help_string(commands):
    """Return the help string.
    
    Args:
        commands: A list of Command objects detailing the commands 
            accepted by the TUI.
    """
    
    string = 'Accepted commands:'
    description_width = 30
    
    def format_arg(arg):
        if '=' in arg:
            return f'[{arg}]'
        else:
            return f'<{arg}>' 
    
    data = []
    headers = ['Command', 'Aliases', 'Args', 'Description']
    for command in commands:       
        name = command.names[0]
        aliases = ', '.join(command.names[1:])
        args = ' '.join([format_arg(arg) for arg in command.args])
        description = '\n'.join(wrap(command.description, description_width))
        data.append([name, aliases, args, description])

    return string + '\n' + tabulate.tabulate(data, headers=headers, 
                                             tablefmt='plain')

def full_output(query, reply):
    """Return a string displaying all data that was sent and received 
    when a command was executed.
    
    Args:
        query: The Query object that was sent to the pump.
        reply: The Reply object that was received from the pump.
        
    Returns:
        A string like the following:
            
        Sent a telegram with the following contents:
            No parameter access
            No control bits active
            Stator frequency: 0 Hz
            Frequency converter temperature: 0 °C
            Motor current: 0×0.1 A
            Intermediate circuit voltage: 0×0.1 V
    
        Received a telegram with the following contents:
            No parameter access
            Present status conditions:
                Ready for operation
            Stator frequency: 0 Hz
            Frequency converter temperature: 0 °C
            Motor current: 0×0.1 A
            Intermediate circuit voltage: 0×0.1 V
    """
    
    return (
        'Sent a telegram with the following contents:\n'
        + _wrapper_output(query) + '\n'
        '\n'         
        'Received a telegram with the following contents:\n'
        + _wrapper_output(reply)
        )
    
def _wrapper_output(query_or_reply):
    """Return a string displaying all data that was sent in a Query 
    object or received in a Reply object.
    """
    strings = [parameter_output(query_or_reply), 
               control_or_status_output(query_or_reply), 
               hardware_output(query_or_reply)]
    string = '\n'.join([s for s in strings if s])
    return textwrap.indent(string, INDENT)

def parameter_output(wrapper, verbose=True):
    """Return a string displaying parameter data.
    
    Args:
        wrapper: A Query or Reply object where the data is read from.
        verbose=True: If this is False, the string will be very brief.
        
    Returns:
        A string matching one of formats below.    
        
        If verbose=True, the possible formats are
        - 'No parameter access'
        - 'Return the value of parameter 1'
        - 'Write the value 100 to parameter 1'
        for queries and
        - 'No parameter access
        - 'The value of parameter 1 is 100'
        - 'Can't access parameter 1; error type: min./max. restriction'
        - 'Parameter 1 isn't writable'
        for replies.
        
        If verbose=False, the formats are
        - ''
        - '100'
        - 'Error: min./max. restriction'
        - 'Not writable'
        for replies; queries always return ''.
    """
    
    mode = wrapper.parameter_mode
    number = wrapper.parameter_number
    index = wrapper.parameter_index
    indexed = wrapper.parameter_indexed
    value = wrapper.parameter_value
    unit = wrapper.parameter_unit
        
    value_str = f'{value} {unit}' if unit else f'{value}'
    number_str = f'{number}, index {index}' if indexed else f'{number}'
        
    if mode == 'none':
        return 'No parameter access' if verbose else ''
    
    if mode == 'read':
        return f'Return the value of parameter {number_str}' if verbose else ''
            
    if mode == 'write':
        return (f'Write the value {value_str} to parameter {number_str}' 
                if verbose else '')
    
    if mode == 'response':
        return (f'The value of parameter {number_str} is {value_str}' 
                if verbose else value_str)
    
    if mode == 'error':
        return (f"Can't access parameter {number_str}: {wrapper.error_message}"
                if verbose else f'Error: {wrapper.error_message}')
        
    if mode == 'no write':
        return (f"Parameter {number} isn't writable" if verbose 
                else 'Not writable')
    
    raise RuntimeError(f'Invalid parameter_mode: {wrapper.parameter_mode}')    
         
def control_or_status_output(wrapper, verbose=True):
    """Return a string displaying active control or status bits.
    
    Args:
        wrapper: A Query or Reply object where the data is read from.
        verbose=True: If this is False, the string will be very brief.
        
    Returns:
        A string matching one of formats below.
        
        If verbose=True, the possible formats are
        - ('Active control bits:\n'
           '    Start/stop\n'
           '    Enable control bits 0, 5, 6, 7, 8, 13, 14, 15')
        - 'No control bits active'
        for control bits and
        - ('Present status conditions:\n'
           '    Pump is turning\n'
           '    Accelerating')
        - 'No status conditions present'
        for status bits.
            
        If verbose=False, 'Errors present' or 'Warnings present' is 
        returned if *wrapper* is a Reply and the warning or error bits 
        are active. Otherwise, '' is returned.
    """
    if not verbose:
        strings = []
        if StatusBits.ERROR in wrapper.control_or_status_set:
            strings.append('Error(s) present')
        if StatusBits.WARNING in wrapper.control_or_status_set:
            strings.append('Warning(s) present')
        return '\n'.join(strings)
    
    if isinstance(wrapper, Query):
        header = 'Active control bits:'
        empty = 'No control bits active'
    elif isinstance(wrapper, Reply):
        header = 'Present status conditions:'
        empty = 'No status conditions present'
    else:
        raise TypeError(
            f'*wrapper* should be a Query or a Reply, not {type(wrapper)}')
    
    cslist = sorted(list(wrapper.control_or_status_set))
    descriptions = [INDENT + cs.description for cs in cslist]
    
    if descriptions:
        return '\n'.join([header] + descriptions)
    else:
        return empty
    
def hardware_output(wrapper, verbose=True):
    """Return a string displaying hardware data.
    
    Args:
        wrapper: A Query or Reply object where the data is read from.
        verbose=True: If this is False, the string will be very brief.
        
    Returns:
        A string matching one of formats below.
        
        If verbose=True, the format is
        ('Stator frequency: 0 Hz\n'
         'Frequency converter temperature: 0 °C\n'
         'Motor current: 0×0.1 A\n'
         'Intermediate circuit voltage: 0×0.1 V')
        for replies and
        'Stator frequency setpoint: 1000 Hz' (if the frequency 
        setpoint is activated) or '' for queries.
        
        If verbose=False, the format is
        ('f=0 Hz\n'
         'T=0 °C\n'
         'I=0×0.1 A\n'
         'U=0×0.1 V')
        for replies and '' for queries.
    """
    
    f_val = f'{wrapper.frequency} Hz'
    T_val = f'{wrapper.temperature} °C'
    I_val = f'{wrapper.current}×0.1 A'
    U_val = f'{wrapper.voltage}×0.1 V'
    
    if verbose and ControlBits.FREQ_SETPOINT in wrapper.control_or_status_set:
        return f'Stator frequency setpoint: {f_val}'
    elif isinstance(wrapper, Query):
        return ''
    
    f_str = 'Stator frequency: ' if verbose else 'f='
    T_str = 'Frequency converter temperature: ' if verbose else 'T='
    I_str = 'Motor current: ' if verbose else 'I='
    U_str = 'Intermediate circuit voltage: ' if verbose else 'U='
    
    return (f_str + f_val + '\n' + 
            T_str + T_val + '\n' +
            I_str + I_val + '\n' +
            U_str + U_val )