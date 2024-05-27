"""A simple command-line user interface for controlling the pump."""

import ast
import inspect
from pathlib import Path
# Importing readline adds command editing etc. to the input function.
import readline  # pylint: disable=unused-import
import sys
import textwrap
import webbrowser

from turboctl.global_constants import DOCS_URL, VERSION
from turboctl.telegram.parser import PARAMETERS, ERRORS, WARNINGS
from turboctl.ui.control_interface import ControlInterface
from turboctl.ui.table import table


class CommandLineUI:
    """A simple command-line UI.

    Instances of this class should be closed after they are no longer
    needed by calling :attr:`control_interface`\
:meth:`.close() <turboctl.ui.control_interface.ControlInterface.close>`
    or using a ``with`` block. Otherwise the parallel thread created by
    :attr:`control_interface` may continue to run in the background and
    consume resources.

    This class contains several methods with names following the pattern
    ``cmd_<command>``.
    These methods correspond to the commands a user can give to the
    UI: when the command string ``'example'`` is entered, the ``cmd_example()``
    method is called.
    Because messages printed by the ``help`` command use the
    docstrings of these methods in an unaltered form, the docstrings
    are written in plain text and cannot contain any reStructuredText
    syntax that isn't easily readable by humans.

    Attributes:
        inputfile:
            A file-like object for receiving input.

        outputfile:
            A file-like object for writing output.

        debug (bool):
            Setting this to ``True`` activates the debug mode;
            the default value is ``False``.
            See :meth:`cmd_debug` for details.
            
        verbose (bool):
            Setting this to ``True`` increases the verbosity of the output of
            commands; the default value is ``False``.
            See :meth:`cmd_verbose` for details.

        control_interface:
            An :class:`~turboctl.ui.control_interface.ControlInterface` object
            used for sending commands to the pump.

        intro:
            A string displayed to the user upon starting the UI.
            The default value is ``f"Welcome to TurboCtl v. {__version__}! Type 'help' for a list of commands."``.

        prompt:
            A string displayed to the user every time the UI
            requests input. The default value is ``'>> '``.

        indent:
            Class attribute.
            A string used to indent text blocks.
            The default value is ``'    '`` (four spaces).

        cmds_and_aliases:
            Class attribute.
            A list of tuples, where index 0 of each tuple contains
            the name of a command accepted by the UI, and index 1
            contains a list of aliases for that command.
            It has the following value:
            ::

                [
                    ('pump'   , []),
                    ('status' , ['s']),
                    ('reset'  , ['re']),
                    ('read'   , ['r']),
                    ('write'  , ['w']),
                    ('info'   , ['i']),
                    ('exit'   , ['e', 'q', 'x']),
                    ('help'   , ['h']),
                    ('docs'   , ['d']),        
                    ('debug'  , ['db']),
                    ('verbose', ['v']),
                ]
    """

    indent = '    '

    # pylint: disable=bad-whitespace
    cmds_and_aliases = [
        ('pump'   , []),
        ('status' , ['s']),
        ('reset' ,  ['re']),
        ('read'   , ['r']),
        ('write'  , ['w']),
        ('info'   , ['i']),
        ('exit'   , ['e', 'q', 'x']),
        ('help'   , ['h']),
        ('docs'   , ['d']),        
        ('debug'  , ['db']),
        ('verbose', ['v'])
    ]
    # pylint: enable=bad-whitespace
    
    _dicts = {'p': PARAMETERS, 'e': ERRORS, 'w': WARNINGS}
    _widths = {'p': {'name': 20, 'type': 16, 'description': 50}, 
               'e': {'name': 30, 'possible_cause': 50, 'remedy': 50}, 
               'w': {'name': 30, 'possible_cause': 50, 'remedy': 50}
    }
    """A dict of *width* arguments for table.table."""

    def __init__(self, port=None, auto_update=True, 
                 inputfile=None, outputfile=None):
        """Initialize a new CommandLineUI.

        Args:
            port:
                This is passed to the initializer of :attr:`control_interface`.
            auto_update:
                This is also passed to :attr:`control_interface`.
            inputfile:
                The value of :attr:`inputfile`.
                If this is ``None``, the value is :data:`sys.stdin`.
            outputfile:
                The value of :attr:`outputfile`.
                If this is ``None``, the value is :data:`sys.stdout`.
        """
        if inputfile:
            self.inputfile = inputfile
        else:
            self.inputfile = sys.stdin

        if outputfile:
            self.outputfile = outputfile
        else:
            self.outputfile = sys.stdout

        # Replacing sys.stdin and sys.stdout would be simpler, but
        # could lead to unintended consequences, and would e.g.
        # prevent using multiple CommandLineUIs at once.

        self.control_interface = ControlInterface(port, auto_update)
        self.debug = False
        self.verbose = False
        self.intro = (f"Welcome to TurboCtl v. {VERSION}! "
                      f"Type 'help' for a list of commands.")
        self.prompt = '>> '
        self._stop_flag = False

    def __enter__(self):
        """Called upon entering a ``with`` block; returns *self*."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Called upon exiting a ``with`` block;
        calls :attr:`control_interface`:meth:`.close()
        <turboctl.ui.control_interface.ControlInterface.close()>`.

        The arguments are ignored.
        """
        self.control_interface.close()

    def run(self):
        """Run the UI.

        This function runs the following algorithm:

        1. Print :attr:`prompt` and wait for user input.
        2. Parse the input string into a command and its arguments by
           splitting it at whitespace.
        3. Call a method with the name ``cmd_<the given command>``.
           The method will execute the command and print its output.
           If no method with that name exists, print an error message
           and start again from step 1.
        4. If the method was :meth:`cmd_exit`, break the loop.
           Otherwise, start another iteration from step 1.
        """
        self.print(self.intro)

        while not self._stop_flag:
            string = self.input(self.prompt)
            self._run_command(string)

    # Don't use reStructuredText in command docstrings, since they are
    # displayed to the user unaltered.

    def cmd_pump(self, value):
        """Turn the pump on or off.

        Values of '1', 'True' and 'on' turn the pump on;
        '0', 'False' and 'off' turn it off.
        """
        # 1 == True and 0 == False.
        if value in [True, 'on']:
            self.print('Turning the pump on')
            return self.control_interface.pump_on()

        if value in [False, 'off']:
            self.print('Turning the pump off')
            return self.control_interface.pump_off()

        raise ValueError('invalid value')

    def cmd_status(self):
        """Get the status of the pump."""
        query, reply = self.control_interface.get_status()

        descriptions = (member.description for member in reply.flag_bits)        
        lines = (self.indent + s for s in descriptions)
        
        if lines:
            condition_str = 'Active status conditions:\n' + '\n'.join(lines)
        else:
            condition_str = 'No active status conditions'

        hardware_str = (
            f'Frequency: {reply.frequency} Hz\n'
            f'Temperature: {reply.temperature} °C\n'
            f'Current: {0.1 * reply.current:.1f} A\n'
            f'Voltage: {reply.voltage} V'
        )
        
        string = textwrap.indent(condition_str + '\n' + hardware_str,
                                 self.indent)
        
        self.print('Pump status:\n' + string)
        return query, reply

    def cmd_reset(self):
        """Reset the error status of the pump."""
        self.print('Resetting error status')
        return self.control_interface.get_status()

    def cmd_read(self, number, index=0):
        """Return the value of parameter *number*, index *index*."""        
        query, reply = self.control_interface.read_parameter(number, index)

        self._print_parameter_output(reply)
        return query, reply

    def cmd_write(self, number, value, index=0):
        """Write *value* to parameter *number*, index *index*."""        
        query, reply = self.control_interface.write_parameter(
            number, value, index)
        
        self._print_parameter_output(reply)
        return query, reply
    
    def _print_parameter_output(self, reply):
        """Format and print out the parameter information in *reply*."""
        
        error = reply.parameter_error
        if error is not None:
            self.print(f'Error: {error.description}')
            return
        
        # Truncate long floats.
        if isinstance(reply.parameter_value, float):
            value_str = f'{reply.parameter_value:.2f}'
        else:
            value_str = str(reply.parameter_value)
            
        self.print(
            f'The value of parameter {reply.parameter_number}, '
            f'index {reply.parameter_index} is {value_str}'
        )

    def cmd_info(self, letter, numbers):
        """Display information about parameters, errors, or warnings.
        
        *letter* should be 'p', 'e', or 'w' depending on whether *numbers*
        refer to parameters, errors, or warnings.
        
        *numbers* should be a list or a tuple of the numbers of those
        parameters/errors/warnings that should be displayed. It can also be a
        single number or 'all', if only a single parameter/error/warning or all
        of them should be listed. 
        """        
        try:
            dict_ = self._dicts[letter]
        except KeyError:
            raise ValueError(f'invalid *letter*: {repr(letter)}')

        # If *numbers* is a single number, convert it into a list.
        if isinstance(numbers, int):
            numbers = [numbers]
        
        self.print(table(dict_, numbers, self._widths[letter]))
        
    def cmd_help(self, value=None):
        """Display a help message.

        *value* should be the name or an alias of the command that
        should be described.
        If no *value* is specified, all commands are listed and
        described.
        """
        if value:
            string = self._helpstring(value)
        else:
            descriptions = []
            for name, _ in self.cmds_and_aliases:
                descriptions.append(self._helpstring(name))
            description_str = '\n\n'.join(descriptions)
            string = ('Valid commands:\n'
                      + textwrap.indent(description_str, self.indent))

        self.print(string)

    def cmd_docs(self):
        """Open TurboCtl documentation in a web browser."""
        webbrowser.open(DOCS_URL)

    def _helpstring(self, cmdname):
        """Return a help message describing the usage of *cmdname*."""
        method = self._get_method(cmdname)
        argstr = self._argstring(method)
        aliasstr = self._alias_string(cmdname)
        docstr = inspect.getdoc(method)
        if docstr is None:
            docstr = ''

        return (f'{cmdname} {argstr}\n'
                + textwrap.indent(docstr, self.indent)
                + ('\n\n' + textwrap.indent(aliasstr, self.indent) if aliasstr
                   else '')
                )

    def cmd_exit(self):
        """Exit the UI."""
        self._stop_flag = True

    def cmd_debug(self, value):
        """Activate or deactivate the debug mode.

        Values of '1', 'True' and 'on' activate the debug mode;
        '0', 'False' and 'off' deactivate it.

        In normal operation, TypeErrors and ValueErrors
        raised during the execution of commands are caught to prevent
        users from crashing the program with invalid commands.
        Activating the debug mode disables this error-catching in order
        to make debugging easier.
        """
        # 1 == True and 0 == False.
        if value in [True, 'on']:
            self.debug = True
            self.print('Debug mode activated')

        elif value in [False, 'off']:
            self.debug = False
            self.print('Debug mode deactivated')

        else:
            raise ValueError('invalid value')
            
    def cmd_verbose(self, value):
        """Activate or deactivate the verbose mode.

        Values of '1', 'True' and 'on' activate the verbose mode;
        '0', 'False' and 'off' deactivate it.

        When the verbose mode is on, commands that send telegrams to the pump
        will print all the contents of the telegram and the reply to the
        screen.
        """
        # 1 == True and 0 == False.
        if value in [True, 'on']:
            self.verbose = True
            self.print('Verbose mode activated')

        elif value in [False, 'off']:
            self.verbose = False
            self.print('Verbose mode deactivated')

        else:
            raise ValueError('invalid value')
            
    def input(self, prompt=''):
        """Ask the user for input.

        This method works like the built-in :func:`.input` function,
        but uses :attr:`inputfile` and :attr:`outputfile` instead of
        :data:`sys.stdin` and :data:`sys.stdout`.

        The line editing functionality provided by the :mod:`readline`
        module works with this method only if :attr:`inputfile` is
        :data:`sys.stdin`.
        """
        # `.input` instead of `input` makes Sphinx refer to the
        # built-in input function instead of this method.

        if self.inputfile == sys.stdin:
            return input(prompt)

        self.print(prompt, end='')
        string = self.inputfile.readline()

        if string[-1] == '\n':
            return string[:-1]

        return string

    def print(self, *objects, sep=' ', end='\n'):
        """Print text to the UI.

        This method works like the built-in :func:`.print` function,
        but uses :attr:`inputfile` and :attr:`outputfile` instead of
        :data:`sys.stdin` and :data:`sys.stdout`, and doesn't include
        the *file* and *flush* arguments.
        """
        print(*objects, file=self.outputfile, sep=sep, end=end, flush=True)

    def _run_command(self, line):
        """Parse *line* and run it as a command.

        Returns:
            True if the main loop should be broken, otherwise
            False.
        """
        # Separate the command and its arguments.
        # split() splits at any whitespace character
        # and discards empty strings.
        parts = line.split()
        try:
            cmdname = parts[0]
        except IndexError:
            # Skip empty lines.
            return False
        args = parts[1:]

        # Get the method.
        try:
            method = self._get_method(cmdname)
        except ValueError as error:
            self.print(f'Error: {error}')
            return False

        # Parse the arguments into appropriate Python objects.
        # Arguments that cannot be parsed into any other type are kept
        # as strings.
        for i, arg in enumerate(args):
            try:
                args[i] = ast.literal_eval(arg)
            except (ValueError, SyntaxError):
                pass

        # Call the method.
        try:
            out = method(*args)
            # If the verbose mode is on, print the contents of every telegram
            # that is sent or received.
            # For methods that don't send telegrams, *out* will be None.
            if out and self.verbose:
                self.print('\n' + self._verbose_string(*out))
                
        except (ValueError, TypeError) as error:

            # Suppress errors, unless the debig mode is on.
            if self.debug:
                raise error

            if isinstance(error, ValueError):
                # ValueErrors should contain a meaningful explanation string,
                # so they can be displayed to the user.
                self.print(f'Error: {error}')
            else:
                # TypeErrors will count the number of arguments wrong (since
                # they also count the *self* argument), and other types of
                # errors shouldn't be raised during normal operation, so those
                # aren't displayed to the user.
                self.print('Error: invalid argument type or number of '
                           'arguments')
                
    def _verbose_string(self, query, reply):
        """Return a string displaying the contents of both the query and the
        reply.
        """        
        return (
            'Sent a telegram with the following contents:\n'
            + textwrap.indent(str(query), self.indent) + '\n'
            + '\n'
            + 'Received a telegram with the following contents:\n'
            + textwrap.indent(str(reply), self.indent)
        )

    def _get_method(self, command):
        """Return the method corresponding to *command* (a str)."""

        names = [command] + self._get_aliases(command)
        for name in names:
            try:
                return getattr(self, 'cmd_' + name)
            except AttributeError:
                pass

        raise ValueError(f'invalid command: {command}')

    def _get_aliases(self, command):
        """Return a list of aliases for *command*.

        *command* itself is never part of the list, but if *command*
        is itself an alias, the primary name of the command will be
        included in the list.
        """
        for cmd, aliases in self.cmds_and_aliases:
            names = [cmd] + aliases
            if command in names:
                names.remove(command)
                return names

        raise ValueError(f'invalid command: {command}')

    def _alias_string(self, command):
        """Return a formatted string that lists the aliases of
        "*command*.

        Returns:
            A string with the format 'Aliases: a, b, c',
            or '' if there are no aliases.
        """
        aliases = self._get_aliases(command)
        if aliases:
            return 'Aliases: ' + ', '.join(aliases)
        return ''

    @staticmethod
    def _argstring(method):
        """Return a formatted string that lists the arguments of
        *command*.

        Format: '<arg1> [optional_arg2=default]'
        """
        argspec = inspect.getfullargspec(method)
        args = argspec.args[1:]  # Ignore *self*.
        defaults = argspec.defaults  # Default values for arguments.
        if defaults is None:
            defaults = []

        reversed_args = args[::-1]
        reversed_defaults = defaults[::-1]
        reversed_argstrings = [None] * len(args)

        # The lists are reversed, so that arguments with default
        # values are iterated first.
        # Arguments without default values are iterated afterwards,
        # when *reversed_defaults* has run out of indices.
        for i, arg in enumerate(reversed_args):
            try:
                default = reversed_defaults[i]
                reversed_argstrings[i] = f'[{arg}={default}]'
            except IndexError:
                reversed_argstrings[i] = f'<{arg}>'

        return ' '.join(reversed_argstrings[::-1])
