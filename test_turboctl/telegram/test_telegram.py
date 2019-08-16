"""Unit tests for the telegram module."""
import unittest

from turboctl import Telegram, Types

# Maximum and minumun values for 16 and 32 bit 
# signed and unsigned integers.
MAX_16 = 2**16 - 1
MAX_32 = 2**32 - 1

MAX_S16 = 2**15 - 1
MIN_S16 = -2**15

MAX_S32 = 2**31 - 1
MIN_S32 = -2**31

def dummy_data(**kwargs):
    """Returns a list that can be used to construct a telegram with 
    specific contents.
    
    Usage: dummy_data(i2=3, i4=9) => [2, 22, 3, 0, 9, 0, ..., checksum]
    The checksum is computed automatically unless set by hand 
    (by defining  the argument i23).
    """
    
    data = [2, 22] + 22*[0]       
    for k, v in kwargs.items():
        i = int(k[1:])
        data[i] = v
    
    # Compute the checksum only if it isn't set by hand.
    if 'i23' not in kwargs:    
        data[-1] = Telegram.compute_checksum(data[:-1])
        
    return data
        
class Base(unittest.TestCase):
    
    def setUp(self):        

        self.data = dummy_data(i3=100, i4=210,
                              i6=56,
                              i9=21, i10=56,
                              i11=51, i12=15,
                              i13=4, i14=197,
                              i15=9, i16=28, 
                              i17=13, i18=115, 
                              i21=17, i22=202)
        
        # A Telegram object with the following contents:
        # Parameter access type: 0110
        # Parameter number: 1234 ('0110' + '0' + 1234 = 100 210)
        # Index: 56
        # Parameter value: 5432 (21 56)
        # Status/control bits: 1111000011001100 (51 15)
        #     Note that status/control bits are saved in the Telegram 
        #     in reverse order
        # Frequency: 1221 (4 197)
        # Temperature: 2332 (9 28)
        # Current: 3443 (13 115)
        # Voltage: 4554 (17 202)
        # Checksum: 250

        self.telegram = Telegram(self.data)
    
    
class TestPropertyGetters(Base):
    
    def test_parameter_access_type(self):
        self.assertEqual(self.telegram.parameter_access_type, '0110')
        
    def test_parameter_number(self):
        self.assertEqual(self.telegram.parameter_number, 1234)
        
    def test_parameter_index(self):
        self.assertEqual(self.telegram.parameter_index, 56)
        
    def test_parameter_value(self):
        self.assertEqual(self.telegram.parameter_value, 5432)
        
    def test_control_or_status_bits(self):
        self.assertEqual(self.telegram.control_or_status_bits, 
                         '1111000011001100')
        
    def test_frequency(self):
        self.assertEqual(self.telegram.frequency, 1221)
        
    def test_temperature(self):
        self.assertEqual(self.telegram.temperature, 2332)
        
        # Temperature can also be negative.
        self.telegram.typedbytes[15:17] = 65531
        self.assertEqual(self.telegram.temperature, -5)
        
    def test_current(self):
        self.assertEqual(self.telegram.current, 3443)
        
    def test_voltage(self):
        self.assertEqual(self.telegram.voltage, 4554)
        
    def test_checksum(self):
        self.assertEqual(self.telegram.checksum, 250)

    
class TestPropertySetters(Base):
    # Because the getter tests prove that getters work as intended, 
    # getters can be used in testing setters.
            
    def setter_test(self, property_, valid_values, invalid_values, 
                    invalid_types):
        
        for value in valid_values:
            with self.subTest(i=value):
                setattr(self.telegram, property_, value)
                self.assertTrue(self.telegram.is_valid())
                self.assertEqual(getattr(self.telegram, property_), value)
                
        for value in invalid_values:
            with self.subTest(i=value):
                with self.assertRaises(ValueError):
                    setattr(self.telegram, property_, value)
                    
        for value in invalid_types:
            with self.subTest(i=value):
                with self.assertRaises(TypeError):
                    setattr(self.telegram, property_, value)
                    
    def setter_uint_test(self, property_, size):
        name = property_
        valid = [0, 123, 2**size-1]
        invalid = [-1, 2**size]
        type_error = ['1', 1.0]
        self.setter_test(name, valid, invalid, type_error)
        
    def test_parameter_access_type(self):
        name = 'parameter_access_type'
        valid = ['0000', '1111', '0101']
        invalid = ['00000', '000', '0002']
        type_error = [1, 1.0]
        self.setter_test(name, valid, invalid, type_error)
 
    def test_parameter_number(self):
        self.setter_uint_test('parameter_number', 11)
        
    def test_parameter_index(self):
        self.setter_uint_test('parameter_index', 8)
                
    def test_control_or_status_bits(self):
        name = 'control_or_status_bits'
        valid = [16*'0', 16*'1', '1111000011001100']
        invalid = [15*'0', 17*'0', 15*'1'+'2']
        type_error = [1, 1.0]
        self.setter_test(name, valid, invalid, type_error)
        
    def test_frequency(self):
        self.setter_uint_test('frequency', 16)
        
    def test_temperature(self):        
        name = 'temperature'
        valid = [MIN_S16, -123, 123, MAX_S16]
        invalid = [MIN_S16-1, MAX_S16+1]
        type_error = ['1', 1.0]
        self.setter_test(name, valid, invalid, type_error)
        
    def test_current(self):
        self.setter_uint_test('current', 16)     
        
    def test_voltage(self):
        self.setter_uint_test('voltage', 16)
        
    def test_checksum(self):
        
        # Make sure all setters update the checksum correctly.
        t = Telegram()
        t.parameter_access_type = '0110'
        t.parameter_number = 1234
        t.parameter_index = 56
        t.parameter_value = 5432
        t.control_or_status_bits = '1111000011001100'
        t.frequency = 1221
        t.temperature = 2332
        t.current = 3443
        t.voltage = 4554
        
        self.assertEqual(t.checksum, 250)
        
        # Make sure the checksum can also be set by hand.
        t.checksum = 123
        self.assertEqual(t.checksum, 123)


