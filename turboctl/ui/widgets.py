"""This module uses the `urwid <http://urwid.org/>`_ library to create
widgets (see :class:`urwid.Widget`) for a text-based user interface
containing a scrollable command line interface below a text screen.

The docstring of each widget defined here tells whether it is a box,
flow or fixed widget. The differences between these widget types are
explained `here <http://urwid.org/manual/widgets.html
#box-flow-and-fixed-widgets>`_.
"""

# pylint: disable=too-many-arguments
# Some urwid methods have many arguments.

# pylint: disable=unused-argument
# Subclasses can't safely change the signatures of methods inherited
# from a superclass.

# pylint: disable=protected-access
# urwid documentation suggests using the _invalidate method.

import urwid


class ScrollableCommandLines(urwid.WidgetWrap):
    """A widget consisting of a scrollable command line interface and
    a scroll bar with two arrow buttons for scrolling it.

    This is a box widget; its container sets it height and width.

    Attributes:
        position (:class:`Position`):
            Keeps track of how far the screen is scrolled.

        command_lines (:class:`CommandLines`):
            Provides the command line interface.

        scroller (:class:`Scroller`):
            Adds scrolling functionality to :attr:`command_lines`.

        scrollbar (:class:`ScrollBar`):
            The scroll bar.

        arrow_up (:class:`ScrollButton`):
            An arrow button that can be clicked to scroll the screen
            up.

        arrow_down (:class:`ScrollButton`):
            An arrow button that can be clicked to scroll the screen
            down.
    """

    def sizing(self):  # pylint: disable=empty-docstring
        """"""
        # By default, self.sizing() seems to return the sizing of
        # urwid.Columns, frozenset({'box', 'flow'}).
        # Overriding _sizing doesn't work, so this method has to be
        # defined.
        # The """""" docstring prevents this method from inheriting the
        # docstring of urwid.Widget.sizing.
        # Because the docstring is empty, this method isn't included in
        # the documentation.
        return {urwid.BOX}

    def __init__(self, inputfile, outputfile):
        """Initialize a new :class:`ScrollableCommandLines`.

        The arguments are passed to the initializer of
        :attr:`command_lines`.
        """
        self.position = Position()

        self.command_lines = CommandLines(inputfile, outputfile)
        self.scroller = Scroller(self.command_lines, self.position)
        self.scrollbar = ScrollBar(self.position)
        self.arrow_up = ScrollButton('▲', -1, self.position)
        self.arrow_down = ScrollButton('▼', +1, self.position)

        self.position.listeners = {self.command_lines, self.scrollbar}

        # (num, widget)-tuples are used to specify the height
        # (for Piles) or width (for Columns) of contained widgets.
        pile = urwid.Pile([(1, self.arrow_up), self.scrollbar,
                           (1, self.arrow_down)])
        super().__init__(urwid.Columns([self.scroller, (2, pile)]))


class CommandLines(urwid.WidgetWrap):
    """This widget provides a terminal-like command line interface.

    Entering commands scrolls the screen automatically so that the
    latest command is always visible on the screen, but the
    functionality to scroll up to view old commands is provided by the
    :class:`Scroller` class instead of this class.

    This is a flow widget; its container sets it height but not width.

    Attributes:
        inputfile (file-like object):
            Input entered into the command-line interface by the user
            is written to this object.

        outputfile (file-like object):
            The command-line interface reads its output from this
            object and prints it on the screen.

        history (:class:`CommandHistory`):
            This object stores previously given commands.

        edit (:class:`urwid.Edit`):
            This widget provides the functionality for displaying and
            editing text.
    """

    def __init__(self, inputfile, outputfile):
        """Initialize a new :class:`CommandLines` object.

        The arguments set the values of :attr:`inputfile` and
        :attr:`outputfile`.
        """
        self.inputfile = inputfile
        self.outputfile = outputfile
        self.history = CommandHistory()
        self.edit = urwid.Edit()
        super().__init__(self.edit)

    def move_cursor_to_end(self):
        """Move the cursor to the end of the editable string."""
        self.edit.set_edit_pos(len(self.edit.edit_text))

    def update(self):
        """Print the string returned by
        :attr:`outputfile.read() <outputfile>` to the screen.
        """
        string = self.outputfile.read()
        if string:
            self.edit.set_caption(self.edit.caption + string)

    def history_up(self):
        """Scroll command history up one step.

        Calling this function has approximately the same effect as
        pressing the up arrow button in a Linux terminal.
        """
        self.history.update_command(self.edit.edit_text)
        self.history.up()
        self.edit.set_edit_text(self.history.get_command())
        self.move_cursor_to_end()

    def history_down(self):
        """Scroll command history down one step.

        Calling this function has approximately the same effect as
        pressing the down arrow button in a Linux terminal.
        """
        self.history.update_command(self.edit.edit_text)
        self.history.down()
        self.edit.set_edit_text(self.history.get_command())
        self.move_cursor_to_end()

    def enter(self):
        """Enter the current editable string as a command."""
        command = self.edit.edit_text
        self.history.update_command(command)
        self.history.enter_command()
        self.inputfile.write(command + '\n')
        self.edit.set_caption(self.edit.caption + command + '\n')
        self.edit.set_edit_text('')

    def keypress(self, size, key):
        """Handle key presses.

        The up and down arrow keys are used to browse command history.
        Enter enters a command.

        Returns:
            ``None`` if the key press was handled by this widget,
            *key* if it was not.
        """
        if key == 'enter':
            self.enter()
            return None

        if key == 'up':
            self.history_up()
            return None

        if key == 'down':
            self.history_down()
            return None

        return super().keypress(size, key)


