import unittest

from turboctl import Parameter, PARAMETERS, parse, Types

# Attributes of the Parameter class:
# number, name, indices, min, max, default, 
# unit, writable, type, size, description

def dummy_parameter(number=1, 
                    name='Test parameter',  
                    indices=range(0), 
                    min_=0, 
                    max_=65535, 
                    default=0, 
                    unit='', 
                    writable=True, 
                    type_=Types.UINT, 
                    size=16, 
                    description='Test description.'):
    
    return Parameter(number=number,
                     name=name,
                     indices=indices, 
                     min=min_, 
                     max=max_, 
                     default=default, 
                     unit=unit, 
                     writable=writable, 
                     type=type_,
                     size=size,
                     description=description)
    
def dummy_parameter_from_line(number='1', 
                    name='"Test parameter"',
                    min_='0', 
                    max_='65535', 
                    default='0', 
                    unit='""', 
                    rw='r/w', 
                    format_='u16',
                    description='"Test description."'):
    
    string = ' '.join([number, name, min_, max_, default, unit, rw, format_, 
                       description])
    return parse(string, 'parameter')
    

class TestParsing(unittest.TestCase):
    
    def test_general(self):
        line = '1 "Test parameter" 0 65535 0 "" r/w u16 "Test description."'
        parameter = parse(line, 'parameter')
        self.assertEqual(parameter, dummy_parameter())
        
    def test_too_many_fields(self):
        line = '1 "Test parameter" 0 65535 0 "" "" r/w u16 "Test description."'
        with self.assertRaises(ValueError):
            parse(line, 'parameter')
            
    def test_too_few_fields(self):
        line = '1 "Test parameter" 0 65535 0 r/w u16 "Test description."'
        with self.assertRaises(ValueError):
            parse(line, 'parameter')

    def test_name_without_quotes(self):
        parameter = dummy_parameter_from_line(name='name')
        self.assertEqual(parameter.name, 'name')

    def test_name_with_line_break(self):
        """Make sure a literal \n is turned into the newline 
        character.
        """
        parameter = dummy_parameter_from_line(name=r'"Lorem\nipsum"')
        self.assertEqual(parameter.name, 'Lorem\nipsum')
        self.assertNotEqual(parameter.name, r'Lorem\nipsum')

    def test_unindexed(self):
        parameter = dummy_parameter_from_line(number='1')
        self.assertEqual(parameter.indices, range(0))
        
    def test_indexed(self):
        parameter = dummy_parameter_from_line(number='1[1:5]')
        self.assertEqual(parameter.indices, range(1,6))
  

    def test_min_max_int(self):
        parameter = dummy_parameter_from_line(min_='-10', max_='100')
        self.assertEqual(parameter.min, -10)
        self.assertEqual(parameter.max, 100)
        
    def test_min_max_float(self):
        parameter = dummy_parameter_from_line(min_='-1.23e-4', max_='4.56e7')
        self.assertEqual(parameter.min, -1.23e-4)
        self.assertEqual(parameter.max, 4.56e7)
        
    def test_min_max_reference(self):
        parameter = dummy_parameter_from_line(min_='P1', max_='P2')
        self.assertEqual(parameter.min, 'P1')
        self.assertEqual(parameter.max, 'P2')
        
        with self.assertRaises(ValueError):
            dummy_parameter_from_line(min_='PX')
            
    def test_default_int(self):
        parameter = dummy_parameter_from_line(default='10')
        self.assertEqual(parameter.default, 10)
        
        parameter = dummy_parameter_from_line(default='-10')
        self.assertEqual(parameter.default, -10)
        
    def test_default_float(self):
        parameter = dummy_parameter_from_line(default='1.2e3')
        self.assertEqual(parameter.default, 1.2e3)

    def test_indexed_default_with_a_single_value(self):
        parameter = dummy_parameter_from_line(number='1[1:3]', default='3')
        self.assertEqual(parameter.default, 3)
        
    def test_indexed_default_with_multiple_values(self):
        parameter = dummy_parameter_from_line(
            number='1[1:3]', default='[3,2,1]')
        self.assertEqual(parameter.default, [3,2,1])
        
    def test_unit(self):
        parameter = dummy_parameter_from_line(unit='"0.1 °C"')
        self.assertEqual(parameter.unit, '0.1 °C')
        
    def test_writable(self):
        parameter = dummy_parameter_from_line(rw='r/w')
        self.assertTrue(parameter.writable)
        
    def test_not_writable(self):
        parameter = dummy_parameter_from_line(rw='""')
        self.assertFalse(parameter.writable)
        
        parameter = dummy_parameter_from_line(rw='r')
        self.assertFalse(parameter.writable)
        
    def test_invalid_writability_fails(self):
        
        with self.assertRaises(ValueError):
            dummy_parameter_from_line(rw='w')
            
        with self.assertRaises(ValueError):
            dummy_parameter_from_line(rw='xyz')
            
    def test_uint(self):
        formats = ['u16', 'u32']
        
        for f in formats:
            with self.subTest(i=f):
                parameter = dummy_parameter_from_line(format_=f)
                self.assertEqual(parameter.type, Types.UINT)
    
    def test_sint(self):
        formats = ['s16', 's32']
        
        for f in formats:
            with self.subTest(i=f):
                parameter = dummy_parameter_from_line(format_=f)
                self.assertEqual(parameter.type, Types.SINT)
        
    def test_float(self):
        f = 'real32'
        parameter = dummy_parameter_from_line(format_=f)
        self.assertEqual(parameter.type, Types.FLOAT)
            
    def test_size_16(self):
        formats = ['u16', 's16']
        
        for f in formats:
            with self.subTest(i=f):
                parameter = dummy_parameter_from_line(format_=f)
                self.assertEqual(parameter.size, 16)
        
    def test_size_32(self):
        formats = ['u32', 's32', 'real32']
        
        for f in formats:
            with self.subTest(i=f):
                parameter = dummy_parameter_from_line(format_=f)
                self.assertEqual(parameter.size, 32)
                
    def test_invalid_size_fails(self):
        formats = ['16', 'x16', 'u']
        
        for f in formats:
            with self.subTest(i=f):
                with self.assertRaises(ValueError):
                    dummy_parameter_from_line(format_=f)
                
    def test_description_without_quotes(self):
        parameter = dummy_parameter_from_line(description='test')
        self.assertEqual(parameter.description, 'test')

    def test_description_with_line_break(self):
        """Make sure a literal \n is turned into the newline 
        character.
        """
        parameter = dummy_parameter_from_line(description=r'"Lorem\nipsum"')
        self.assertEqual(parameter.description, 'Lorem\nipsum')
        self.assertNotEqual(parameter.description, r'Lorem\nipsum')   
        
        
