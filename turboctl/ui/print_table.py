import os
import textwrap as tx
import tabulate

from ..data import Types
        
tabulate.PRESERVE_WHITESPACE = True
        
def print_table(database, numbers='all', widths={}, use_less=True):

    if numbers == 'all':
        data_objects = database.values()
        
    else:
        data_objects = []
        for n in numbers:
            try:
                data_objects.append(database[n])
            except KeyError:
                raise ValueError(f'Invalid number: {n}')

    # If a maximum width is not specified, it is set to infinite.
    for f in _fieldnames(database):
        if f not in widths:
            widths[f] = float('inf')
    
    if use_less:
        command = 'less -S'
        pipe = os.popen(command, 'w')
        pipe.write(_table(widths, data_objects))
        pipe.close()
    else:
        print(_table(widths, data_objects))
        
def _fieldnames(database):
    try:
        object_ = list(database.values())[0]
    except KeyError as e:
        raise RuntimeError('*database* is empty') from e
        
    return list(object_.fields.keys())

def _table(widths, data_objects):
    rows = [format_row(o, widths) for o in data_objects]
    return tabulate.tabulate(rows, tablefmt='plain')

def format_row(data_object, widths):
    
    return [_format_field(name, value, widths[name])
            for name, value in data_object.fields.items()]

def _format_field(name, value, width):
    
    if isinstance(value, Types):
        value = value.description
        
    if isinstance(value, range):
        value = f'{value.start}...{value.stop-1}' if value else '-'            
        
    if value == '':
        value = '-'
    
    value = str(value)
    
    if name == 'type':
        value = value.capitalize()
        
    name = name.replace('_', ' ')
    
    value = _wrap(value, width)
    
    return name.upper() + '\n' + value + '\n '

def _wrap(string, width):
    lines = string.split('\n')
    wrapped_lines = [tx.wrap(line, width) for line in lines]
    shortened_lines = ['\n'.join(list_) for list_ in wrapped_lines]
    return '\n'.join(shortened_lines)