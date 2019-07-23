
class Switcher():
    
    def __init__(self, value, name='*value*'):
        self.value = value
        self.name = name
        self.acceptable_values = set()
        self.types_all_valid = set()
        self.finished = False
        
    @property
    def types_some_valid(self):
        return {type(case) for case in self.acceptable_values}
    
    @property
    def acceptable_types(self):
        return self.types_all_valid | self.types_some_valid
        
    def case(self, case_value):
        self.acceptable_values.add(case_value)
        
        if self.finished:
            return False
        
        if self.value == case_value:
            self.finished = True
            return True
        
        return False
    
    def case_type(self, type_):
        self.acceptable_types.add(type_)
        
        if self.finished:
            return False
        
        if isinstance(self.value, type_):
            self.finished = True
            return True
        
        return False
    
    def error(self):
        
        correct_type = any([isinstance(self.value, type_) 
                            for type_ in self.acceptable_types])
        
        if not correct_type:
            raise TypeError(
                f"{self.name} should be an instance of one of the following: "
                f"{self.types_str}, not a(n) {type(self.value).__name__}")
            
        raise ValueError(
                f"{self.name} should be one of the following: "
                f"{self.cases}, not {self.value}")
        
    @property
    def types_str(self):
        return '{' + ', '.join(
            [t.__name__ for t in self.acceptable_types]) + '}'