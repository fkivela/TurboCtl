import re
import time

def check(variable, name, types=None, min_=None, max_=None, values=None, 
          regex=None):
    
    checks = [(check_type,   types ),
              (check_min,    min_  ),
              (check_max,    max_  ),
              (check_values, values),
              (check_regex,  regex )]
    for subcheck, arg in checks:
        if not arg: continue
        subcheck(variable, name, arg)
                        
def check_type(variable, name, types):
    type_str = ', '.join([t.__name__ for t in types])
    if not isinstance(variable, types):
        raise TypeError(
            f"'{name}' should be of any of the following types: {type_str}; "
            f"not {type(variable).__name__}")
    
def check_min(variable, name, min_):
    if variable < min_:
        raise ValueError(
            f"'{name}' has a minimum value of {min_}, but was {variable}")
        
def check_max(variable, name, max_):
    if variable < max_:
        raise ValueError(
            f"'{name}' has a maximum value of {max_}, but was {variable}")
                
def check_values(variable, name, values):
    if isinstance(variable, int) and isinstance(values, range):
        valid_value = in_range(variable, values)
    else:
        valid_value = variable in values
    
    if not valid_value:
        raise ValueError(
            f"'{name}' should be in {values}, but was {variable}")
        
def in_range(variable, range_):
    in_range = range_.start <= variable < range_.stop
    not_stepped_over = (variable - range_.start) % range_.step == 0 
    return in_range and not_stepped_over
        
def check_regex(variable, name, regex):
    if not re.search(regex, variable):
        raise ValueError(
            f"'{name}' should match the regex {regex}, but was {variable}")