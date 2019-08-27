"""This module was created to test the count_lines module.

If the count_lines script works, it should report this module as having:
    9 lines of code (6 actual code lines and 3 string lines.)
    25 lines of documentation
    4 empty lines
    38 total lines
    
pygount separates lines into four categories: code, documentation, 
empty and string.
* Empty lines include lines containing only whitespace and also 
    lines containing only a pass statement.
* Documentation includes comments and docstrings. Empty lines inside 
    docstrings are part of the string,and are also counted as 
    documentation.
* Lines containing only strings and brackets are counted a string 
    lines.
* All other lines are code.

count_lines.py sums code lines and string lines together and 
counts both as lines of code.
"""

def plus(x, y):
    """Return x plus y."""
    return x + y

# Define variables.
x = 1
y = 2
# Print their sum.
print(f'{x}+{y}={plus(x,y)}') # Prints 1+2=3
    
x = ['This line is a code line.',
     'This line is a string line.',
     ('This line is a also a string line,'
     
     'but the line above is empty.')]