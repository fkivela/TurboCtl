"""This script counts the number of lines of code in the TurboCtl  
project and prints the results.
"""
import os
import pygount
import glob
import tabulate

def main():
    # The directory of this script (bin).
    dirname = os.path.abspath(os.path.dirname(__file__))
    # The directory above that (TurboCtl).
    superdir = os.path.split(dirname)[0]
    # Find all files ending in .py under the TurboCtl directory.
    files = glob.glob(superdir + '/**/*.py', recursive=True)
    # Count the number of lines in each of the files.
    data = [row(file) for file in files]
    # Sort the results alphabetically.
    data.sort()
    
    headers = ['Package', 'Subpackage', 'Module', 'Code', 'Documentation', 
               'Empty', 'Total']
    totals = ['TOTAL', '', ''] + [column_sum(data, j) for j in range(3,7)]
    
    # Add *totals* under *headers* in order to move them above the 
    # vertical line drawn by tabulate.
    total_headers = [f'{header}\n{totals[i]}' for i, header in enumerate(headers)]
    
    print()
    print('Lines of code in the TurboCtl project by line type and module')
    print()
    print(tabulate.tabulate(data, headers=total_headers))

def names(path):
    """Return the package, subpackage and module names extracted from *path*.
    
    If there is only one package layer, the subpackage name is set to ''.
    """
    no_ending = path.split('.')[0]
    no_start = no_ending.split('TurboCtl/')[-1]
    fields = no_start.split('/')

    pkg = fields[0]
    subpkg = fields[1] if len(fields) == 3 else ''
    module = fields[-1]

    return [pkg, subpkg, module]

def row(file):
    """Return a table row (a list) of data about *file*.
    
    The row contains the following data: 
        package name, subpackage name, module name, lines of code, 
        lines of documenration, empty lines, total lines
    """
    file_data = pygount.source_analysis(file, '')
    package, subpackage, module = names(file)
    
    # Count both code lines and string lines as lines of code.
    code_lines = file_data.code + file_data.string
    doc_lines = file_data.documentation
    empty_lines = file_data.empty
    total = code_lines + doc_lines + empty_lines
    
    return [
        package, subpackage, module, code_lines, doc_lines, empty_lines, total]

def column_sum(data, j):
    """Return the sum of all the cells in the j'th column of the 2d 
    list *data*.
    """
    s = 0
    for row in data:
        s += row[j]
    return s

if __name__== '__main__':
    main()