class CommandHistory:
    """A class to store command history.

    This class emulates the command history browsing behaviour of a
    typical Linux terminal.

    Attributes:
        history:
            A list of previously entered commands.
            Index 0 is set to ``None`` to give :attr:`history`
            and :attr:`temp_history` the same length.

        temp_history:
            The same as :attr:`history`, but includes the newest
            command (the one that is currently being written) at
            index 0.
            If any previously given commands are modified
            (through :meth:`update_command`), the modified versions
            are saved here, while :attr:`history` contains the
            original ones.

        index:
            The index of the currently selected command.
            ``0`` is the command currently being written;
            ``1`` is the previous one etc.
    """

    def __init__(self):
        """Initialize :attr:`history` to ``[]``,
        :attr:`temp_history` to ``[None]`` and
        :attr:`index` to ``0``.
        """
        self.history = [None]
        self.temp_history = ['']
        self.index = 0

    def up(self):  # pylint: disable=invalid-name
        """Increase :attr:`index` by 1 (i.e. select a command that is
        older than the current one).

        If the current command is the oldest one, nothing is done.
        """
        self.index += 1
        if self.index >= len(self.history):
            self.index = len(self.history) - 1

    def down(self):
        """Decrease :attr:`index` by 1 (i.e. select a command that is
        newer than the current one).

        If the current command is the newest one, nothing is done.
        """
        self.index -= 1
        if self.index < 0:
            self.index = 0

    def get_command(self):
        """Return the currently selected command as a string."""
        return self.temp_history[self.index]

    def update_command(self, string):
        """Change the currently selected command into *string*."""
        self.temp_history[self.index] = string

    def enter_command(self):
        """Enter the currently selected command.

        This saves the command into memory and  and resets
        :attr:`index` to 0. If the command was created by modifying a
        previous command, that command's history entry will be reset
        into its original form. If multiple identical commands are
        entered consecutively, only one is saved; empty commands
        are not saved at all.
        """
        # The command that was entered:
        entered_cmd = self.temp_history[self.index]
        # The command before that:
        try:
            previous_cmd = self.temp_history[self.index + 1]
        except IndexError:
            previous_cmd = None

        # If a previous command was modified and the entered, changes
        # to it in the command history are erased by copying the
        # original form from *history*.
        if self.index > 0:
            self.temp_history[self.index] = self.history[self.index]

        # Save the entered command to the command history.
        # However, don't save consecutive duplicates or empty commands.
        if entered_cmd not in (previous_cmd, ''):
            self.history.insert(1, entered_cmd)
            self.temp_history.insert(1, entered_cmd)

        # Add a new command to be edited; initially this is empty.
        self.history[0] = ''

        # Reset *index*.
        self.index = 0


