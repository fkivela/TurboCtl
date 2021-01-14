Installation
============

.. _dependencies:

Dependencies
------------

TurboCtl requires Python 3.8, and will not run on older Python versions
(it was tested with version 3.8.5).
It is intended to be used on a Linux operating system, and probably won't work
on other systems such as Windows without some tweaks. 

In addition to the Python standard library, TurboCtl uses the following
external libraries:

    - pySerial_ (tested with version 3.5)
    - tabulate_ (tested with version 0.8.7)
    - Urwid_ (tested with version 2.1.2).
    
TurboCtl can also run without Urwid by using an alternative user interface
(see :doc:`usage` for details).


The ``TurboCtl`` directory
--------------------------

TurboCtl doesn't include an installation script; simply download the
``TurboCtl`` directory to a location of your choosing.
In order to access the :doc:`modules/index` package and the ``turboctl-run``
script, the ``TurboCtl`` directory  should be added to ``$PYTHONPATH`` and
``$PATH`` or made the working directory.

.. _pySerial: https://pypi.org/project/pyserial/
.. _tabulate: https://pypi.org/project/tabulate/
.. _Urwid: http://urwid.org/


The ``dialout`` group
---------------------

In order to form a serial connection, the user running TurboCtl needs to be
part of the ``dialout`` group. If they aren't already, they can be added with
the command

::

    sudo adduser <username> dialout

