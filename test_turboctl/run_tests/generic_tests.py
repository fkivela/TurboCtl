import unittest
import math

class GenericTests(unittest.TestCase):
    
    def _test_args(self, function, args_and_rets):
        try:
            iterable = args_and_rets.items()
        except AttributeError:
            iterable = args_and_rets
        
        for args, ret in iterable:
            with self.subTest(i=args):
                if isinstance(ret, type) and issubclass(ret, Exception):
                    self._test_error(function, args, ret)
                else:
                    self._test_return(function, args, ret)
                
    def _test_return(self, function, args, correct_return):
        actual_return = function(*args)
            
        if not isinstance(correct_return, float):
            self.assertEqual(actual_return, correct_return)
            return
        
        if math.isnan(correct_return):
            self.assertTrue(math.isnan(actual_return))
            return
        
        delta = max(1E-10, 1E-5 * abs(correct_return))
        self.assertAlmostEqual(actual_return, correct_return, delta=delta)
            
    def _test_error(self, function, args, error):
        with self.assertRaises(error):
            function(*args)
