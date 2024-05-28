Installation
============

Installation with pip
---------------------

TurboCtl is available on PyPI_ and can be installed with the command

::

    pip install 'turboctl[urwid]'

This installs TurboCtl with a fancier UI that uses Urwid_.

Running

::

    pip install turboctl

performs a minimal installation of TurboCtl without Urwid.
If you use this option, you can only run TurboCtl with the :option:`-s` flag (see :doc:`usage` for details).

In order to run the automatic tests included in TurboCtl (the :option:`-t` flag), you also need the Hypothesis_ library, which can be included in the installation with 

::

    pip install 'turboctl[tests]'

or

::

    pip install 'turboctl[tests,urwid]'

depending on whether you want to also include Urwid or not.


Installation from GitHub
------------------------

You can also download TurboCtl directly from GitHub_, but you'll need to manually install its dependencies.
See the ``pyproject.toml`` file in the ``TurboCtl`` directory for a list of them.


The ``dialout`` group
---------------------

In order to form a serial connection, the user running TurboCtl needs to be
part of the ``dialout`` group. If they aren't already, they can be added with
the command

::

    sudo adduser <username> dialout


.. _Urwid: http://urwid.org/
.. _Hypothesis: https://hypothesis.readthedocs.io/en/latest/
