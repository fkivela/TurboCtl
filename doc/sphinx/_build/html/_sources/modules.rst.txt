Packages and modules
====================

The source code for TurboCtl is located in the :ref:`turboctl` package, which
has the following internal structure of subpackages and modules:

.. toctree::
   
   modules/index.rst

In addition to :ref:`turboctl`, TurboCtl also contains the ``test_turboctl``
package, which contains automatic tests for :ref:`turboctl`. The internal
structure of ``test_turboctl`` mirrors that of :ref:`turboctl`, and most
modules in :ref:`turboctl` have a corresponding test module
``test_<modulename>.py`` in ``test_turboctl``.
