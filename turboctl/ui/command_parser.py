import ast
import re

from .ui_errors import (UIParseError, UICommandError, 
                        UIArgumentNumberError)
from .correct_error_message import correct_error_message


class CommandParser():
    """A class to parse text-based UI commands."""
    
    def __init__(self, ui, command_list):
        self.ui = ui
        self.command_dict = {cmd.name: cmd for cmd in command_list}

    def parse(self, string: str, debug: bool) -> bool:
        """Parse a command and perform the requested action.
        
        Args:
        """
        
        parts = [p for p in string.split(' ') if p]
        # Some of the cells in string.split(' ') can be empty if there 
        # are multiple consecutive spaces; ignore those.
        
        # Skip commands containing only whitespace.
        if not parts:
            return False
        
        cmd_string = parts[0]
        arg_strings = parts[1:]
                
        args_and_vals = [self._parse_arg(a) for a in arg_strings]
        args = [val for arg, val in args_and_vals if not arg]
        kwargs = {arg: val for arg, val in args_and_vals if arg}
                
        try:
            command = self.command_dict[cmd_string]
        except KeyError:
            raise UICommandError(f"Command '{cmd_string}' not recognized")
        
        try:
            stop = getattr(self.ui, command.function)(*args, **kwargs)
        except TypeError as e:
            if debug: raise e
            msg = correct_error_message(str(e))
            raise UIArgumentNumberError(msg)
            
        return stop
        
    @staticmethod
    def _parse_arg(arg_str):
    
        parts = arg_str.split('=')
        
        if len(parts) == 1:
            argname = None
            value_str = parts[0]
        elif len(parts) == 2:
            argname = parts[0]
            value_str = parts[1]
        else:
            raise UIParseError(f"Too many '='s in argument: {arg_str}")
        
        valid_argname = '^[a-zA-Z_][0-9a-zA-Z_]*$'
        
        if argname and not re.fullmatch(valid_argname, argname):
            raise UIParseError(f"Cannot parse argument name: {argname}")
        
        try:
            value = ast.literal_eval(value_str)
        except (SyntaxError, ValueError):
            value = ast.literal_eval(repr(value_str))
    
        return argname, value