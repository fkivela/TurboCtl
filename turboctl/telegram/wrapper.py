class SynchronizedSet(set):
    
    def __init__(self, upon_update, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.upon_update = upon_update

        update_methods = [
            'add', 'clear', 'difference_update', 'discard', 
            'intersection_update', 'pop', 'remove', 
            'symmetric_difference_update', 'update'
        ]
        for name in update_methods:
            method = getattr(self, name)
            new_method = self.add_upon_update(method)
            setattr(self, name, new_method)
        
    def add_upon_update(self, method):
        def new_method(*args, **kwargs):
            method(*args, **kwargs)
            self.upon_update()
        return new_method
    
#def upon_update():
#    print('Toimii')
#    
#s = SynchronizedSet(upon_update)
#print(s)
#s.add(1)
#print(s)