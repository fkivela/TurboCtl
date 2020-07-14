"""Create tables of parameters, errors and warnings."""
import textwrap as tx
import tabulate

        
tabulate.PRESERVE_WHITESPACE = True
        
def table(database, numbers='all', widths={}):
    """Return a table of parameters, errors or warnings.
    
    Args:
        database: A dict of parameters, errors or warnings. The keys 
            should be numbers and the values Parameter or 
            ErrorOrWarning objects.
        numbers: 'all', or the numbers of the 
            parameters/errors/warnings that should be displayed.
        widths: A dict with keys corresponding to column names and 
            values to the maximum widths of the columns. Column names 
            are the same as the attributes of the Parameter or 
            ErrorOrWarning classes. If a column's maximum width isn't 
            specified in *widths*, it is set to infinite and no text 
            wrapping is used for that column.
    
    Returns:
        The table as a formatted string ready for printing. 
            
    Raises:
        ValueError: If *database* is empty or if there is no 
            parameter/error/warning corresponding to a number 
            in *numbers*.
    """
    a = array(database, numbers, widths)
    return tabulate.tabulate(a, tablefmt='plain')

def array(database, numbers='all', widths={}):
    """The same as table(), but returns the table as a 2d list 
    instead of a string.
    
    This function can be used to test this module.
    """
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
    for f in _column_names(database):
        if f not in widths:
            widths[f] = float('inf')
    
    return [_format_row(o, widths) for o in data_objects]
        
def _column_names(database):
    """Return the names of the columns in the table.
    
    The column names correspond to the attributes of the objects in 
    *database*.
    It is assumed *database* only contains objects of one type 
    (Parameter or ErrorOrWarning).
    
    Returns:
        A list of strings.
        
    Raises:
        ValueError: If *database* is empty.
    """
    try:
        object_ = list(database.values())[0]
    except KeyError as e:
        raise ValueError('*database* is empty') from e
        
    return list(object_.fields.keys())

def _format_row(data_object, widths):
    """Return a single table row.
    
    Args:
        data_object: The object whose data should be displayed on 
            the row.
        widths: The maximum widths of the cells in the row (a list).
        
    Returns: A list of strings corresponding to the text displayed in
        each cell of the row.
    """    
    return [_format_field(name, value, widths[name])
            for name, value in data_object.fields.items()]

def _format_field(name, value, width):
    """Return a single formatted table cell.
    
    Args:
        name: The name of the column the cell belongs to.
        value: The value to be displayed in the cell (any type).
        width: The maximum width of the cell (in characters).
        
    Returns: A string. Line breaks will be inserted in appropriate 
        places, if some of the lines in text would be longer than 
        *width* wthout them. If *value* already contains line breaks, 
        these are preserved.
    """
    if isinstance(value, range):
        value = f'{value.start}...{value.stop-1}' if value else '-'            
        
    if value == '':
        value = '-'
    
    value = str(value)
    
    if name == 'type':
        value = value.capitalize()
        
    name = name.replace('_', ' ')
    
    value = _wrap(value, width)
    
    # Tabulate seems to strip a '\n' from the end of a string, 
    # so two line breaks are needed to add an empty line between rows.
    return name.upper() + '\n' + value + '\n\n'

def _wrap(string, width):
    """Add line breaks to a long string.
    
    Args:
        string: The string that line breaks should be insterted to.
        width: The maximum amount of characters in each line.
    
    Returns:
        A string with line breaks inserted in appropriate places. 
        If *string* already contains line breaks, these are 
        preserved.
    """
    lines = string.split('\n')
    wrapped_lines = [tx.wrap(line, width) for line in lines]
    shortened_lines = ['\n'.join(list_) for list_ in wrapped_lines]
    return '\n'.join(shortened_lines)