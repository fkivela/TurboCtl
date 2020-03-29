"""This module defines the singledispatchmethod decorator.

The functools.singledispatchmethod decorator is included in Python 3.8,
but not in 3.7.
Because the support for 3.8 is not yet very widespread,
TurboCtl still uses 3.7.
When TurboCtl is updated to Python 3.8, this module will be
removed. 
"""
from functools import singledispatch, update_wrapper

# This was copied from StackOverflow and slightly altered.
def singledispatchmethod(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kwargs):
        try:
            return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)
        except IndexError:
            raise TypeError('at least 1 positional argument is required')
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