class TestParameterValue(TestPropertySetters):
    
    def value_test(self, type_, values):
        
        for value in values:
            with self.subTest(i=value):
                self.telegram.parameter_value = value
                self.assertTrue(self.telegram.is_valid())
                value_out = self.telegram.get_parameter_value(type_)
                
                if isinstance(value, float):
                    self.assertAlmostEqual(value_out, value, 
                                           delta=10**-5*value)
                else:
                    self.assertEqual(value_out, value)

    def test_default(self):
        # This test tests the parameter_value property instead of the 
        # get_parameter_value method.
        name = 'parameter_value'
        valid = [0, 123, MAX_32]
        invalid = []
        type_error = []
        self.setter_test(name, valid, invalid, type_error)
        
    def test_int(self):
        # This and all following tests test the get_parameter_value 
        # method.
        values = [0, 123, MAX_32]
        self.value_test(Types.UINT, values)
        
        
        
    def test_signed_int(self):
        values = [MIN_S32, -123, 123, MAX_S32]
        self.value_test(Types.SINT, values)
        
    def test_string(self):
        values = ['0', '1010', 32*'1']
        
        for value in values:
            with self.subTest(i=value):
                self.telegram.parameter_value = value
                self.assertTrue(self.telegram.is_valid())
                value_out = self.telegram.get_parameter_value(Types.STR)
                self.assertEqual(value_out, value.zfill(32))
        
    def test_float(self):
        values = [-123.456e7, 0.0, 1.0e-1, 123.456e7]
        self.value_test(Types.FLOAT, values)
        
    def test_invalid_values_fail(self):
        
        invalid_values = [MIN_S32-1, MAX_32+1, '', 33*'0', 15*'0'+'2']
        
        for value in invalid_values:
            with self.subTest(i=value):
                with self.assertRaises(ValueError):
                    self.telegram.parameter_value = value
                    
    def test_invalid_types_fail(self):
                    
        invalid_types = [int, [], bytes()]
        
        for value in invalid_types:
            with self.subTest(i=value):
                with self.assertRaises(TypeError):
                    self.telegram.parameter_value = value
                    
                    
class TestSpecialSetters(Base):
    
    def test_set_checksum(self):
        
        telegram = Telegram()
        
        # Copy telegram contents from data but leave the correct 
        # checksum out.
        telegram.typedbytes.data = bytearray(self.data[:-1] + [0])
        # The telegram should now be invalid.
        self.assertFalse(telegram.is_valid())
        
        telegram.set_checksum()
        self.assertEqual(telegram.checksum, self.data[-1])
        # The telegram should now be valid again.
        self.assertTrue(telegram.is_valid())
        
    def test_set_control_or_status_bits(self):
        
        telegram = Telegram()
        self.assertEqual(telegram.control_or_status_bits, '0000000000000000')
        
        telegram.set_control_or_status_bits([0, 10, 2, 15, 7, 4], '111111')
        self.assertEqual(telegram.control_or_status_bits, '1010100100100001')
        
        telegram.set_control_or_status_bits([0, 10, 2], '100')
        self.assertEqual(telegram.control_or_status_bits, '1000100100000001')


