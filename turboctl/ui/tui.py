"""Text-based user interfaces for the pump."""

import readline
# Importing the readline module adds better editing capabilities 
# to the input function.
from collections import namedtuple 
import os

from ..data import PARAMETERS, ERRORS, WARNINGS, Types

from .abstractui import AbstractUI
from .table import table
from .command_parser import CommandParser
from .output import (help_string, full_output, parameter_output, 
                     control_or_status_output, hardware_output)
from .ui_errors import UIError, UIValueError, UITypeError

Command = namedtuple('Command', 'names, function, args, description')    

COMMAND_LIST = [
    Command(names=['onoff', 'o'],
        function='cmd_onoff',
        args=[],
        description='Turn the pump on or off'),

    Command(names=['status', 's'],
            function='cmd_status',
            args=[],
            description='Report pump status'),

    Command(names=['read', 'r'],
            function='cmd_read',
            args=['number', 'index=0'],
            description='Read the value of a parameter'),

    Command(names=['write', 'w'],
            function='cmd_write',
            args=['value', 'number', 'index=0'],
            description='Write a value to a parameter'),
                        
    Command(names=['list', 'l'],
            function='cmd_list',
            args=['letter', 'numbers'],
            description=(
                "List parameters (letter='p'), "
                "errors (letter='e') "
                "or warnings (letter='w'). "
                "*numbers* should be an iterable "
                "of the numbers to be listed or 'all'.")),

    Command(names=['info', 'i'],
            function='cmd_info',
            args=['letter', 'number'],
            description=(
                "Display a single parameter (letter='p'), "
                "error (letter='e') "
                "or warning (letter='w'). ")),

    Command(names=['help', 'h'],
            function='cmd_help',
            args=[],
            description='Display a help message'),

    Command(names=['exit', 'e', 'x', 'q'],
            function='cmd_exit',
            args=[],
            description='Exit the program'),
    
    Command(names=['debug', 'd'],
            function='cmd_debug',
            args=[],
            description='Turn debug mode on or off'),
    
    Command(names=['verbosity', 'v'],
        function='cmd_verbosity',
        args=['value'],
        description='Set output verbosity (valid values are 1, 2 and 3)'),
    
    Command(names=['setpoint', 'sp'],
        function='cmd_setpoint',
        args=['value'],
        description='Set frequency setpoint'),
            
    Command(names=['save', 'sv'],
        function='cmd_save',
        args=[],
        description='Save parameters to nonvolatile memory'),
]


