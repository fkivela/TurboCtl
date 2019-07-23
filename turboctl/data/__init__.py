"""This package defines dictionaries containing data about pump 
parameters, errors and warnings.
"""
#import turboctl.data.parser as parser
#Parameter = parser.Parameter
#ErrorOrWarning = parser.ErrorOrWarning
#PARAMETERS = parser.PARAMETERS
#ERRORS = parser.ERRORS
#WARNINGS = parser.WARNINGS

from .codes import (ParameterAccess, ParameterResponse, ParameterError, 
                    ControlBits, StatusBits)
from .parser import (Parameter, ErrorOrWarning, PARAMETERS, ERRORS, WARNINGS, 
                     parse)
from .types import Types