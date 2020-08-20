"""This is the main script used to run TurboCtl."""

import argparse
import sys

from turboctl.ui import status_format
from turboctl.ui.command_line_ui import CommandLineUI
from turboctl.ui.queuefile import QueueFile
from turboctl.virtualpump.virtualpump import VirtualPump
from test_turboctl.run_tests.run_tests import run_tests


### Command-line arguments ###

# The argparse module hepls with parsing command line arguments.
# The -h option displays an automatically generated help message.
parser = argparse.ArgumentParser(description='This script runs TurboCtrl')

# TurbCtl can be run in three modes: run tests (-t), run without urwid
# (-s) or run with the regular UI (no letter).
mode_group = parser.add_mutually_exclusive_group()
mode_group.add_argument('-t', '--test', help='run tests', action='store_true')
mode_group.add_argument('-s', '--simple',
                        help="use a UI that doesn't require urwid", 
                        action='store_true')
mode_group.add_argument('-n', '--no-poll',
                        help=('do not poll the status of the pump by sending '
                              'automatic telegrams'), 
                        action='store_true')


# Regardless of mode, TurboCtl can be run with a virtual pump (-v) 
# or with a real pump (-p and port name). These options don't matter when
# running tests. 
vpump_group = parser.add_mutually_exclusive_group()
vpump_group.add_argument('-v', '--virtual', help='use a virtual pump',
                         action='store_true')
vpump_group.add_argument('-p', '--port', 
                         help='the address of the serial port device')

args = parser.parse_args()


### The main part of the script ###

def main():
    """Execute the script."""
    
    if args.test:
        run_tests()
        return
    
    try:
        # If virtualpump was defined in another function
        # and an error occurred between its creation and the
        # 'return virtualpump' statement,
        # the finally block wouldn't work, because 'virtualpump' wouldn't
        # be included in the namespace of main().
        # This also holds for command_line_ui. Because of this,
        # both objects are defined directly in main().
        virtualpump = VirtualPump() if args.virtual else None
        port = get_port(virtualpump)

        # Automatically poll the pump only if the advanced UI is used,
        # since the simple UI doesn't contain a screen to display the changing
        # status.
        autoupdate = not (args.simple or args.no_poll)
        inputfile, outputfile = get_io_files()
        command_line_ui = CommandLineUI(port, autoupdate,
                                        inputfile, outputfile)
        ui = get_ui(command_line_ui)
        ui.run()
    finally:
        # Make sure all parallel threads are closed, even if the program
        # crashes. Otherwise the terminal may be left in a weird unresponsive
        # state.

        try:
            # This raises a NameError if the script raises an error
            # before command_line_ui is defined.
            command_line_ui.control_interface.close()
        except NameError:
            pass

        try:
            # An AttributeError is raised if virtualhv is None.
            virtualpump.connection.close()
        except AttributeError:
            pass


def get_port(virtualpump):
    """Return the port used for the serial connection.

    If a virtual pump isn't used, the *virtualpump* argument is ignored.
    """
    if args.virtual:
        return virtualpump.connection.port
    if args.port:
        return args.port
    # Use the default value.
    return None


def get_io_files():
    """Return the input and output files for the UI.

    Returns:
        (inputfile, outpufile)
    """
    if args.simple:
        inputfile = sys.stdin
        outputfile = sys.stdout
    else:
        inputfile = QueueFile(block=True)
        outputfile = QueueFile()

    return inputfile, outputfile


def get_ui(command_line_ui):
    """Return *command_line_ui* or an AdvancedUI object that uses
    *command_line_ui*.
    """
    if args.simple:
        ui = command_line_ui
    else:
        # Because AdvancedTUI imports urwid, it is imported only if
        # it is needed.
        # This makes it possible to run HVCtl without urwid by using
        # CommandLineUI.

        from turboctl.ui.advanced_tui import AdvancedTUI

        advanced_ui = AdvancedTUI(command_line_ui.run,
                                  command_line_ui.inputfile,
                                  command_line_ui.outputfile,
                                  status_format.palette)

        # Show the status of the HV generator in the UI.
        def callback(status):
            text = status_format.status_screen(status)
            advanced_ui.display.set_text(text)
        command_line_ui.control_interface.status.callback = callback
        ui = advanced_ui

    return ui


main()