class Scroller(urwid.WidgetWrap):
    """A container widget that makes a flow widget scrollable.

    This is a box widget; its container sets it height and width.

    Attributes:
        widget (urwid.Widget):
            The widget to be made scrollable. This should be a flow
            widget.

        position (:class:`Position`):
            An object to keep track of how far the widget is scrolled.
            The same :class:`Position` object should be shared among all
            objects that can scroll the widget (e.g. the scroll bar).
    """

    def __init__(self, widget, position):
        """Initialize a new :class:`Scroller`.

        The arguments set the values of :attr:`widget` and
        :attr:`position`.
        """
        self.widget = widget
        self.position = position
        super().__init__(urwid.Filler(self.widget))

    def render(self, size, focus=False):
        """Render the visible portion of the scrollable widget,
        update :attr:`position` and
        return an :class:`urwid.Canvas` object.
        """
        cols = size[0]
        # self.widget should be a float widget.
        canvas = self.widget.render((cols,), focus)
        # *canvas* has been finalized and can't be edited.
        new_canvas = urwid.CompositeCanvas(canvas)

        # How many rows should be rendered.
        given_rows = size[1]
        # How many rows tall self.widget is.
        canvas_rows = new_canvas.rows()

        # Update self.position
        self.position.visible_rows = given_rows
        self.position.total_rows = max(canvas_rows, given_rows)

        # Compute how many rows should be trimmed from the canvas
        # (or added to it as padding).
        total_trim = canvas_rows - given_rows
        top_trim = round(self.position.relative * total_trim)
        # A negative trim means padding, but padding should be added
        # to the bottom, so *top_trim* can never be negative
        if top_trim < 0:
            top_trim = 0

        # If *bottom_trim* is negative, the bottom is padded instead
        # of trimmed.
        bottom_trim = total_trim - top_trim

        # If the cursor is moved off the screen, it shouldn't be
        # displayed.
        if new_canvas.cursor:
            # canvas.cursor is None or (col, row).
            cursor_row = new_canvas.cursor[1]
            if cursor_row >= given_rows + top_trim:
                new_canvas.cursor = None

        # Negative arguments trim, positive arguments pad
        # -> trim amounts must be converted to negative values.
        new_canvas.pad_trim_top_bottom(-top_trim, -bottom_trim)
        return new_canvas

    def mouse_event(self, size, event, button, col, row, focus):
        """Handle mouse events.

        The mouse wheel scrolls the terminal up and down.

        Returns:
            ``True`` if the event was handled by this widget,
            ``False`` otherwise.
        """
        # Mouse wheel up
        if button == 4:
            self.position.absolute -= 1
            return True

        # Mouse wheel down
        if button == 5:
            self.position.absolute += 1
            return True

        return super().mouse_event(size, event, button, col, row, focus)

    def keypress(self, size, key):
        """Handle key presses.

        Pressing any key scrolls the terminal to the bottom so that
        the current command can be edited.

        Returns:
            ``None`` if the key press was handled by this widget,
            *key* if it was not.
        """
        self.position.relative = 1
        return super().keypress(size, key)


class Position:
    """A class to keep track of the position to which a widget made
    scrollable with :class:`Scroller` has been scrolled.

    Attributes:
        listeners (iterable):
            The widgets that should be re-rendered whenever
            :attr:`absolute` or :attr:`relative` is changed.

        total_rows (int):
            The height of the scrollable widget in rows,
            including those that are not currently visible on the
            screen.
            Empty rows are also included.
            The :class:`Scroller` widget should update this attribute
            whenever it is rendered.

        visible_rows (int):
            Like :attr:`total_rows`, but only counts the rows visible
            on the screen.

        relative (float):
            A relative scroll position between ``0`` (scrolled to the
            top) and ``1`` (scrolled to the bottom).
            Changing this also changes the value of :attr:`absolute`.
            Values below ``0`` are set to ``0`` and values above ``1``
            to ``1``.

        absolute (int):
            An absolute scroll position given as the number of
            invisible rows that are located above the top edge of the
            widget.
            Changing this also changes the value of :attr:`relative`.
            Values below ``0`` are set to ``0`` and values above
            :attr:`max_absolute` to :attr:`max_absolute`.
    """

    def __init__(self, listeners=None):
        """Initialize a new :class:`Position` object.

        Args:
            listeners (iterable):
                The initial value for :attr:`listeners`.
                This may be changed later. If no value is given,
                :attr:`listeners` is initialized to ``set()``.
        """
        if listeners is not None:
            self.listeners = listeners
        else:
            self.listeners = set()
        self.total_rows = 1
        self.visible_rows = 1
        self._relative = 0

    @property
    def max_absolute(self):
        """The maximum value of :attr:`absolute`, equal to
        ``total_rows - visible_rows``."""
        ret = self.total_rows - self.visible_rows
        if ret < 0:
            raise AssertionError(
                f'*total_rows* should always be >= *visible_rows*; '
                f'now they were {self.total_rows} and {self.visible_rows}.')
        return ret

    @property
    def relative(self):
        return self._relative

    @relative.setter
    def relative(self, value):
        if value < 0:
            value = 0

        if value > 1:
            value = 1

        self._relative = value
        for listener in self.listeners:
            listener._invalidate()

    @property
    def absolute(self):
        return round(self._relative * self.max_absolute)

    @absolute.setter
    def absolute(self, value):
        if value < 0:
            value = 0

        if value > self.max_absolute:
            value = self.max_absolute

        if self.max_absolute != 0:
            self._relative = value / self.max_absolute
        else:
            self._relative = 0

        for listener in self.listeners:
            listener._invalidate()


