"""This module defines an API of functions which can be used to send commands
to the pump.

All functions in this module share the following common arguments:
    
    *connection*:
        This is a :class:`serial.Serial` instance, which is used to send the
        command.
        
    *pump_on*:
        If this evaluates to ``True``, control bits telling the pump to turn or
        stay on are added to the telegram. Otherwise receiving the telegram
        will cause the pump to turn off if it is on.  

If a command cannot be sent due to an error in the connection, a
:class:`serial.SerialException` will be raised.

The functions return the a :class:`~turboctl.telegram.telegram.TelegramReader`
instance created from the reply telegram sent by the pump.
"""

from turboctl.telegram.codes import ControlBits
from turboctl.telegram.telegram import (Telegram, TelegramBuilder, 
                                        TelegramReader)


_PUMP_ON_BITS = [ControlBits.COMMAND, ControlBits.ON]

           
def send(connection, telegram):
    """Send *telegram* to the pump.
    
    Args:
        telegram: A :class:`~turboctl.telegram.telegram.Telegram` instance.
    """
    connection.write(bytes(telegram))
    reply_bytes = connection.read(Telegram.LENGTH)
    reply = TelegramBuilder.from_bytes(reply_bytes).build()
    return TelegramReader(reply)

    
def status(connection, pump_on=True):
    """Request pump status.
    
    This function sends an empty telegram to the pump, which causes it to send
    back a reply containing some data about the status of the pump.
    
    This can also be used for turning the pump on or off by setting *pump_on*
    to ``True`` or ``False``.
    """
    
    builder = TelegramBuilder()
    
    if pump_on:
        builder.set_flag_bits(_PUMP_ON_BITS)
    
    query = builder.build()
    return send(connection, query)

            
def _access_parameter(connection, number, index, value, mode, pump_on):
    """This auxiliary function provides functionality for both reading and
    writing parameter values, since the processes are very similar.
    """
    builder = (TelegramBuilder()
        .set_parameter_number(number)
        .set_parameter_index(index)
        .set_parameter_value(value)
        .set_parameter_mode('read')
    )
    
    if pump_on:
        builder.set_flag_bits(_PUMP_ON_BITS)
    
    query = builder.build()
    return send(connection, query)

    
def read_parameter(connection, number, index=0, pump_on=True):
    """Read the value of an index of a parameter.
    
    Args:
        number
            The number of the parameter.
            
        index
            The index of the parameter (0 for unindexed parameters).
            
    Raises:
        ValueError:
            If *number* or *index* have invalid values.
    """
    _access_parameter(connection, number, index, 0, 'read', pump_on)


def write_parameter(connection, value, number, index=0, pump_on=True):
    """Write a value to an index of a parameter.
    
    Args:
        number:
            The number of the parameter.
            
        index:
            The index of the parameter (0 for unindexed parameters).
            
        value:
            The value to be written.
            
    Raises:
        ValueError:
            If *number* or *index* have invalid values.
    """
    _access_parameter(connection, number, index, value, 'write', pump_on)
