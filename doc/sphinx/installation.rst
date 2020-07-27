Installation
============

.. _dependencies:

Dependencies
------------

TurboCtl was written and tested in Python 3.7.7, so that or another relatively
new Python version should be installed.
It is intended to be used on a Linux operating system, and probably won't work
on other systems such as Windows without some tweaks. 

In addition to the Python standard library, TurboCtl uses the following
external libraries:

    - pySerial_ (tested with version 3.4)
    - tabulate_ (tested with version 0.8.3)
    - urwid_ (tested with version 2.0.1).
    
TurboCtl can also run without urwid by using an alternative user interface
(see :doc:`usage` for details).


The TurboCtl directory
----------------------

TurboCtl doesn't include an installation script; simply download the
``TurboCtl`` directory to a location of your choosing.
In order to access the ``turboctl`` package and the ``turboctl-run`` script,
the ``TurboCtl`` directory  should be added to ``$PYTHONPATH`` and ``$PATH``
or made the working directory.

.. _pySerial: https://pypi.org/project/pyserial/
.. _tabulate: https://pypi.org/project/tabulate/
.. _urwid: http://urwid.org/