class ScrollBar(urwid.WidgetWrap):
    """A widget that provides a vertical scroll bar.

    This is a box widget; its container sets it height and width.

    Attributes:
        position (:class:`Position`):
            An object used to keep track of how far the screen is
            scrolled.

        scroller_char (single-character :class:`str`):
            The character used to draw the moving part of the scroll
            bar.

        background_char (single-character :class:`str`):
            The character used to draw the other parts of the scroll
            bar.
    """

    def __init__(self, position, scroller_char='█', background_char='░'):
        """Initialize a new scrollbar.

        The arguments set the values of :attr:`position`,
        :attr:`scroller_char` and :attr:`background_char`.
        """
        self.position = position
        self.scroller_char = scroller_char
        self.background_char = background_char
        # A filler must be used to make this a box widget.
        widget = urwid.Filler(urwid.Text(''))
        super().__init__(widget)

    def render(self, size, focus=False):
        """Generate the scroll bar and render it."""
        text = self._generate_text(size)
        self._w.original_widget.set_text(text)
        return super().render(size, focus)

    def _generate_text(self, size):
        """Generate the text displayed by *self.*

        Returns:
            A list of strings, each corresponding to a text row.
            The list has the dimensions indicated by *size*.
        """
        scroller_relative_size = (
            self.position.visible_rows / self.position.total_rows)

        if scroller_relative_size > 1:
            scroller_relative_size = 1

        ncols, nrows = size
        n_scroller_rows = round(nrows * scroller_relative_size)

        if n_scroller_rows < 1:
            n_scroller_rows = 1

        n_background_rows = nrows - n_scroller_rows
        n_background_rows_above = (
            round(self.position.relative * n_background_rows))
        n_background_rows_below = n_background_rows - n_background_rows_above

        basic_row = ncols * self.background_char
        scroller_row = ncols * self.scroller_char

        return (n_background_rows_above * [basic_row]
                + n_scroller_rows * [scroller_row]
                + n_background_rows_below * [basic_row])

    def mouse_event(self, size, event, button, col, row, focus):
        """Handle mouse events.

        Mouse button 1 moves the scroller so that clicking the scroll
        bar at a point *X* % from its top will set
        :attr:`position`:attr:`.relative <Position.relative>`
        to ``X / 100``.

        Returns:
            ``True`` if the event was handled by this widget,
            ``False`` otherwise.
        """
        if button == 1:
            nrows = size[1]  # size = (ncols, nrows)
            max_row = nrows - 1
            self.position.relative = row / (max_row)

        return True


class ScrollButton(urwid.WidgetWrap):
    """A widget that can be clicked with the mouse to scroll another
    widget.

    This is a box widget; its container sets it height and width.

    Attributes:
        step (int):
            The amount of rows scrolled when this widget is clicked.
            Negative values are used to scroll towards the top of the
            scrollable widget, positive values towards the bottom.

        position (:class:`Position`):
            An object used to keep track of how far the scrollable
            widget is scrolled.
    """

    def __init__(self, symbol, step, position):
        """Initialize a new :class:`ScrollButton`.

        Args:
            symbol (str):
                The character or string that is displayed on the
                button.

            step:
                The value of :attr:`step`.

            position:
                The value of :attr:`position`.
        """
        self.position = position
        self.step = step
        widget = urwid.Filler(urwid.Text(symbol))
        super().__init__(widget)

    def mouse_event(self, size, event, button, col, row, focus):
        """Handle mouse events.

        A left click scrolls the scrollable widget by :attr:`step`
        rows.

        Returns:
            ``True`` if the event was handled by this widget,
            ``False`` otherwise.
        """
        if button == 1:
            self.position.absolute += self.step

        return True