"""Write README.rst with and without Sphinx extensions."""
import turboctl


# This is the main text of the readme file.
# The documentation section as well as the current version and copyright
# information need to be filled in.
body = """TurboCtl
========

TurboCtl is a RS-232 controller for a Leybold TURBOVAC i or iX turbovacuum
pump. It was written in Python 3 and is intended for Linux operating systems.

Documentation
-------------

{documentation}

Author
------

TurboCtl was written by Feliks Kivelä.
The author can be contacted at firstname.lastname@aalto.fi
(with the "ä" replaced by an "a").

Copyright © {project_copyright}.

Version
-------

This is version {version} of TurboCtl.

License
-------

TurboCtl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.
"""


# This version displays correctly in GitHub and PyPI, which don't support
# Sphinx.
raw_rst_docs = """TurboCtl includes HTML documentation generated with Sphinx.
You can view the documentation in a correctly rendered form `here <https://html-preview.github.io/?url=https://github.com/fkivela/TurboCtl/blob/master/doc/sphinx/_build/html/index.html>`_ or by downloading TurboCtl and opening ``README.html`` in a browser."""


# This version is used for the index page of the HTML docs.
sphinx_docs = """.. toctree::
   
   installation.rst
   usage.rst
   modules.rst
   errata.rst"""


# Write the readme file.
with open('README.rst', 'w') as file:
    file.write(body.format(documentation=raw_rst_docs,
                           project_copyright=turboctl.copyright,
                           version=turboctl.__version__))


# Write the HTML docs index.
with open('doc/sphinx/index.rst', 'w') as file:
    file.write(body.format(documentation=sphinx_docs,
                           project_copyright=turboctl.copyright,
                           version=turboctl.__version__))