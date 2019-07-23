import os
import sys
import pygount
import glob

# Add the path to turboctl:
dirname = os.path.abspath(os.path.dirname(__file__))
superdir = os.path.split(dirname)[0]
if not superdir in sys.path:
    sys.path.append(superdir)
    
import turboctl

path = os.path.dirname(turboctl.__file__)
files = glob.glob(path + '/**/*.py', recursive=True)
data = [pygount.source_analysis(file, '') for file in files]

code_lines = 0
doc_lines = 0
empty_lines = 0

for file_data in data:
    code_lines += file_data.code + file_data.string
    doc_lines += file_data.documentation
    empty_lines += file_data.empty

print('Lines by type:')    
print(f'  Code: {code_lines}')
print(f'  Documentation: {doc_lines}')
print(f'  Empty: {empty_lines}')
print(f'  Total: {code_lines + doc_lines + empty_lines}')