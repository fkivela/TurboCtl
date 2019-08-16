import textwrap
import tabulate

from ..data import ControlBits
from ..telegram import Query, Reply

INDENT = 4 * ' '

def help_string(commands):
    string = 'List of accepted commands:'
    
    def format_arg(arg):
        if '=' in arg:
            return f'[{arg}]'
        else:
            return f'<{arg}>' 
    
    data = []
    for command in commands:       
        name = command.name
        args = ' '.join([format_arg(arg) for arg in command.args])
        args = ' ' + args if args else ''
        description = command.description
        
        data.append([name + args, description])

    return string + '\n' + tabulate.tabulate(data, tablefmt='plain')

def output(query, reply):
    return (
        'Sent a telegram with the following contents:\n'
        + _wrapper_output(query) + '\n'
        '\n'         
        'Received a telegram with the following contents:\n'
        + _wrapper_output(reply)
        )
    
def _wrapper_output(query_or_reply):
    strings = [_parameter_output(query_or_reply), 
               _control_or_status_output(query_or_reply), 
               _hardware_output(query_or_reply)]
    string = '\n'.join([s for s in strings if s])
    return textwrap.indent(string, INDENT)

def _parameter_output(wrapper):
    
    mode = wrapper.parameter_mode
    number = wrapper.parameter_number
    index = wrapper.parameter_index
    indexed = wrapper.parameter_indexed
    value = wrapper.parameter_value
    unit = wrapper.parameter_unit
    
    value_str = f'{value} {unit}' if unit else f'{value}'
    number_str = f'{number}, index {index}' if indexed else f'{number}'
    
    if mode == 'none':
        return 'No parameter access'
    
    if mode == 'read':
        return f'Return the value of parameter {number_str}'
            
    if mode == 'write':
        return f'Write the value {value_str} to parameter {number_str}'
    
    if mode == 'response':
        return f'The value of parameter {number_str} is {value_str}'
    
    if mode == 'error':
        return (f"Can't access parameter; error type: {wrapper.error_message}")
        
    if mode == 'no write':
        return f"Parameter {number} isn't writable"
    
    raise RuntimeError(f'Invalid parameter_mode: {wrapper.parameter_mode}')    
    
def _hardware_output(wrapper):
    
    if ControlBits.FREQ_SETPOINT in wrapper.control_or_status_set:
        return f'Stator frequency setpoint: {wrapper.frequency} Hz' + '\n'
    
    if isinstance(wrapper, Query):
        return ''
    
    return (           
        f'Stator frequency: {wrapper.frequency} Hz' + '\n'
        f'Frequency converter temperature: {wrapper.temperature} °C' + '\n'
        f'Motor current: {wrapper.current}×0.1 A' + '\n'
        f'Intermediate circuit voltage: {wrapper.voltage}×0.1 V'
    )
     
def _control_or_status_output(wrapper):
    
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