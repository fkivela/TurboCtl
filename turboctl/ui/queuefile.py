"""This module defines the :class:`QueueFile` class."""

import queue
import io
import itertools


class QueueFile:
    """This class wraps a :class:`queue.Queue` object in the interface
    of a file-like object.

    The :class:`QueueFile` class makes redirecting input and output
    between different parts of a program easier than it would be using
    standard file objects, such as :class:`io.StringIO` or those
    created by :func:`pty.openpty`.
    :class:`QueueFile` is thread-safe, can be read from and written to
    at the same time, and its blocking behaviour can be easily
    controlled.
    (If there is nothing to read, reading from :class:`io.StringIO`
    never blocks, but reading from an object created with
    :func:`pty.openpty` always does.)

    Attributes:
        queue (queue.Queue):
            The wrapped :class:`~queue.Queue` object.
            Strings are saved in the queue one character at a time.

        block (bool):
            A flag indicating whether :meth:`read` and
            :meth:`readline` should block or not.
    """

    def __init__(self, block=False):
        """Intialize a new :class:`QueueFile` with :attr:`block` set
        to the value given as an argument.
        """
        self.queue = queue.Queue()
        self.block = block

    def write(self, string):
        """Write *string* to the queue and return the number of
        characters written.

        This method emulates :meth:`io.TextIOBase.write`.
        """
        # io.TextIOBase.write() doesn't accept keyword arguments,
        # so we can safely change the argument name from *s* to
        # *string* without breaking anything.
        for char in string:
            self.queue.put(char)
        return len(string)

    def read(self, size=-1):
        """Read and return a string of *size* characters from the queue.

        If the queue contains less than *size* characters or *size* is
        ``None`` or less than ``1``, all characters in the queue are
        read.

        This method emulates :meth:`io.TextIOBase.read`.
        """
        return self._read(size)

    def readline(self, size=-1):
        """Like :meth:`read`, but reading characters is stopped if a
        newline character is encountered. If this happens, the string
        returned includes that newline character.

        This method emulates :meth:`io.TextIOBase.readline`.
        """
        return self._read(size, endchar='\n')

    def _read(self, size=-1, endchar=None):
        """This method provides the functionality shared by
        read() and readline().
        """
        buffer = io.StringIO()

        if not size or size < 0:
            # An infinite generator that yields 0,1,2,...
            iterations = itertools.count()
        else:
            iterations = range(size)

        # Read a finite or an infinite number of characters.
        for _ in iterations:
            try:
                char = self.queue.get(block=self.block)
                buffer.write(char)
            except queue.Empty:
                break

            if endchar and char == endchar:
                break

        return buffer.getvalue()

    def flush(self):
        """This method does nothing, but its existence makes it
        possible to :func:`print` to this object with ``flush=True``
        without raising an :class:`AttributeError`."""