import curses
import curses.ascii

import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()



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
        self.memory = []
        self.memory_ind = -1
        self.temp_line = None
        self.prompt = '>> '
        self.prompt_y = None
        self.prompt_x = None
        self.window = None
        
    def process_input(self, input_str):
        self.memory.insert(0, input_str)
        self.writeline('Gave the command: ' + input_str)
    
    def run(self):
        curses.wrapper(self._run)

    def _run(self, window):
        self.window = window
        while True:
            string = self.getline()        
            #self.writeline()
            self.process_input(string)
                
    def insert(self, char):
        self.window.insstr(char)
        self.right()
        
    def write(self, string):
        self.window.addstr(string)
        self.window.refresh()
        
    def writeline(self, string=''):
        self.write(string + '\n')
        
    def rewrite(self, string):
        self.window.addstr(self.prompt_y, self.prompt_x, string)
        self.window.clrtoeol()
        self.window.refresh()
                
    def left(self):
        y, x = self.window.getyx()  
        self.window.move(y, x - 1)
        self.window.refresh()
        
    def right(self):
        y, x = self.window.getyx()  
        self.window.move(y, x + 1)
        self.window.refresh()
        
    def up(self):
        
        if self.memory_ind + 1 >= len(self.memory):
            return
        
        if self.memory_ind < 0:
            string = self.window.instr(self.prompt_y, self.prompt_x).decode('ASCII')
            string = string.strip()
            self.write(string)
            self.temp_line = string        
        
        self.memory_ind += 1
        self.rewrite(self.memory[self.memory_ind])
            
    def down(self):
        
        if self.memory_ind < 0:
            return
        
        self.memory_ind -= 1
        
        if self.memory_ind < 0:
            string = self.temp_line
        else:
            string = self.memory[self.memory_ind]
        
        self.rewrite(string)

    def delete(self):
        y, x = self.window.getyx()  
        self.window.delch(y, x - 1)     

    def process_char(self, char):
        
        if char in self.ENTER_KEYS:
            return '\n'
            
        elif char == curses.KEY_UP:
            self.up()
            
        elif char == curses.KEY_DOWN:
            self.down()

        elif char == curses.KEY_LEFT:
            self.left()  

        elif char == curses.KEY_RIGHT:
            self.right()
            
        elif char in self.DELETE_KEYS:
            self.delete()
            
        else:
            try:
                return bytes([char]).decode('ASCII')
            except ValueError:
                pass
                        
    def getline(self):
        self.write(self.prompt)
        self.prompt_y, self.prompt_x = self.window.getyx()
        self.memory_ind = -1
        self.temp_line = None

        chars = []
        while True:            
            char = self.window.getch()
            letter = self.process_char(char)    
            
            if letter == '\n':
                break
            
            if not letter:
                continue
                            
            chars.append(letter)
            self.insert(letter)      
             
        string = self.window.instr(self.prompt_y, self.prompt_x).decode('ASCII')
        string = string.strip()
        self.writeline(string)
        return string    

main()