"""This package is used to form telegrams that send commands to the 
pump.
"""
from . import conversions
from .numtypes import TurboNum, Uint, Sint, Float, Bin

#from .telegram_wrapper import TelegramWrapper, Query, Reply
from .telegram import Telegram