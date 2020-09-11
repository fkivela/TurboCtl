"""This module controls how the status of the pump is presented to the user in
the UI.

Attributes:
    palette:
        A colour palette for an
        :class:`~turboctl.ui.advanced_tui.AdvancedTUI`.

    red_button:
        This is displayed by :class:`urwid.Text` widgets as a red
        circle, if the widgets are used in an
        :class:`~turboctl.ui.advanced_tui.AdvancedTUI`
        initialized with :attr:`palette`.

    green_button:
        Similar to :attr:`red_button`, but green instead of red.
"""

# (name, text color, background color)
palette = [('green', 'light green', ''),
           ('red', 'light red', '')]

red_button = ('red', '⏺')
green_button = ('green', '⏺')


def status_screen(status):
    """Return a status screen for the
    :attr:`display <turboctl.ui.advanced_tui.AdvancedTUI.display>`
    of an :class:`~turboctl.ui.advanced_tui.AdvancedTUI`.

    Args:
        status:
            A :class:`~turboctl.ui.control_interface.api.Status` object, the
            contents of which will be displayed on the screen.

    Returns:
        A nested iterable of strings, which will be interpreted by
        :class:`urwid.Text` as coloured text.
        The format is explained
        `here <http://urwid.org/manual/displayattributes.html
        ?highlight=display%20attributes#text-markup>`_.
    """    
    onoff_str = 'Pump ' + 'on' if status.pump_on else 'off'
    button = green_button if status.pump_on else red_button
    
    descriptions = (member.description for member in status.status_bits)        
    lines = ('    ' + s for s in descriptions)
        
    if lines:
        condition_str = 'Active status conditions:\n' + '\n'.join(lines)
    else:
        condition_str = 'No active status conditions'

    hardware_str = (
        f'Frequency: {status.frequency} Hz\n'
        f'Temperature: {status.temperature} °C\n'
        f'Current: {status.current:.1f} A\n'
        f'Voltage: {status.voltage:.1f} V'
    )
        
    text = ([
        onoff_str, ' ', button, '\n',
        condition_str, '\n',
        hardware_str
    ])
    return text
