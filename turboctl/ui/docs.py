"""Functionality for opening TurboCtl docs in a browser."""
import webbrowser


def docs():
    """Open TurboCtl documentation in a browser."""
    url = 'https://turboctl.readthedocs.io/en/latest/index.html'
    webbrowser.open(url, new=2)
