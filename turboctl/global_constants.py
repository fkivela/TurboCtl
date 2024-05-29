"""String constants used throughout the TurboCtl project.

This module defines a place where string constants such as URLs can be defined
and changed without having to go through multiple files to manually change the
values in each of them.

In addition to the :ref:`turboctl` Python module, these constants are used by
the Sphinx documentation and scripts at the top level of the project.
"""
from datetime import date


TESTPYPI_URL = 'https://test.pypi.org/project/turboctl/'
"""The URL of the TurboCtl project on TestPyPI."""

PYPI_URL = 'https://pypi.org/project/turboctl/'
"""The URL of the TurboCtl project on PyPI."""

GITHUB_URL = 'https://github.com/fkivela/TurboCtl'
"""The URL of the TurboCtl repository on GitHub."""

DOCS_URL = 'https://turboctl.readthedocs.io/en/latest/index.html'
"""The URL of TurboCtl documentation on Read the Docs."""

AUTHOR = 'Feliks Kivelä'
"""The author of the TurboCtl project."""

EMAIL = 'firstname.lastname@aalto.fi'
"""The email of the TurboCtl author.

This uses the firstname.lastname format in order to provide some degree of
protection against email scrapers.
"""

COPYRIGHT = f'2019-{date.today().year} University of Helsinki Fusor Team'
"""Copyright information with an automatically updating year."""

VERSION = '1.1.1'
"""The current version of the TurboCtl project."""

SPHINX_PATH = 'doc/sphinx'
"""The path to the Sphinx documentation directory, relative to the top-level
TurboCtl directory.
"""
# This has changed a few times and may change in the future so it's a good idea
# to make it a variable.

REVERSE_SPHINX_PATH = '../..'
"""The path to the top-level TurboCtl directory, relative to the Sphinx
documentation directory.
"""


def main():
    """Write the constants defined in this module to a shell file."""
    attributes = dir()
    constants = [s for s in attributes if s[0] != '_' and s.isupper()]
    
    with open('global_constants.sh', 'w') as file:
        file.write('#!/usr/bin/env bash')
        file.write('# This file was automatically generated by '
                   'global_constants.py; see that for details.')
        for name in constants:
            value = locals()[name]
            file.write(f'{name}={value}')


if __name__ == '__main__':
    main()
