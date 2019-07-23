"""This module is used to run all unit tests at once."""
import unittest
import importlib
import tabulate

# Comment module names away to exclude certain modules 
# from being tested. 
MODS_BY_PKG = {}

MODS_BY_PKG['data'] = [
    'test_parameters',
    ]

MODS_BY_PKG['telegram'] = [
    'test_byteholder',
    'test_conversions', 
    'test_numtypes',
    'test_query',
    'test_reply',
    'test_telegram_wrapper',
    'test_telegram',
    'test_typedbytes'
    ]

MODS_BY_PKG['virtualpump'] = [
    'test_virtualpump', 
    'test_virtualconnection'
    ]

# Uncommenting this module adds 1 successful test, 2 failures, 
# 3 errors and 4 skipped tests. 
# This can be used to test the run_tests() function.
#MODS_BY_PKG['general'] = [
#    'test_testrunner'
#    ]

class Module():
    """A class representing a single module and its test results."""
    
    def __init__(self, name, package_name):
        self.name = name
        self.package_name = package_name
        
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        
    def __add__(self, other):
        """Return *self* + *other*.
        
        If bool(other) is False, return *self*.
        The sum of different test results is acquired by adding 
        all Module objects together.
        """
        
        if not other:
            return self
        
        res = Module('TOTAL', '')
        
        res.tests_run = self.tests_run + other.tests_run
        res.failures = self.failures + other.failures
        res.errors = self.errors + other.errors
        res.skipped = self.skipped + other.skipped
        
        return res
        
    def run_tests(self):
        """Run all tests in this module and record their results."""
        
        module = importlib.import_module(
            f'test_turboctl.{self.package_name}.{self.name}')
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TestResult()    
        suite.run(result)
        
        self.tests_run = result.testsRun
        
        self.failures = [
            FailedResult('failure', *fields) for fields in result.failures]
        
        self.errors = [
            FailedResult('error', *fields) for fields in result.errors]
        
        self.skipped = [
            FailedResult('skipped', *fields) for fields in result.skipped]
        
    @property
    def n_failures(self):
        """The number of failed tests."""
        return len(self.failures)
    
    @property
    def n_errors(self):
        """The number of tests that raised errors."""
        return len(self.errors)
    
    @property
    def n_skipped(self):
        """The number of skipped tests."""
        return len(self.skipped)        

class FailedResult():
    """A class representing any kind of unsuccessful test result 
    (failed, error or skipped)."""
    
    def __init__(self, type_, name, message):
        """Initialize a new instance.
        
        Args:
            type_: 'failure', 'error' or 'skipped'.
            name: Test name.
            message: Test traceback.
            """
        self.type = type_
        self.name = name
        self.message = message
        
    def __str__(self):
        
        type_str = {'failure': 'Failed ',
                    'error': 'Error in ',
                    'skipped': 'Skipped '}[self.type]        
        
        return f'{type_str}{self.name}\n{self.message}'
    

def run_tests():
    """Run all unit tests and print the results."""
    
    # Sort results by package and module name
    modlist = [Module(mod, pkg) 
               for pkg, mods_in_pkg in sorted(MODS_BY_PKG.items()) 
               for mod in sorted(mods_in_pkg)]
    
    for mod in modlist:
        mod.run_tests()
    
    used_pkgs = set()
    
    def row(module):
        
        if module.package_name in used_pkgs:
            pkg_str = ''
        else:
            pkg_str = module.package_name
            used_pkgs.add(module.package_name)
            
        return [pkg_str, module.name, module.tests_run, 
                module.n_failures, module.n_errors, module.n_skipped]
        
    
    total = None
    for module in modlist:
        total = module + total
    
    modlist.append(total)
    results = [row(module) for module in modlist]
    _print_results(results)    
    print()
#    _print_messages(modlist)    

def _print_results(results):    
    """Print a table displaying the quantities of different test 
    results.
    """
    
    headers = ['Package', 'Module', 'Total', 'Failures', 'Errors', 'Skipped']
    print(tabulate.tabulate(results, headers=headers))
    
def _print_messages(modlist):
    """Print messages detailing all unsuccessful tests."""
    
    def printall(list_):
        for x in list_:
            print(x)
    
    for mod in modlist:
        printall(mod.failures)
        printall(mod.errors)
        printall(mod.skipped)
    
    
if __name__ == '__main__':
    run_tests()