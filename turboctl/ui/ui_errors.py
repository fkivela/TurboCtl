"""This module contains UI error classes to be used in a TUI."""

class UIError(Exception):
    """An abstract superclass for UI errors."""
    pass

class UITypeError(UIError):
    """An UI error raised when the argument of a function is of an 
    invalid type."""
    pass

class UIValueError(UIError):
    """An UI error raised when the argument of a function is of a 
    valid type but has an invalid value."""
    pass

class UIArgumentNumberError(UIError):
    """An UI error raised when a function is given a wrong number of 
    arguments.
    """
    pass

class UICommandError(UIError):
    """An UI error raised when the UI is given an invalid command."""
    pass

class UIParseError(UIError):
    """An UI error raised when a string containing a command and/or 
    its arguments cannot be parsed.
    """
    pass