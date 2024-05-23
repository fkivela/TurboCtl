"""Functionality for opening TurboCtl docs in a browser."""
import webbrowser


URL = 'https://turboctl.readthedocs.io/en/latest/index.html'
"""The URL of TurboCtl documentation."""


def docs():
    """Open TurboCtl documentation in a web browser."""
    webbrowser.open(URL, new=2)
