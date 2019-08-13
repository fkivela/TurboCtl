import curses
import curses.ascii
from .tui import AbstractTUI        
from io import StringIO
import sys    
    
# TODO: Scrolling
    
class InteractiveTUI(AbstractTUI):
    
    def __init__(self, port):
        super().__init__(port)
        self.shell = Shell(super().process_input)
        #self.shell.prompt = "Type a command or 'help' for a list of commands: "
    
    def run(self):
        self.shell.run()

# TODO: Expand
KEYS = {'RESIZE'   : (curses.KEY_RESIZE, 'KEY_RESIZE'),
        'LEFT'     : (curses.KEY_LEFT, 'KEY_LEFT'),
        'RIGHT'    : (curses.KEY_RIGHT, 'KEY_RIGHT'),
        'UP'       : (curses.KEY_UP, 'KEY_UP'),
        'DOWN'     : (curses.KEY_DOWN, 'KEY_DOWN'),
        'ENTER'    : (curses.KEY_ENTER, 'KEY_ENTER', '\n'),
        'BACKSPACE': (curses.KEY_BACKSPACE, curses.ascii.BS, curses.ascii.DEL, 
                      '\b', '\x7f'),
        'DELETE'   : (curses.KEY_DC, 'KEY_DC'),
}

class Shell():    
        
    def __init__(self, func):
        self.func = func
        self.lines = []
        self.cmd_history_i = -1
        self.new_line = ''
        self.temp_cmd = None
        self.prompt = '>> '
        self.window = None
        self._cursor_position = 0
                
    @property
    def cmd_history(self):
        return [line.split('\n')[0] for line in self.lines][::-1]
                
    @property
    def cursor_position(self):
        return self._cursor_position
    
    @cursor_position.setter
    def cursor_position(self, value):
        if value < 0:
            self._cursor_position = 0
        elif value > len(self.new_line):
            self._cursor_position = len(self.new_line)
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
        
        for line in self.lines:
            self.window.addstr(self.prompt + line)
        base_y = self.window.getyx()[0]
        self.window.addstr(self.prompt + self.new_line)
                
        max_y, max_x = self.window.getmaxyx()
        cursor_x = len(self.prompt) + self.cursor_position
        
        new_x = cursor_x % max_x
        n_newlines = cursor_x // max_x
        new_y = base_y + n_newlines
        
        self.window.move(new_y, new_x)
        self.window.refresh()
        
    def process_input(self):
        char = self.window.get_wch()
        self.process_char(char)

    def process_char(self, char):

        if char in KEYS['RESIZE']:
            pass
        
        elif char in KEYS['LEFT']:
            self.cursor_position -= 1
            
        elif char in KEYS['RIGHT']:
            self.cursor_position += 1
            
        elif char in KEYS['UP']:
            self.up()
        
        elif char in KEYS['DOWN']:
            self.down()
        
        elif char in KEYS['ENTER']:
            self.enter()
            
        elif char in KEYS['BACKSPACE']:
            self.delete(self.cursor_position - 1) 
            
        elif char in KEYS['DELETE']:
            self.delete(self.cursor_position) 

        else:
            self.write(char)
                        
    def up(self):
        
        if self.cmd_history_i == -1:
            self.temp_cmd = self.new_line
            
        self.cmd_history_i += 1
        if self.cmd_history_i >= len(self.cmd_history):
            self.cmd_history_i = len(self.cmd_history) - 1
            
        self.new_line = self.cmd_history[self.cmd_history_i]
        
        self.cursor_position = len(self.new_line)
        
    def down(self):
        self.cmd_history_i -= 1
        
        if self.cmd_history_i < 0:
            self.cmd_history_i = -1
            self.new_line = self.temp_cmd
        else:
            self.new_line = self.cmd_history[self.cmd_history_i]
            
        self.cursor_position = len(self.new_line)
        
    def enter(self):
        
        old = sys.stdout    
        output = StringIO()
        
        sys.stdout = output
        stop = self.func(self.new_line)
        sys.stdout = old
        
        self.new_line += '\n' + output.getvalue()

        self.lines.append(self.new_line)
        self.cmd_history_i = -1
        self.new_line = ''
        self.cursor_position = 0
        
        return stop
        
    def delete(self, position):
        start = self.new_line[:position]
        end = self.new_line[position + 1:]
        self.new_line = start + end
        self.cursor_position = position
            
    def write(self, string):
        start = self.new_line[:self.cursor_position]
        end = self.new_line[self.cursor_position:]
        self.new_line = start + string + end
        self.cursor_position += len(string)