class TestActualParameters(unittest.TestCase):
    
    def test_keys_equal_numbers(self):
        for num, parameter in PARAMETERS.items():
            self.assertEqual(PARAMETERS[num].number, num)
            
    def test_all_parameters_are_defined(self):
        numbers = {1,2,3,4,5,6,7,8,11,16,17,18,19,20,21,23,24,25,26,27,28,29,
                   30,31,32,36,37,38,40,41,43,119,122,125,126,128,131,132,133,
                   134,140,150,171,174,176,179,180,182,183,184,185,227,247,
                   248,249,312,313,314,315,316,349,350,355,394,395,396,601,
                   602,604,606,609,610,611,615,616,617,618,619,620,623,624,
                   625,634,636,643,644,647,648,649,652,670,671,672,673,678,
                   679,682,686,690,918,923,924,1025,1035,1100,1101,1102}
        self.assertEqual(PARAMETERS.keys(), numbers)
        
    # These two test together also assert that all parameter numbers 
    # are ints (since all keys are ints and parameter numbers are equal 
    # to keys).
    
    def test_all_names_are_strings(self):
        for parameter in PARAMETERS.values():
            self.assertIsInstance(parameter.number, int)
            
    def test_all_indices_are_ranges(self):
        for parameter in PARAMETERS.values():
            self.assertIsInstance(parameter.indices, range)
            
    def test_all_mins_are_numbers_or_references(self):
        
        for parameter in PARAMETERS.values():        
            value = parameter.min
            
            # Convert a string value 'P<number>' to an integer:
            try:
                if value[0] == 'P':
                    value = int(value[1:])
            except (TypeError, ValueError):
                pass
            
            self.assertIsInstance(value, (int, float))  
            
    def test_all_maxes_are_numbers_or_references(self):
        
        for parameter in PARAMETERS.values():
            value = parameter.max
            
            # Convert a string value 'P<number>' to an integer:
            try:
                if value[0] == 'P':
                    value = int(value[1:])
            except (TypeError, ValueError):
                pass
            
            self.assertIsInstance(value, (int, float))  

    def test_all_defaults_are_numbers_or_list_of_numbers(self):
        
        for parameter in PARAMETERS.values():
            
            value = parameter.default
            value_is_number = isinstance(value, (int, float))
            value_is_list =  isinstance(value, list)
            try:
                values_are_numbers = all([isinstance(i, (int, float)) 
                                          for i in value])
            except TypeError:
                # Ints and floats aren't iterable and will raise this
                # error.
                pass
                            
            self.assertTrue(
                    value_is_number or (value_is_list and values_are_numbers)) 
            
    def test_all_units_are_strings(self):
        for parameter in PARAMETERS.values():
            self.assertIsInstance(parameter.unit, str) 

    def test_all_writable_values_are_booleans(self):
        for parameter in PARAMETERS.values():
            self.assertIsInstance(parameter.writable, bool)

    def test_all_types_are_uint_sint_or_float(self):
        for parameter in PARAMETERS.values():
            self.assertTrue(
                    parameter.type in (Types.UINT, Types.SINT, Types.FLOAT))

    def test_all_sizes_are_16_or_32(self):
        for parameter in PARAMETERS.values():
            self.assertTrue(parameter.size in (16, 32))

    def test_all_descriptions_are_strings(self):
        for parameter in PARAMETERS.values():
            self.assertIsInstance(parameter.description, str)

          
if __name__ == '__main__':
    unittest.main()