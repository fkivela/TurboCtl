"""This module defines the VirtualConnection class, which can be used 
to simulate serial connections."""

import os
import threading
import pty
import time
        
class VirtualConnection():
    """A virtual serial connection.
    
    Data can be sent through a VirtualConnection object by accessing 
    the *user_end* and *virtual_end* attributes. *virtual_end* can be 
    written to and read from with os.read and os.write. 
    os.read doesn't seem to work with *user_end*, and the serial 
    module should be used instead. The *port* attribute returns a 
    device name which can be given to serial.Serial() as an argument.
    
    A VirtualConnection object runs code in a parallel thread.
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
    
    # Keep references to all running instances of this class.
    running_instances = set()
            
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
        
        This function returns only after the parallel thread has 
        actually stopped.
        """
        if self.is_running():
            self._stop_flag.set()
            # Write an empty string to stop os.read from blocking.
            os.write(self.user_end, bytes([0]))
        
        # Wait for the parallel thread to stop.
        while self.is_running():
            time.sleep(0.001)
            
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
        """Return True, IFF the parallel thread is running."""
        return self.thread.is_alive()
        
    @property
    def port(self):
        """Returns a device name ('/dev/pts/...') that can be used as the 
        *port* argument of serial.Serial."""
        
        return os.ttyname(self.user_end)
                    
    def _run(self):
        """Run the parallel thread."""
        
        while not self._stop_flag.is_set():    
            # Blocks until there is input to read.                                       
            input_ = os.read(self.virtual_end, self.buffer_size)
            output = self.process(input_)
            os.write(self.virtual_end, output)
        
        # Close the files after the parallel thread has stopped.
        # Otherwise the system will run out of file descriptors, 
        # if a VirtualConnection is created and stopped many times 
        # in a a row.
        os.close(self.user_end)
        os.close(self.virtual_end)
                                    
    def process(self, input_):
        """Form output based on *input_*.
        
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