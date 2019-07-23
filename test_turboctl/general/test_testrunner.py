import unittest

# Successes: 1
# Failures: 2
# Errors: 3
# Skipped: 4
# Total: 10


class TestClass(unittest.TestCase):
        
    def test_this_should_succeed(self):
        self.assertTrue(True)
        
    def test_this_should_fail_1_of_2(self):
        self.assertTrue(False)
        
    def test_this_should_fail_2_of_2(self):
        self.assertTrue(False)

    def test_this_should_raise_an_error_1_of_3(self):
        raise ValueError('This is a test error.')
    
    @unittest.skip('#1 of 4 skipped tests')
    def test_this_should_be_skipped_1_of_4(self):
        self.assertTrue(False)
        
    @unittest.skip('#2 of 4 skipped tests')
    def test_this_should_be_skipped_2_of_4(self):
        self.assertTrue(False)        
        
        
class AnotherTestClass(unittest.TestCase):
    
    def test_this_should_raise_an_error_2_of_3(self):
        raise ValueError('This is a test error.')
        
    def test_this_should_raise_an_error_3_of_3(self):
        raise ValueError('This is a test error.')
    
    
@unittest.skip('This entire class should be skipped')
class SkippedClassWithTwoTests(unittest.TestCase):
    
    def test_this_should_be_skipped_3_of_4(self):
        self.assertTrue(False)
        
    def test_this_should_be_skipped_4_of_4(self):
        self.assertTrue(False)
        
        
if __name__ == '__main__':
    unittest.main()