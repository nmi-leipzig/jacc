import unittest
from fpga_primitives import *
from fpga_globals import get_clock_attributes
from fpga_globals import FPGA_MODELS


# Test Cases for the ClockAttribute classes (and others that inherit from ClockAttribute)
class ClockAttributeTest(unittest.TestCase):

    def test_base_class(self):
        # Another class that inherits from ClockAttribute is used here, since ClockAttribute is a abstract class

        # Setup
        attribute = ListAttribute("", "Dieter", "", ["Dieter", "Jürgen", "Friedrich"])
        another_attribute = ListAttribute("", "Dieter", "", ["Dieter", "Jürgen", "Friedrich"])

        # Test default value
        self.assertEqual(attribute.value, "Dieter")

        # Verify that two Attribute of different types return False
        attribute_of_another_type = BoolAttribute("", "Dieter", "")
        self.assertNotEqual(attribute, attribute_of_another_type)

        # Test eq
        self.assertEqual(attribute, another_attribute)

        # Test ne
        attribute.value = "Friedrich"
        self.assertNotEqual(attribute, another_attribute)

    def test_range_attribute(self):
        # Setup
        attribute = RangeAttribute("CLKIN_PERIOD", 0.0, ".CLKIN1_PERIOD(@value@)", 0.0, 52.631, 3)

        # Test set_value
        self.assertRaises(TypeError, attribute.set_value, "")
        self.assertRaises(ValueError, attribute.set_value, 53)

        for value in [52.631, 0.0, 26.5]:
            attribute.set_value(value)
            self.assertEqual(attribute.value, value)

        # Test template
        self.assertEqual(attribute.instantiate_template(), ".CLKIN1_PERIOD(26.500)")

    def test_increment_range_attribute(self):
        # Setup
        attribute = IncrementRangeAttribute("CLKOUT0_DUTY_CYCLE", 0.5, ".CLKOUT0_DUTY_CYCLE(@value@)", 0.00, 0.99, 2,
                                            1 / 7)

        # Test set_and_correct_value
        for value, set_value in [(0.9899, 0.99), (0.99, 0.99), (-1, 0.00), (1, 0.99), (0.5, 4 / 7)]:
            attribute.set_and_correct_value(value)
            self.assertEqual(attribute.value, set_value)

        # Test get_range_as_generator
        self.assertEqual(list(attribute.get_range_as_generator()), [factor * (1 / 7) for factor in range(7)] + [0.99])

    def test_output_divider_value(self):
        # Setup
        attribute = OutputDivider("CLKOUT0_DIVIDE_F", 1, ".CLKOUT0_DIVIDE_F(@value@)", 2.0, 128.0, 3, 0.125,
                                  additional_values=[1])

        # Test get_bounds_based_on_value
        for value, bounds in [(1.3, (1, 2.0)), (0.5, (128.0, 1)), (7.3, (7.25, 7.375)), (127.9, (127.875, 128)),
                              (128, (128.0, 1)), (129, (128.0, 1))]:
            self.assertEqual(attribute.get_bounds_based_on_value(value), bounds)

    def test_list_attribute(self):
        # Setup
        attribute = ListAttribute("BANDWIDTH", "OPTIMIZED", ".BANDWIDTH(@value@)", ["OPTIMIZED", "HIGH", "LOW"])

        # Test set_value
        self.assertRaises(ValueError, attribute.set_value, "OTTO")
        self.assertEqual(attribute.value, "OPTIMIZED")
        attribute.set_value("HIGH")
        self.assertEqual(attribute.value, "HIGH")

        # Test template
        self.assertEqual(attribute.instantiate_template(), ".BANDWIDTH(\"HIGH\")")

    def test_bool_attribute(self):
        # Setup
        attribute = BoolAttribute("START_WAIT", False, ".STARTUP_WAIT(@value@)")

        # Test set_value
        self.assertRaises(TypeError, attribute.set_value, "OTTO")
        attribute.set_value(True)
        self.assertTrue(attribute.value)

        # Test template
        self.assertEqual(attribute.instantiate_template(), ".STARTUP_WAIT(TRUE)")


