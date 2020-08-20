Usage
=====

Running the program
-------------------

The TurboCtl program is run via the ``__main__.py`` script inside the
``turboctl`` package. This is done with the command

::

    $ python path/to/turboctl -args

This only works if the ``python`` command is set to run a Python version that
TurboCtl is compatible with; i.e. Python 3.7 or newer. If this is not the case,
substitute ``python`` for a command that runs a compatible version of Python,
e.g. ``python3`` or ``python3.7``.        

Because this command requires providing the relative or absolute path of the
``turboctl`` package every time it is used, TurboCtl also provides a shell
script which automatically fills in the path before calling the command.
If the ``TurboCtl`` directory has been added to ``$PATH``, the shell script
can be run from any directory with

::

    $ turboctl-run -args
    
The script uses the ``/usr/bin/env python3`` command to run the program. If
the ``python3`` command is set to use an older Python 3 version that isn't
compatible with TurboCtl, the script should be edited to use a specific newer
version (e.g. ``python3.7``) instead. The script is located in
``TurboCtl/turboctl-run``.

Both of these commands accept the following command-line arguments:

-h, --help          Show a help message that lists all command-line arguments.

-p, --port port     Define the port used for the serial connection.
                    If this argument isn't supplied, the default port
                    ``/dev/ttyUSB0`` will be used. 

-v, --virtual       Run HVCtl with a virtual pump. 
                    If this argument is supplied, instead of sending messages
                    to a real pump, TurboCtl creates a simulated, virtual one
                    and sends messages to that.
                    This makes it possible to test TurboCtl easily without
                    having to connect to a real pump.     
                    This option is incompatible with ``-p``.

-s, --simple        Run TurboCtl with a simple command-line interface that
                    doesn't require :ref:`urwid <dependencies>`.
                    If TurboCtl is run without the ``-s`` argument, a more
                    advanced UI will be used (see below for an example).

-t, --test          Instead of running the TurboCtl program, run all automatic
                    tests for it.
                   


                    
.. The user interface
.. ------------------

.. <screen + command-line, or just copmmand-line is -s was used.>
.. <commands are given by writing the command + args just like real command line
.. output is the printed>
.. <values are parsed with ast-literal eval -> python syntax but no spaces, no complex objects>
.. <the commands are the following>
.. <advanced ui polls, less advanced doesn't>

.. <list here>
.. <note about errors: invalid args raise errors which are suppressed. However,
.. some genuine bugs may do so too. In that case, run the debid command to see the
.. error string. Also, Turboctl ui hasn't been tested yet very well and may be
.. buggy. In that case, simply run turboctl again, it should function then.>

.. <a bit about the api>






