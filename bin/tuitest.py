import curses
import curses.ascii

#import locale
#locale.setlocale(locale.LC_ALL, '')
#code = locale.getpreferredencoding()



#class InteractiveTUI():
#    
#    def __init__(self, port):
#        super().__init__(port)
#    
#    def run(self):
#        prompt = "Type a command or 'help' for a list of commands: "
#        
#        stop = False
#        while not stop:
#            stop = super().process_input(input(prompt))
#            
#    def write(self, string):
        
def main():
    ui = InteractiveTUI()
    ui.run()

class InteractiveTUI():    
    
    ENTER_KEYS = ('\n', curses.KEY_ENTER, curses.ascii.NL)
    DELETE_KEYS = ('\b', curses.KEY_BACKSPACE, curses.ascii.DEL, curses.ascii.BS)
    
    def __init__(self):
        self.lines = ['lorem\nout\nput', 'ipsum', 'dolor sit ametttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt', 'testi']
        #self.memory = []
        #self.memory_ind = -1
        #self.temp_line = None
        self.prompt = '>> '
        #self.prompt_y = None
        #self.prompt_x = None
        self.window = None
        self.cursor_position = 0
        
    @property
    def cursor_position(self):
        return self._cursor_position
    
    @cursor_position.setter
    def cursor_position(self, value):
        if value < 0:
            self._cursor_position = 0
        elif value > len(self.lines[-1]):
            self._cursor_position = len(self.lines[-1])
        else:
            self._cursor_position = value
        
    def run(self):
        curses.wrapper(self._run)

    def _run(self, window):
        self.window = window
        self.draw()

        while True:
            self.process_input()
            self.draw()
            
            
    def draw(self):
        self.window.erase()
        self.window.move(0,0)
        
        for line in self.lines[:-1]:
            self.window.addstr(self.prompt + line + '\n')
        base_y = self.window.getyx()[0]
        self.window.addstr(self.prompt + self.lines[-1])
        
        max_y, max_x = self.window.getmaxyx()
        cursor_x = len(self.prompt) + self.cursor_position
        
        new_x = cursor_x % max_x
        n_newlines = cursor_x // max_x
        new_y = base_y + n_newlines
        
        self.window.move(new_y, new_x)
        self.window.refresh()
        
    def process_input(self):
        char = self.window.getkey()
        self.process_char(char)

    def process_char(self, char):
        
        if char in (curses.KEY_RESIZE, 'KEY_RESIZE'):
            pass
        
        elif char in (curses.KEY_LEFT, 'KEY_LEFT'):
            self.cursor_position -= 1
            
        elif char in (curses.KEY_RIGHT, 'KEY_RIGHT'):
            self.cursor_position += 1
            
        elif char in (curses.KEY_UP, 'KEY_UP'):
            pass
        
        elif char in (curses.KEY_DOWN, 'KEY_DOWN'):
            pass
        
        elif char in (curses.KEY_ENTER, '\n'):
            self.lines[-1] = self.lines[-1] + '\nGave the command: ' + self.lines[-1]
            self.lines.append('')
            self.cursor_position = 0
            
        elif char in (curses.KEY_BACKSPACE, 'KEY_BACKSPACE', curses.ascii.BS, curses.ascii.DEL, '^?'):
            self.delete(self.cursor_position - 1) 
            
        elif char in (curses.KEY_DC, 'KEY_DC'):
            self.delete(self.cursor_position) 


        else:
            print(repr(char))
            self.write(str(char))
            
    def delete(self, position):
        start = self.lines[-1][:position]
        end = self.lines[-1][position + 1:]
        self.lines[-1] = start + end
        self.cursor_position = position
            
    def write(self, string):
        start = self.lines[-1][:self.cursor_position]
        end = self.lines[-1][self.cursor_position:]
        self.lines[-1] = start + string + end
        self.cursor_position += len(string)
        

        
        
        
        
        
        
        
        
        
#    def process_input(self, input_str):
#        self.memory.insert(0, input_str)
#        self.writeline('Gave the command: ' + input_str)
#            
#    def insert(self, char):
#        self.window.insstr(char)
#        self.right()
#        
#    def write(self, string):
#        self.window.addstr(string)
#        self.window.refresh()
#        
#    def writeline(self, string=''):
#        self.write(string + '\n')
#        
#    def rewrite(self, string):
#        self.window.addstr(self.prompt_y, self.prompt_x, string)
#        self.window.clrtoeol()
#        self.window.refresh()
#                
#    def left(self):
#        y, x = self.window.getyx()  
#        self.window.move(y, x - 1)
#        self.window.refresh()
#        
#    def right(self):
#        y, x = self.window.getyx()  
#        self.window.move(y, x + 1)
#        self.window.refresh()
#        
#    def up(self):
#        
#        if self.memory_ind + 1 >= len(self.memory):
#            return
#        
#        if self.memory_ind < 0:
#            string = self.window.instr(self.prompt_y, self.prompt_x).decode('ASCII')
#            string = string.strip()
#            self.write(string)
#            self.temp_line = string        
#        
#        self.memory_ind += 1
#        self.rewrite(self.memory[self.memory_ind])
#            
#    def down(self):
#        
#        if self.memory_ind < 0:
#            return
#        
#        self.memory_ind -= 1
#        
#        if self.memory_ind < 0:
#            string = self.temp_line
#        else:
#            string = self.memory[self.memory_ind]
#        
#        self.rewrite(string)
#
#    def delete(self):
#        y, x = self.window.getyx()  
#        self.window.delch(y, x - 1)     
#
#    
#    def getline(self):
#        self.write(self.prompt)
#        self.prompt_y, self.prompt_x = self.window.getyx()
#        self.memory_ind = -1
#        self.temp_line = None
#
#        chars = []
#        while True:            
#            char = self.window.getch()
#            letter = self.process_char(char)    
#            
#            if letter == '\n':
#                break
#            
#            if not letter:
#                continue
#                            
#            chars.append(letter)
#            self.insert(letter)      
#             
#        string = self.window.instr(self.prompt_y, self.prompt_x).decode('ASCII')
#        string = string.strip()
#        self.writeline(string)
#        return string    

main()