# Test Cases for the most "complex" methods of the ClockPrimitive class family
class ClockPrimitiveTest(unittest.TestCase):
    f_in_1 = 500
    mmcm_f_out_min = 4.69
    mmcm_f_out_max = 800.0
    pll_f_out_min = 6.25
    pll_f_out_max = 800.0
    m = 30
    d = 10
    mmcm = Mmcme2Base.get_new_instance()
    pll = Plle2Base.get_new_instance()

    def test_clock_primitve_methods(self):
        # Test configure_approximated_o_dividers
        self.pll.configure_approximated_o_dividers(self.m, self.d, self.f_in_1, {0: 800, 1: 400.5, 3: 6.25},
                                                   {0: 1, 1: 1, 3: 1}, self.pll_f_out_min, self.pll_f_out_max)
        for index, value in [(0, 2), (4, 1), (3, 128)]:
            self.assertEqual(self.pll.get_output_divider(index).value, value)

        # Test get_output_frequency
        self.assertEqual(self.pll.get_output_frequency_dict(), {0: 750, 1: 375, 3: 11.71875})

    def test_mmcme_2_base_methods(self):
        # Test approximate_o_divider
        o6 = self.mmcm.approximate_o_divider(6, self.m, self.d, self.f_in_1, self.mmcm_f_out_min, 1,
                                             self.mmcm_f_out_min,
                                             self.mmcm_f_out_max)
        self.assertEqual(o6, 128)

        # Test get_output_frequency
        self.mmcm.clkout6_divide.value = o6
        self.mmcm.clkout6_divide.on = True
        self.mmcm.clkout4_cascade.set_value(True)
        self.mmcm.configure_approximated_o_dividers(self.m, self.d, self.f_in_1, {0: 800, 1: 400.5, 4: 4.69 * o6},
                                                    {0: 1, 1: 1, 4: 1}, self.mmcm_f_out_min, self.mmcm_f_out_max)
        self.assertEqual(self.mmcm.get_output_frequency_dict(), {0: 750, 1: 375, 4: 5.859375, 6: 11.71875})


# Test Cases for the get_clock_attributes function
class AttributeListTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dict_pll = get_clock_attributes("Plle2Base")
        self.temp_dict_mmcm = get_clock_attributes("Mmcme2Base")

    # Test if all the necessary attributes for the Mmcme2Base are existent
    def test_mmcme2_base_attributes(self):
        for attribute_name in ["bandwidth", "clkfbout_mult_f", "clkfbout_phase", "clkin1_period", "clkout0_divide_f",
                               "clkout1_divide", "clkout2_divide", "clkout3_divide", "clkout4_divide", "clkout5_divide",
                               "clkout6_divide", "clkout0_duty_cycle", "clkout1_duty_cycle", "clkout2_duty_cycle",
                               "clkout3_duty_cycle", "clkout4_duty_cycle", "clkout5_duty_cycle", "clkout6_duty_cycle",
                               "clkout0_phase", "clkout1_phase", "clkout2_phase", "clkout3_phase", "clkout4_phase",
                               "clkout5_phase", "clkout6_phase", "clkout4_cascade", "divclk_divide", "ref_jitter1",
                               "startup_wait"]:
            self.assertIn(attribute_name, self.temp_dict_mmcm)

    # Test if all the necessary attributes for the Plle2Base are existent
    def test_plle2_base_attributes(self):
        for attribute_name in ["bandwidth", "clkfbout_mult", "clkfbout_phase", "clkin1_period",
                               "clkout0_divide",
                               "clkout1_divide", "clkout2_divide", "clkout3_divide", "clkout4_divide",
                               "clkout5_divide", "clkout0_duty_cycle", "clkout1_duty_cycle", "clkout2_duty_cycle",
                               "clkout3_duty_cycle", "clkout4_duty_cycle", "clkout5_duty_cycle",
                               "clkout0_phase", "clkout1_phase", "clkout2_phase", "clkout3_phase", "clkout4_phase",
                               "clkout5_phase", "divclk_divide", "ref_jitter1",
                               "startup_wait"]:
            self.assertIn(attribute_name, self.temp_dict_pll)
        self.assertFalse("clkout4_cascade" in self.temp_dict_pll)

    # Test if get_clock_attributes delivers a new copy each time it is called
    def test_reference_and_value_integrity(self):
        self.assertEqual(self.temp_dict_pll["bandwidth"].value, "OPTIMIZED")

        self.temp_dict_pll["bandwidth"].set_value("LOW")
        self.assertEqual(self.temp_dict_pll["bandwidth"].value, "LOW")

        # Reset dictionary
        self.temp_dict_pll = get_clock_attributes("Plle2Base")
        self.assertEqual(self.temp_dict_pll["bandwidth"].value, "OPTIMIZED")


# Test Case for the FPGAModel class
class FPGAModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_model = FPGA_MODELS[("dummy", "dummy")]

    # Test if attributes were read correctly from xml
    def test_dummy_model_attribute(self):
        self.assertEqual(self.dummy_model.model_name, "dummy")
        self.assertEqual(self.dummy_model.mmcm_f_in_min, 10)

    # Test if values for specific limitations are validated correctly
    def test_dummy_model_value_verification(self):
        self.assertTrue(self.dummy_model.validate_mmcm_input_frequency(55))
        self.assertFalse(self.dummy_model.validate_pll_input_frequency(1337))
