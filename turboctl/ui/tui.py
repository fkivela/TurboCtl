from collections import namedtuple 

from ..data import PARAMETERS, ERRORS, WARNINGS, Types

from .abstractui import AbstractUI
from .shell import Shell
from .print_table import print_table
from .command_parser import CommandParser
from .output import output, help_string
from .ui_errors import UIError, UIValueError, UITypeError

Command = namedtuple('Command', 'name, function, args, description')    

COMMAND_LIST = [
    Command(name='onoff',
        function='cmd_onoff',
        args=[],
        description='Turn the pump on or off'),

    Command(name='status',
            function='cmd_status',
            args=[],
            description='Report pump status'),

    Command(name='read',
            function='cmd_read',
            args=['number', 'index=0'],
            description='Read the value of a parameter'),

    Command(name='write',
            function='cmd_write',
            args=['value', 'number', 'index=0'],
            description='Write a value to a parameter'),
                        
    Command(name='list',
            function='cmd_list',
            args=['letter', 'numbers'],
            description=(
                "List parameters (letter='p'), "
                "errors (letter='e') "
                "or warnings (letter='w'). "
                "*numbers* should be an iterable "
                "of the numbers to be listed or 'all'.")),

    Command(name='info',
            function='cmd_info',
            args=['letter', 'number'],
            description=(
                "Display a single parameter (letter='p'), "
                "error (letter='e') "
                "or warning (letter='w'). ")),

    Command(name='help',
            function='cmd_help',
            args=[],
            description='Display a help message'),

    Command(name='exit',
            function='cmd_exit',
            args=[],
            description='Exit the program'),
    
    Command(name='debug',
            function='cmd_debug',
            args=[],
            description='Turn debug mode on or off')
]


class AbstractTUI(AbstractUI):
            
    databases = {'parameter': PARAMETERS, 'error': ERRORS, 'warning': WARNINGS}
    
    widths = {'parameter': {'name': 20, 'type': 16, 'description': 50}, 
              'error'    : {'name': 30, 'possible_cause': 50, 'remedy': 50}, 
              'warning'  : {'name': 30, 'possible_cause': 50, 'remedy': 50}
             }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = False
        self.cmd_parser = CommandParser(self, COMMAND_LIST)
        
    def process_input(self, string):
        try:
            return self.cmd_parser.parse(string, self.debug)
        except UIError as e:
            print(e)
            return False
        
    def cmd_onoff(self):
        query, reply = self.on_off()
        self._print_output(query, reply)
        
    def cmd_status(self):
        query, reply = self.status()
        self._print_output(query, reply)
        
    def cmd_read(self, number, index=0):
        
        self._check_type('number', number, int)
        self._check_type('index', index, int)
        self._check_pew_number('parameter', number)
        
        query, reply = self.read_parameter(number, index)
        self._print_output(query, reply)
       
    def cmd_write(self, value, number, index=0):
        
        self._check_type('value', value, (int, float))
        self._check_type('number', number, int)
        self._check_type('index', index, int)
        self._check_parameter_type(number, value)
        
        query, reply = self.write_parameter(value, number, index)
        self._print_output(query, reply)
           
    def cmd_list(self, letter, numbers):
        name = self._letter_to_name(letter)
        self._check_pew_numbers(name, numbers)
        
        print_table(self.databases[name], numbers, self.widths[name], 
                    use_less=True)

    def cmd_info(self, letter, number):
        name = self._letter_to_name(letter)
        self._check_pew_number(name, number)
        
        print_table(self.databases[name], [number], self.widths[name], 
                    use_less=False)
        
    def _letter_to_name(self, letter):
        names = {'p': 'parameter',
                 'e': 'error',
                 'w': 'warning'}
        
        self._check_type('letter', letter, (str))
        try:
            return names[letter]
        except KeyError:
            raise UIValueError(
                f"The argument 'letter' should be 'p', 'e' or 'w', not {repr(letter)}")
                                        
    def cmd_debug(self):
        self.debug = not self.debug
        print(f'debug={self.debug}')
           
    def _print_output(self, query, reply):
        print('\n' + output(query, reply) + '\n')
        
    def cmd_help(self):
        print(help_string(COMMAND_LIST))
        
    def cmd_exit(self):
        return True
        
    def _check_type(self, name, value, types):
        
        if not isinstance(value, types):
            raise UITypeError(
                f"The argument '{name}' should be of one of the following types: "
                f'{types}, not {type(value)}')
                    
    def _check_pew_numbers(self, name, numbers):
        
        if isinstance(numbers, str):
            if numbers == 'all':
                return numbers
            raise UIValueError(
                f"The only permitted string value for the argument 'numbers' is 'all'")
            
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

        self._check_pew_number('parameter', number)
        type_ = self.databases['parameter'][number].type
        
        if not Types.is_type(value, type_):
            raise UITypeError(
                f'The type of parameter {number} is {type_.description}, '
                f'not {Types.type_of(value).description}')


class InteractiveTUI(AbstractTUI):
    
    def __init__(self, port):
        super().__init__(port)
        self.shell = Shell(super().process_input)
        self.shell.prompt = "Type a command or 'help' for a list of commands: "
    
    def run(self):
        self.shell.run()
        
#class InteractiveTUI(AbstractTUI):
#    
#    def __init__(self, port):
#        super().__init__(port)
#    
#    def run(self):
#        prompt = "Type a command or 'help' for a list of commands: "
#        
#        stop = False
#        while not stop:
#            stop = super().process_input(input(prompt))
            
            
class ScriptTUI(AbstractTUI):
    pass

#    
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#    
#    def run(self, file):
#        with  open(file, "r") as file:
#            line = file.read()
#            #TODO: while loop
#            super().process_input(line)
            

class ShellTUI(AbstractTUI):
    
    def __init__(self, port):
        super().__init__(port)
    
    def run(self, command):
        super().process_input(command)