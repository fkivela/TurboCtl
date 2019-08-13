import curses
import curses.ascii
import sys    
from io import StringIO
        
# TODO: Expand
#curses.keyname(k)
KEYS = {'RESIZE'   : (curses.KEY_RESIZE, 'KEY_RESIZE'),
        'LEFT'     : (curses.KEY_LEFT, 'KEY_LEFT'),
        'RIGHT'    : (curses.KEY_RIGHT, 'KEY_RIGHT'),
        'UP'       : (curses.KEY_UP, 'KEY_UP'),
        'DOWN'     : (curses.KEY_DOWN, 'KEY_DOWN'),
        'ENTER'    : (curses.KEY_ENTER, 'KEY_ENTER', '\n'),
        'BACKSPACE': (curses.KEY_BACKSPACE, curses.ascii.BS, curses.ascii.DEL, 
                      '\b', '\x7f'),
        'DELETE'   : (curses.KEY_DC, 'KEY_DC'),
        'END'      : (curses.KEY_END, 'KEY_END'),
        'HOME'     : (curses.KEY_HOME, 'KEY_HOME'),
        'PG_DOWN'  : (curses.KEY_PPAGE, 'KEY_PPAGE'),
        'PG_UP'    : (curses.KEY_NPAGE, 'KEY_NPAGE'),
}

class Shell():    
        
    def __init__(self, func):
        self.func = func
        self.command_history = []
        self.history_i = -1
        self.new_line = ''
        self.temp_cmd = None
        self.prompt = '>> '
        self.window = None
        self._cursor_position = 0
        self.xloc = 0
        self.yloc = 0
        self.stop_flag = False
        
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
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        win = stdscr
        win.idlok(1)
        win.scrollok(1)
        
        error = None        
        try:
            self._run(win)
        except BaseException as e:
            error = e

        curses.nocbreak()
        stdscr.keypad(False)
        win.keypad(False)
        curses.echo()
        curses.endwin()

        if error:
            raise error
        
        #curses.wrapper(self._run)

    def _run(self, window):        
        self.window = window
        self.pad = curses.newpad(*window.getmaxyx())
        self.window.refresh()
        self.draw()

        while not self.stop_flag:
            self.process_input()
            self.draw()
            
    def draw(self):
        cmds = [self.prompt + line for line in self.command_history  + [self.new_line]]

        lines_2d = [cmd.split('\n') for cmd in cmds]
        lines = []
        for l in lines_2d:
            lines += l
        
        height = len(lines) + 1
        width = max(len(l) for l in lines) + 1 if lines else 1
        self.pad.resize(height, width)
        
        max_y, max_x = self.window.getmaxyx()

        self.pad.erase()
        self.pad.move(0,0)
        self.pad.addstr('\n'.join(lines))
        self.pad.refresh(self.yloc,self.xloc,0,0,max_y-1,max_x-1)
        
#        self.pad.erase()
#        self.pad.move(0,0)
#                
#        for line in self.command_history:
#            self.pad.addstr(self.prompt + line)
#        base_y = self.pad.getyx()[0]
#        self.pad.addstr(self.prompt + self.new_line)
#                
#        max_y, max_x = self.pad.getmaxyx()
#        cursor_x = len(self.prompt) + self.cursor_position
#        
#        new_x = cursor_x % max_x
#        n_newlines = cursor_x // max_x
#        new_y = base_y + n_newlines
#        
#        self.pad.move(new_y, new_x)
#        self.pad.refresh(0,0,0,0,max_y,max_x)
        
        # The arguments are pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol; 
        # the p arguments refer to the upper left corner of the pad region 
        # to be displayed and the s arguments define a clipping box on the 
        # screen within which the pad region is to be displayed.        

        
        
        
        
        
        
        
        
#        self.window.erase()
#        self.window.move(0,0)
#        
#        lines_2d = [cmd.split('\n') for cmd in self.command_history]
#        lines = list(numpy.array(lines_2d).flatten())
#        
#        for line in self.command_history:
#            self.window.addstr(self.prompt + line)
#        base_y = self.window.getyx()[0]
#        self.window.addstr(self.prompt + self.new_line)
#                
#        max_y, max_x = self.window.getmaxyx()
#        cursor_x = len(self.prompt) + self.cursor_position
#        
#        new_x = cursor_x % max_x
#        n_newlines = cursor_x // max_x
#        new_y = base_y + n_newlines
#        
#        self.window.move(new_y, new_x)
#        self.window.refresh()
        
        
        
        
        
        
        
        
    def process_input(self):
        char = self.window.get_wch()
        return self.process_char(char)

    def process_char(self, char):
        
        if char in KEYS['RESIZE']:
            pass
        
        elif char in KEYS['LEFT']:
            self.cursor_position -= 1
            
        elif char in KEYS['RIGHT']:
            self.cursor_position += 1
            
        elif char in KEYS['UP']:
            self.scroll_history(+1)
        
        elif char in KEYS['DOWN']:
            self.scroll_history(-1)
            
        elif char in KEYS['PG_UP']:
            self.yloc -= 1
        
        elif char in KEYS['PG_DOWN']:
            self.yloc += 1
            
        elif char in KEYS['HOME']:
            self.xloc -= 1
        
        elif char in KEYS['END']:
            self.xloc += 1
        
        elif char in KEYS['ENTER']:
            self.enter()
            
        elif char in KEYS['BACKSPACE']:
            self.delete(self.cursor_position - 1) 
            
        elif char in KEYS['DELETE']:
            self.delete(self.cursor_position) 

        else:
            self.write(str(char))
                        
    def scroll_history(self, amount):
        commands = [line.split('\n')[0] for line in self.command_history][::-1]

        if self.history_i == -1:
            self.temp_cmd = self.new_line
            
        self.history_i += amount
        
        if self.history_i >= len(commands):
            self.history_i = len(commands) - 1
        
        if self.history_i < -1:
            self.history_i = - 1
        
        if self.history_i == -1:
            self.new_line = self.temp_cmd
        else:
            self.new_line = commands[self.history_i]
            
        self.cursor_position = len(self.new_line)
        
    def enter(self):
        
        old = sys.stdout    
        output = StringIO()
        
        sys.stdout = output
        stop = self.func(self.new_line)
        sys.stdout = old
        
        self.new_line += '\n' + output.getvalue()

        self.command_history.append(self.new_line)
        self.history_i = -1
        self.new_line = ''
        self.cursor_position = 0
        
        self.stop_flag = stop
        
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