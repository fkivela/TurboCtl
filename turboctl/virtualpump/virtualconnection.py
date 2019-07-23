"""This module defines the VirtualConnection class, which ca be used 
to simulate serial connections."""

import os
import threading
import select
import pty
import time
        
class VirtualConnection():
    """A virtual serial connection.
    
    A VirtualConnection object contains two attributes which can be 
    read from and written to.
    
    I/O to and from a machine or other non-user entity can be 
    simulated by reading from and writing to vc.virtual_end with 
    os.read and os.write.
    
    The entity using the machine should have access to vc.user_end.
    The user end can only be written to and read from with the serial 
    module; os.write and os.read don't work.
    
    vc.port returns a device name that can be given to serial.Serial 
    as an argument.
    
    The VirtualConnection object runs code in a parallel thread.
    If a VC is not closed after the it is no longer needed, 
    it may continue using resources needlessly.
    A VC may be closed with
    >> vc.close()
    This stops the parallel thread, closes vc.user_end and 
    vc.virtual_end, and frees their file descriptors.
    
    If a VC is used with a "with" block in the following manner:
    >> with VirtualConnection as vc:
    >>     # code here
    the VC will close automatically when the "with" block is exited.
    
    It is possible for a VC to continue running even if there 
    are no accessible references to it. 
    This happens e.g. if a VC is 
    defined in an IPython console and then deleted using "del vc".
    This deletes the name "vc", but doesn't seem to garbage-collect 
    the object.
    In this case, all running instances of the VirtualConnection class 
    can be closed with
    >> VirtualConnection.close_all()
    """
    
    # This flag can be used to stop all instances of this class at 
    # once without needing references to them.
    _stop_all_instances_flag = threading.Event()
        
    def __init__(self, buffer_size=1024):
        """Initialize a new VirtualConnection.
        
        The new instance starts running automatically.
        
        Args:
            buffer_size=1024: The buffer size for the connection 
                (how many bits are read at once).
        """
        
        self.buffer_size = buffer_size
        
        master, slave = pty.openpty()
        
        # This may be written to and read from with os.write 
        # and os.read.
        self.virtual_end = master
        
        # os.write and os.read don't work with this, but writing and 
        # reading with the serial module works.
        # TODO
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
        # Unset the global stop flag.
        self._stop_all_instances_flag.clear()
                
        self.thread.start()
        
    def __enter__(self):
        """Called at the beginning of a "with" block; returns 
        *self*.
        """
        return self
    
    def __exit__(self, type_, value, traceback):
        """Called at the end of a "with" block; stops the parallel 
        thread.
        """
        self.close()
        
    def close(self):
        """Stop the parallel thread and close the connection.
        
        This function only returns after the parallel thread has 
        actually stopped.
        """
        self._stop_flag.set()
        os.write(self.user_end, bytes([0]))
        while self.is_running():
            time.sleep(0.001)
        
    @classmethod
    def close_all(cls):
        """Close all running instances of this class.
        
        This function returns immediately after setting the stop flag, 
        so it may take a nonzero amount of time for the parallel 
        threads to finish executing after this function is called.
        """
        cls._stop_all_instances_flag.set()
        
    def is_running(self):
        """Return True, IFF the parallel thread is running."""
        return self.thread.is_alive()
        
    @property
    def port(self):
        """Returns a device name ('/dev/pts/...') that can be used as the 
        *port* argument of serial.Serial."""
        
        return os.ttyname(self.user_end)
    
    def _should_stop(self):
        """Return True, IFF a stop flag is set."""
        
        if self._stop_flag.is_set():
            return True
        
        if self._stop_all_instances_flag.is_set():
            return True
        
        return False
                
    def _run(self):
        """Run the parallel thread."""
        
        while not self._should_stop():    
                                       
            #input_ = self._read_without_blocking(self.virtual_end, 
            #                                     self.buffer_size)
            input_ = os.read(self.virtual_end, self.buffer_size)
            
            #time.sleep(0.1)
            
            if input_:
                output = self.process(input_)
                os.write(self.virtual_end, output)
        
        # Close the files after the parallel thread has stopped.
        # Otherwise the system will run out of file descriptors, 
        # if a VirtualConnection is created and stopped many times 
        # in a a row.
        os.close(self.user_end)
        os.close(self.virtual_end)
                        
    @staticmethod
    def _read_without_blocking(file, buffer_size):
        """Read *buffer_size* or less bytes from *file*.
        
        os.read blocks (i.e. doesn't return anything and prevents the 
        program from proceeding) if *file* is some special kind of 
        nonexistant/empty (this is different from a regular empty 
        file). Using this function prevents this blocking and retuns 
        None instead. 
        
        If *file* can be read from but contains less bits than 
        *buffer_size* (including 0 bits), all the bits in *file* are 
        returned, but no more.
        """
        
        # Some of the following variables aren't actually used, 
        # but are given a name to better illustrate what select.select 
        # does. 
        rlist = [file] 
        # select.select checks whether these can be written to.
        wlist = []
        # select.select checks whether these can be read from.
        xlist = []
        # select.select checks whether these have error conditions.
        timeout = 0
        
        readable, writable, errors = select.select(rlist, wlist, xlist, 
                                                   timeout)
        
        # Prevent blocking by reading only if *file* can actually be 
        # read from.
        if file in readable:
            return os.read(file, buffer_size)
        else:
            return None
            
    def process(self, input_):
        """Forms output based on *input_*.
        
        By default, *input_* is simply mirrored back.
        This behaviour can be changed by redefining this function in 
        subcalsses.    
        
        Args:
            input_: A bytes-like object.
        
        Returns: 
            *input_*. This is supposed to be redefined in subclasses.
        """
        
        output = input_
        return output