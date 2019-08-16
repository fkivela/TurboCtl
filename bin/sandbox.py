import enum


#class Test(int):
#    
#    def __new__(cls, x, msg):
#        obj = super().__new__(cls, x)
#        return obj
#    
#    def __init__(self, x, msg):
#        self.msg = msg
        

# Toimii mutta arvo on 0
#class TestEnum(enum.IntEnum):
#    
#    def __new__(cls, value, description):
#        obj = int.__new__(cls)        
#        obj._value_ = value # prevents "'str' object cannot be interpreted as an integer"
#        return obj
#
#    
#    def __init__(self, value, description):
#        self._value_ = value
#        self.description = description
#    
#    Y = (1, '10')
#    K = (2, '10')
    
#print(Test.Y + Test.K)
#print(Test.Y.value, Test.Y.description)

# Tomii mutta ei descriptionia
#class TestEnum(int, enum.Enum):
#    
#    def __new__(cls, value):
#        obj = int.__new__(cls, value)
#        return obj
#    #    obj = int.__new__(cls)        
#    #    obj._value_ = value # prevents "'str' object cannot be interpreted as an integer"
#    #    return obj
#
#    def __init__(self, value):
#        self._value_ = value
#        #self.description = description
#    
#    Y = (1)
#    K = (2)
#    
#print(int(TestEnum.Y))


class TestInt(int):
    
    def __new__(cls, value, description):
        return int.__new__(cls, value)

class TestEnum(TestInt, enum.Enum):
    
    #def __new__(cls, value, _):
    #    obj = int.__new__(cls, value)
    #    return obj
    #    obj = int.__new__(cls)        
    #    obj._value_ = value # prevents "'str' object cannot be interpreted as an integer"
    #    return obj

    def __init__(self, value, description):
        self._value_ = value
        self.description = description
    
    Y = (1, '1')
    K = (2, '1')
    
print(int(TestEnum.Y))








#class Test(enum.IntEnum):
#    
#    def __new__(cls, value, description):
#        obj = int.__new__(cls)        
#        obj._value_ = value # prevents "'str' object cannot be interpreted as an integer"
#        return obj
#
#    
#    def __init__(self, value, description):
#        #self._value_ = value
#        self.description = description
#    
#    Y = (1, '10')
#    K = (2, '10')
#    
#print(Test.Y + Test.K)
#print(Test.Y.value, Test.Y.description)

