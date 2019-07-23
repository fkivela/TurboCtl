"""This module contains the correct_error_message function."""
import re

def correct_error_message(message):
    """Change an error message so that it can be presented to a user.
    
    If an invalid number of arguments is given to a TUI command, 
    Python raises a TypeError.
    However, the error message can't be shown to the user unaltered,
    because it reports the number of arguments wrong (because a TUI 
    always automatically passes the *self* argument to all command 
    methods) and calls commands by their method names instead of the 
    names visible to the user.
    
    This function adds the correct command name to the error message 
    and removes the *self* argument from the reported argument count.
    """
    return _change_argument_count(_change_function_name(message))

def _change_function_name(message):
    """Change 'cmd_example()' to "'example'"."""
    
    regex = '(^cmd_)([a-z_]+)(\(\))'
    match = re.match(regex, message)
    if not match:
        return message
    
    cmd_, name, parentheses = match.groups()
    new_name = f"'{name}'"
    return re.sub(regex, new_name, message)

def _change_argument_count(message):
    """Take a string of matching the format '<function_name> takes x 
    positional arguments but y were given' and decrease the numbers 
    (x and y in this example) by 1."""
    
    regex = ('(.* takes) (\d+|from \d+ to \d+) (positional argument)(s)? '
             '(but) (\d+) (was|were) (given)') 
    # '\d' matches any number.

    match = re.match(regex, message)
    if not match:
        return message

    groups = list(match.groups())
    (func_takes, number_range, positional_arg, s, 
     but, n_args, was_were, given) = groups 
     # Give names to the different groups.
    
    # *number_range* can match either the format 'x' or 'from x to y'.
    number_range_regex = '(\d+)|(from) (\d+) (to) (\d+)'
    number_range_match = re.match(number_range_regex, number_range)
    number_range_groups = [g for g in number_range_match.groups() if g]
    # *match* may contain empty groups; remove them.
    for i, g in enumerate(number_range_groups):
        try:
            number_range_groups[i]=str(int(g)-1)
        except ValueError:
            pass
    number_range = ' '.join(number_range_groups)

    n_args = str(int(n_args) - 1)
    was_were = 'was' if n_args == '1' else 'were'
    s = '' if number_range == '1' else 's'
    positional_arg_s = positional_arg + s
    # The 's' must be added to the end of 'argument' without 
    # a space in between.
    
    return ' '.join([func_takes, number_range, positional_arg_s, 
                     but, n_args, was_were, given])