class AbstractTUI(AbstractUI):
    """An abstract class for text-based user interfaces (TUIs).
    
    Specific TUI implementations are created by subclassing this class.
    """
            
    databases = {'parameter': PARAMETERS, 'error': ERRORS, 'warning': WARNINGS}
    widths = {'parameter': {'name': 20, 'type': 16, 'description': 50}, 
              'error'    : {'name': 30, 'possible_cause': 50, 'remedy': 50}, 
              'warning'  : {'name': 30, 'possible_cause': 50, 'remedy': 50}
             }
    
    def __init__(self, *args, **kwargs):
        """Initialize a new AbstractTUI.
        
        Arguments are delegated to AbstractUI.__init__().
        """
        super().__init__(*args, **kwargs)
        self.verbosity = 2
        self.debug = False
        self.cmd_parser = CommandParser(self, COMMAND_LIST)
        
    def process_input(self, string):
        """Process *string* and execute the commands defined 
        therein.
        
        Returns: True if the command is an exit command, False 
            otherwise.
        """
        try:
            return self.cmd_parser.parse(string, self.debug)
        except UIError as e:
            print(e)
            return False
        
    def cmd_onoff(self):
        """Call AbstractUI.on_off() and print the results."""
        
        query, reply = self.on_off()       

        if self.verbosity == 3:
            print(full_output(query, reply))
        
        elif self.verbosity == 2:
            print('Turning the pump on or off')
            conditions = control_or_status_output(reply)
            if conditions:
                print(conditions)
        
        elif self.verbosity == 1:
            print('Turning the pump on or off')
            conditions = control_or_status_output(reply, verbose=False)
            if conditions:
                print(conditions)
        
    def cmd_status(self):
        """Call AbstractUI.status() and print the results."""
        
        query, reply = self.status()
        
        if self.verbosity == 3:
            print(full_output(query, reply))
        
        elif self.verbosity == 2:
            conditions = control_or_status_output(reply)
            if conditions:
                print(conditions)
            print(hardware_output(reply))
        
        elif self.verbosity == 1:
            conditions = control_or_status_output(reply, verbose=False)
            if conditions:
                print(conditions)
            print(hardware_output(reply, verbose=False))
        
    def cmd_read(self, number, index=0):
        """Call AbstractUI.read_parameter() and print the results.
        
        The arguments are passed to AbstractUI.read_parameter() 
        unchanged, but a UIValueError or UITypeError will be 
        raised if the arguments are invalid.
        """
        
        
        
        
        
        self._check_type('number', number, int)
        self._check_type('index', index, int)
        self._check_pew_number('parameter', number)
        
        query, reply = self.read_parameter(number, index)
        
        if self.verbosity == 3:
            print(full_output(query, reply))
        
        elif self.verbosity == 2:
            print(parameter_output(reply))
        
        elif self.verbosity == 1:
            print(parameter_output(reply, verbose=False))
       
    def cmd_write(self, value, number, index=0):
        """Call AbstractUI.write_parameter() and print the results.
        
        The arguments are passed to AbstractUI.read_parameter() 
        unchanged, but a UIValueError or UITypeError will be 
        raised if the arguments are invalid.
        """
        
        self._check_type('value', value, (int, float))
        self._check_type('number', number, int)
        self._check_type('index', index, int)
        self._check_parameter_type(number, value)
        
        query, reply = self.write_parameter(value, number, index)
        
        if self.verbosity == 3:
            print(full_output(query, reply))
        
        elif self.verbosity == 2:
            print(parameter_output(reply))
        
        elif self.verbosity == 1:
            print(parameter_output(reply, verbose=False))
            
    def cmd_list(self, letter, numbers):
        """List parameters, error or warnings.
        
        This command opens an information table with the less program.
        
        Args:
            letter: 'p', 'e' or 'w' depending on what should be listed.
                'p' lists parameters, 'e' errors and 'w' warnings.
            numbers: An iterable of numbers or 'all'. This defined 
                which parameters/errors/warnings should be displayed.
        
        Raises:
            UIValueError or UITypeError if the arguments are invalid.
        """
        name = self._letter_to_name(letter)
        self._check_pew_numbers(name, numbers)
        
        command = 'less -S'
        pipe = os.popen(command, 'w')
        pipe.write(table(self.databases[name], numbers, self.widths[name]))
        pipe.close()

    def cmd_info(self, letter, number):
        """Display information about a single parameters, error or 
        warnings.
        
        Unlike *cmd_list*, this command doesn't use less, and prints 
        the output normally instead.
        
        Args:
            letter: 'p', 'e' or 'w' in the same way as in *cmd_list*.
            number: A single number determining which 
                parameter/error/warning should be displayed.
        
        Raises:
            UIValueError or UITypeError if the arguments are invalid.
        """
        name = self._letter_to_name(letter)
        self._check_pew_number(name, number)
        
        print(table(self.databases[name], [number], self.widths[name]))
        
    def _letter_to_name(self, letter):
        """Return a word ('parameter', 'error' or 'warning') based on 
        *letter* ('p', 'e', 'w').
        
        Raises:
            UITypeError: If *letter* isn't a string. 
            UIValueError: If *letter* is a string but not 
                'p', 'e' or 'w'.
        """
        names = {'p': 'parameter',
                 'e': 'error',
                 'w': 'warning'}
        
        self._check_type('letter', letter, str)
        try:
            return names[letter]
        except KeyError:
            raise UIValueError(
                f"The argument 'letter' should be 'p', 'e' or 'w', "
                f"not {repr(letter)}")
                                        
    def cmd_debug(self, value):
        """Turn debug mode on or off.
        
        Args:
            Value: True, False, 1 or 0.
            
        Raises:
            UITypeError or UIValueError if *value* is invalid.
        
        by setting *value* to True/1 or False/0."""
        self._check_type('value', value, (int, bool))
        # In Python, True == 1 and False == 0.
        if not value in (True, False):
            raise UIValueError(
                f"The argument 'value' should be True, False, 1 or 0,"
                f"not {repr(value)}")
        
        self.debug = bool(value)
        print(f'debug={self.debug}')
        
    def cmd_verbosity(self, value):
        """Set verbosity to the desired level.
        
        Verbosity affects how much text is displayed when running TUI 
        commands.
        
        verbosity=3 prints all information carried by both the 
            telegram sent to the pump and the telegram received back.
        verbosity=2 is the default level, and doesn't print 
            information that is irrelevant to the command that was run.
        verbosity=1 only prints the bare minum needed to display the 
            output of the command.
        
        Args:
            Value: 1, 2 or 3.
            
        Raises:
            UITypeError or UIValueError: If *value* is invalid.
        """
        self._check_type('value', value, int)
        if value not in (1, 2, 3):
            raise UIValueError(
                f"The argument 'value' should be 1, 2 or 3, not {repr(value)}")
        self.verbosity = value
        
    def cmd_setpoint(self, value):
        """Set the frequency setpoint to *value*.
        
        Args:
            value: An int.
            
        Raises:
            UITypeError: If *value* isn't an int.
        """
        self._check_type('value', value, int)
        self.set_frequency(value)
        
    def cmd_save(self):
        """Save modified parameters to nonvolatile memory.
        
        Parameters that are not saved will be reset when the pump 
        is restarted.
        """
        self.save_data()
               
    def cmd_help(self):
        """Print a help message."""
        print(help_string(COMMAND_LIST))
        
    def cmd_exit(self):
        """Return True, which tells the TUI to exit the program."""
        return True
        
    def _check_type(self, name, value, types):
        """Make sure that *value* is an instance of any of the types 
        in *types*.
        
        Args:
            name: The variable name that should be used in error 
                messages (a string).
            value: The value of the variable.
            types: A type or a tuple of types.
        
        Raises:
            UITypeError: If *value* is not an instance of any of the 
                types in *types*.
        """
        
        if not isinstance(value, types):
            raise UITypeError(
                f"The argument '{name}' should be of one of the following "
                f"types: '{types}, not {type(value)}")
                    
    def _check_pew_numbers(self, name, numbers):
        """Make sure that all the numbers in *numbers* are valid 
        parameter, error or warning numbers.
        
        Args:
            name: 'parameter', 'error' or 'warning'.
            numbers: An iterable of ints.
            
        Raises:
            UIValueError: 
                - If *numbers* is a string other than 'all'.
                - If *name* is not 'parameter', 'error' or 'warning'.
                - If any of the numbers in *numbers* is not a valid 
                    parameter/error/warning number.
            UITypeError: If *numbers* is not an iterable.
        """
        if isinstance(numbers, str):
            if numbers == 'all':
                return numbers
            raise UIValueError(
                f"The only permitted string value for the argument "
                f"'numbers' is 'all'")
            
        try:
            for n in numbers:
                self._check_pew_number(name, n)
            return numbers
        except TypeError:
            pass
        
        raise UITypeError(
            f"The argument 'numbers' must be an iterable or 'all', not a(n) "
            f"{type(numbers).__name__}")
            
    def _check_pew_number(self, name, number):
        """Make sure that *number* is a valid parameter, error or 
        warning number.
        
        Args:
            name: 'parameter', 'error' or 'warning'.
            number: An ints.
            
        Raises:
            UIValueError: 
                - If *name* is not 'parameter', 'error' or 'warning'.
                - If number is not a valid parameter/error/warning 
                    number.
        """
        if name == 'parameter':
            database = PARAMETERS
        elif name == 'error':
            database = ERRORS
        elif name == 'warning':
            database = WARNINGS
        else:
            raise ValueError(
                f"name should be 'parameter', 'error' or 'warning', "
                f"not {name}")
        
        if not number in database:
            raise UIValueError(f'There is no {name} {number}')
                
    def _check_parameter_type(self, number, value):
        """Make sure that *value* is of the same type as parameter *number*.
        
        Raises:
            UIValueError: If there is no parameter *number*.
            UITypeError: If type(value) doesn't match the type of the 
                parameter.
        """

        self._check_pew_number('parameter', number)
        type_ = self.databases['parameter'][number].type
        
        if not Types.is_type(value, type_):
            raise UITypeError(
                f'The type of parameter {number} is {type_.description}, '
                f'not {Types.type_of(value).description}')

        
class InteractiveTUI(AbstractTUI):
    """An interactive TUI that runs until exited."""
    
    def __init__(self, port):
        super().__init__(port)
    
    def run(self):
        """Run the UI.
        
        The UI asks for input and executes commands until a command 
        returns True, after which the UI exits.
        """
        print("Type a command or 'help' for a list of commands")
        prompt = '>> '
        
        stop = False
        while not stop:
            stop = super().process_input(input(prompt))


class ShellTUI(AbstractTUI):
    """A TUI that runs a single command."""
    
    def __init__(self, port):
        super().__init__(port)
    
    def run(self, command):
        """Process and execute *command* (a string)."""
        super().process_input(command)