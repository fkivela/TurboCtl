class Wrapper():
    
    fields = ['obj', 'setter', 'getter', 'caller']
    
    def __init__(self, obj):
        self.obj = obj
        
    # TODO: Why is this needed?
    # TODO: Print like set
    def __iter__(self, *args, **kwargs):
        return self.obj.__iter__(*args, **kwargs)
        
    def __setattr__(self, name, value):
        
        if name == 'fields' or name in self.fields:
            self.__dict__[name] = value
        else:
            self.setter(self.obj, name, value)
            
    def __getattr__(self, name):
        
        if name == 'fields' or name in self.fields:
            return self.__dict__[name]
        else:
            return self.getter(self.obj, name)
        
    def __call__(self, *args, **kwargs):
        self.caller(self.obj, *args, **kwargs)
        
    def __str__(self):
        return f'{type(self).__name__}({repr(self.obj)})'
    
    def __repr__(self):
        return str(self)
        
    def setter(self, obj, name, value):
        setattr(obj, name, value)
        
    def getter(self, obj, name):
        getattr(obj, name)
        
    def caller(self, obj, *args, **kwargs):
        obj(*args, **kwargs)
        
        
class NotifyUponCall(Wrapper):
    
    fields = Wrapper.fields + ['upon_call']
    
    def __init__(self, obj, upon_call):
        self.obj = obj
        self.upon_call = upon_call
    
    def caller(self, obj, *args, **kwargs):
        obj(*args, **kwargs)
        self.upon_call()


class NotifyUponAccess(Wrapper):
    
    fields = Wrapper.fields + ['upon_change']
    
    def __init__(self, obj, upon_change):
        self.obj = obj
        self.upon_change = upon_change
        
    def setter(self, obj, name, value):
        setattr(obj, name, value)
        self.upon_change()
        
    def getter(self, obj, name):
        out = getattr(obj, name)
        self.upon_change()
        return NotifyUponCall(out, self.upon_change)