class TestInit(Base):
    
    def test_empty(self):
        empty_bytes = dummy_data()
        self.assertEqual(Telegram().data, bytearray(empty_bytes))
        
    def test_full(self):        
        self.assertEqual(self.telegram.data, bytearray(self.data))
                                
    def test_bad_arguments_fail(self):        
        # This tries to initialize an empty Telegram with 
        # a length of 24, which will fail because the start, length 
        # and checksum bytes have invalid values.
        with self.assertRaises(ValueError):
            Telegram(24)
            
        with self.assertRaises(TypeError):
            Telegram(1.0)
            
    def test_kwargs(self):  
        t1 = Telegram(current=1234, parameter_index=5)
        t2 = Telegram()
        t2.current = 1234
        t2.parameter_index = 5
        self.assertEqual(t1, t2)
        
    def test_invalid_kwarg_name_fails(self):
        with self.assertRaises(TypeError):
            Telegram(wrong_kwarg=0)
            
    def test_data_as_both_arg_and_kwarg_fails(self):
        with self.assertRaises(TypeError):
            Telegram(self.data, data=self.data)
            
    def test_kwarg_with_invalid_value_fails(self):
        with self.assertRaises(ValueError):
            Telegram(frequency=-1)
            
    def test_setting_both_kwargs_and_data_fails(self):
        with self.assertRaises(TypeError):
            Telegram(self.data, current=0)
            
    def test_wrong_length_fails(self):
        
        empty = dummy_data()
        short = empty[:2] + empty[3:] # length = 23
        long = empty[:2] + [0] + empty[2:] # length = 25
        
        with self.assertRaises(ValueError):
            Telegram(short) 
                    
        with self.assertRaises(ValueError):
            Telegram(long)
                        
    def test_wrong_start_byte_fails(self):
        
        data = dummy_data(i0=0) # Should be 2.
        with self.assertRaises(ValueError):
            Telegram(data)    
            
    def test_wrong_length_byte_fails(self):
        
        data = dummy_data(i1=0) # Should be 22.
        with self.assertRaises(ValueError):
            Telegram(data)     
            
    def test_wrong_checksum_fails(self):

        data = dummy_data(i23=1) # Should be 20.
        with self.assertRaises(ValueError):
            Telegram(data)      
            
            
class TestIsValid(Base):
            
    def test_correct_telegram_is_valid(self):
        # Test an empty telegram
        self.assertTrue(Telegram().is_valid())
        
        # Test a telegram full of data
        self.assertTrue(self.telegram.is_valid())
        
    def test_wrong_start_byte_is_invalid(self):
        self.telegram.typedbytes[0] = 10
        self.assertFalse(self.telegram.is_valid())
        
    def test_wrong_length_byte_is_invalid(self):
        self.telegram.typedbytes[1] = 10
        self.assertFalse(self.telegram.is_valid())
        
    def test_wrong_length_is_invalid(self):
        self.telegram.typedbytes.data = bytearray(
            [2, 22, 0, 0, 0, 0, 0, 0, 0, 20])
        self.assertFalse(self.telegram.is_valid())
        
    def test_wrong_checksum_is_invalid(self):
        self.telegram.typedbytes[23] = 10
        self.assertFalse(self.telegram.is_valid())
            
            
class TestUtils(Base):
    
    def test_str(self):
        t = Telegram()
        string = ("Telegram(parameter_access_type='0000', "
                           "parameter_number=0, "
                           "parameter_index=0, "
                           "parameter_value=0, "
                           "control_or_status_bits='0000000000000000', "
                           "frequency=0, "
                           "temperature=0, "
                           "current=0, "
                           "voltage=0, "
                           "checksum=20)")
        self.assertEqual(str(t), string)
    
    def test_repr(self):
        new_tel = eval(repr(self.telegram))
        self.assertEqual(new_tel, self.telegram)
        self.assertFalse(new_tel is self.telegram)
        
    def test_eq(self):
        
        self.assertEqual(self.telegram, self.telegram)
        self.assertEqual(self.telegram, Telegram(self.data))
        self.assertNotEqual(self.telegram, Telegram())
        # Make sure comparison with a non-Telegram object doesn't
        # raise errors.
        self.assertNotEqual(self.telegram, 1)
        
    def test_len(self):
        self.assertEqual(len(self.telegram), 24)
    
        
class TestHiddenMethods(Base):
    
    def test_xor(self):        
        a = 12 # = 1100_bin
        b = 10 # = 1010_bin
        c = 6  # = 0110_bin  
        
        self.assertEqual(Telegram._xor(a, b), c)
        
    def test_compute_checksum(self):
        
        nums = [54, 12, 255, 0, 17, 2, 89, 55, 23, 88, 48, 21, 5, 89, 70, 150, 
                199, 52, 109, 201, 11, 56, 38]
        self.assertEqual(Telegram.compute_checksum(nums), 28)
                
        
if __name__ == '__main__':
    unittest.main()