class UIError(Exception):
    """Abstract superclass"""
    pass

class UITypeError(UIError):
    """For arguments with a wrong type"""
    pass

class UIValueError(UIError):
    """For arguments with a correct type but a wrong value"""
    pass

class UIArgumentNumberError(UIError):
    """For wrong number of arguments"""
    pass

class UICommandError(UIError):
    """For an invalid command"""
    pass

class UIParseError(UIError):
    """For commands or arguments that cannot be parsed"""
    pass