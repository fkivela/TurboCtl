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
grey_button = ('grey', '⏺')


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
    match status.pump_on:
        case None:
            onoff_str = 'Pump status unknown'
            button = grey_button
        case True:
            onoff_str = 'Pump on'
            button = green_button
        case False:
            onoff_str = 'Pump off'
            button = red_button
        case _:
            raise ValueError(
                f'status.pump_on should be None, True or False, '
                f'was {status.pump_on}')

    if status.status_bits is None:
        lines = None
    else:
        descriptions = (member.description for member in status.status_bits)        
        lines = ('    ' + s for s in descriptions)

    match lines:
        case None:
            condition_str = 'Status conditions unknown'
        case []:
            condition_str = 'No active status conditions'
        case _:
            condition_str = 'Active status conditions:\n' + '\n'.join(lines)        

    def format_float(x, unit, format_str='{}'):
        if x is None:
            return 'unknown'
        return f'{format_str.format(x)} {unit}'

    hardware_str = (
        'Frequency: ' + format_float(status.frequency, 'Hz') + '\n'
        'Temperature: ' + format_float(status.temperature, '°C') + '\n'
        'Current: ' + format_float(status.current, 'A', '{:.1f}') + '\n'
        'Voltage: ' + format_float(status.voltage, 'V')
    )

    text = ([
        onoff_str, ' ', button, '\n',
        condition_str, '\n',
        hardware_str
    ])
    return text