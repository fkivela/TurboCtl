"""This module handles the simulation of the serial connection in a
:class:~`turboctl.virtualpump.virtualpump.VirtualPump`.
"""

import os
import pty
import select
import threading
import time


class VirtualConnection():
    """A virtual serial connection.

    Data can be sent through a :class:`VirtualConnection` object by
    accessing the :attr:`user_end` and :attr:`virtual_end` attributes.
    The :attr:`port` property is a device name which can be given to
    the initializer of :class:`serial.Serial` as an argument.

    A :class:`VirtualConnection` object runs code in a parallel thread,
    which will continue running until it is closed or the Python
    interpreter exits.
    A parallel thread can be closed by calling the :func:`close`
    method of the :class:`VirtualConnection` object that created it.
    This also closes :attr:`user_end` and :attr:`virtual_end`,
    and frees their file descriptors.

    If a :class:`VirtualConnection` object is used in a ``with``
    block in the following manner:

    ::

        with VirtualConnection() as vc:
            # Some code here

    :meth:`close` will be called automatically when the ``with`` block
    is exited.

    If all variables referring to a :class:`VirtualConnection`
    object are removed with ``del`` or by reassigning them,
    the parallel thread will continue to run without a possibility of
    closing it with :meth:`close`.
    In this case, all running instances of the
    :class:`VirtualConnection` class can be closed with

    >>> VirtualConnection.close_all()

    Attributes:
        buffer_size (int):
            The buffer size for the connection
            (how many bits are read at once).

        sleep_time (float):
            How long (in seconds) the object waits after checking for
            input before doing it again.

        process (function):
            The method used for processing input and forming output.
            Its signature should be
            ::

                process(self, input_: bytes) -> output: bytes

            A machine or other device that communicates with its user
            can be simulated by assigning a suitable method to the
            :attr:`process` attribute.

        virtual_end (file-like object):
             This end of the connection is used by :meth:`process` to
             read and write data. It can be written to and read from
             with :func:`os.read` and :func:`os.write`.

        user_end (file-like object):
            This end of the connection is meant to be used by a user to
            send commands to and read data from a simulated device.
            :func:`os.read` doesn't seem to work with it,
            and the `serial <https://pypi.org/project/pyserial/>`_
            module should be used instead.

        thread (:class:`threading.Thread`):
            The parallel thread that runs most functionality in a
            :class:`VirtualConnection` object.

        running_instances:
            Class attribute.
            A set of all currently running instances of the
            :class:`VirtualConnection` class.
    """

    # Keep references to all running instances of this class.
    running_instances = set()

    def __init__(self, process=None, buffer_size=1024, sleep_time=0.01):
        """Initialize a new :class:`VirtualConnection`.

        The new instance starts the parallel thread automatically.

        Args:
            process (function):
                The function assigned to the :attr:`process` attribute.
                If no value is supplied, the :attr:`default_process`
                method will be used instead.

            buffer_size:
                The value of :attr:`buffer_size`.

            sleep_time:
                The value of :attr:`sleep_time`.
        """
        if process:
            self.process = process
        else:
            self.process = self.default_process

        self.buffer_size = buffer_size
        self.sleep_time = sleep_time

        master, slave = pty.openpty()
        # This may be written to and read from with os.write
        # and os.read.
        self.virtual_end = master
        # os.read doesn't seem to work with this, but the serial
        # module does.
        self.user_end = slave

        # A parallel thread for the function self._run().
        self.thread = threading.Thread(target=self._run, args=[])
        # Daemon threads are killed when there are no more non-daemon
        # threads left. Setting daemon to True prevents the parallel
        # thread from running in the background even after the main
        # program has exited.
        self.thread.daemon = True

        # Flag for stopping the parallel thread.
        self._stop_flag = threading.Event()
        # Add this instance to the set.
        self.running_instances.add(self)
        self.thread.start()

    def __enter__(self):
        """Called at the beginning of a ``with`` block; returns
        *self*.
        """
        return self

    def __exit__(self, type_, value, traceback):
        """Called upon exiting a ``with`` block; calls
        :meth:`close`.
        """
        self.close()

    def close(self):
        """Stop the parallel thread and close the connection.

        This function returns only after the parallel thread has
        actually stopped.
        """
        if self.is_running():
            self._stop_flag.set()

        # Wait for the parallel thread to stop.
        while self.is_running():
            time.sleep(self.sleep_time)

        # Unlike set.remove(x), set.discard(x) doesn't raise an error
        # if there is no x in the set.
        self.running_instances.discard(self)

    @classmethod
    def close_all(cls):
        """Close all running instances of this class.

        This function returns only after all parallel threads have
        actually stopped.
        """
        # Iterate over a copy, because closing a VC removes it from
        # cls.running_instances, and removing members from a set
        # during iteration raises an error.
        copy = cls.running_instances.copy()
        for i in copy:
            i.close()

    def is_running(self):
        """Return ``True`` if the parallel thread is running,
        ``False`` otherwise."""
        return self.thread.is_alive()

    @property
    def port(self):
        """Return a device name (e.g. ``'/dev/pts/...'``) that can be
        used as the *port* argument when a :class:`serial.Serial`
        object is created."""
        return os.ttyname(self.user_end)

    def _run(self):
        """Run the parallel thread."""

        while not self._stop_flag.is_set():
            # If there is nothing to read from self.virtual_end,
            # os.read will block forever even with a timeout.
            # select makes sure this doesn't happen.
            ready_for_read, _, _ = select.select([self.virtual_end], [], [], 0)

            if self.virtual_end in ready_for_read:
                input_ = os.read(self.virtual_end, self.buffer_size)
            else:
                time.sleep(self.sleep_time)
                continue

            output = self.process(input_)
            os.write(self.virtual_end, output)

        # Close the files after the parallel thread has stopped.
        # Otherwise the system will run out of file descriptors,
        # if a VirtualConnection is created and stopped many times
        # in a a row.
        os.close(self.user_end)
        os.close(self.virtual_end)

    @staticmethod
    def default_process(input_):
        """Form output based on *input_*.

        This is the default method assigned to :attr:`process`,
        and simply returns *input_* uncanged.

        Args:
            input_: A bytes-like object.

        Returns:
            *input_*.
        """

        output = input_
        return output
