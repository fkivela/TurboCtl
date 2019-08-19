import textwrap
import tabulate
from textwrap import wrap

from ..data import ControlBits, StatusBits
from ..telegram import Query, Reply

INDENT = 4 * ' '

def help_string(commands):
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
    return (
        'Sent a telegram with the following contents:\n'
        + _wrapper_output(query) + '\n'
        '\n'         
        'Received a telegram with the following contents:\n'
        + _wrapper_output(reply)
        )
    
def _wrapper_output(query_or_reply):
    strings = [parameter_output(query_or_reply), 
               control_or_status_output(query_or_reply), 
               hardware_output(query_or_reply)]
    string = '\n'.join([s for s in strings if s])
    return textwrap.indent(string, INDENT)

def parameter_output(wrapper, verbose=True):
    
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
        return (f"Can't access parameter; error type: {wrapper.error_message}"
                if verbose else f'Error: {wrapper.error_message}')
        
    if mode == 'no write':
        return (f"Parameter {number} isn't writable" if verbose 
                else 'Not writable')
    
    raise RuntimeError(f'Invalid parameter_mode: {wrapper.parameter_mode}')    
         
def control_or_status_output(wrapper, verbose=True):
    
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
    f_val = f'{wrapper.frequency} Hz'
    T_val = f'{wrapper.temperature} °C'
    I_val = f'{wrapper.current}×0.1 A'
    U_val = f'{wrapper.voltage}×0.1 V'
    
    if verbose and ControlBits.FREQ_SETPOINT in wrapper.control_or_status_set:
        f_str = 'Stator frequency setpoint: '
    elif verbose:
        f_str = 'Stator frequency: '
    else:
        f_str = 'f='
        
    T_str = 'Frequency converter temperature: ' if verbose else 'T='
    I_str = 'Motor current: ' if verbose else 'I='
    U_str = 'Intermediate circuit voltage: ' if verbose else 'U='
    
    return (f_str + f_val + '\n' + 
            T_str + T_val + '\n' +
            I_str + I_val + '\n' +
            U_str + U_val )