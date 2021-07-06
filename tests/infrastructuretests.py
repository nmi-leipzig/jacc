import unittest
from pathtests import paths
from fpga_globals import get_clock_attributes
from fpgaobjects import FPGAModel


# Test Cases for the ClockAttribute classes (and others that inherit from ClockAttribute)
class PrimitiveAttributeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dict_pll = get_clock_attributes("Plle2Base")
        self.temp_dict_mmcm = get_clock_attributes("Mmcme2Base")

    def test_range_attribute(self):
        attribute = self.temp_dict_mmcm["clkfbout_mult_f"]

        # Set value to something valid and test
        attribute.set_value(11.5)
        self.assertTrue(attribute.is_valid())

        # Set value to something invalid and test
        attribute.set_value(64.001)
        self.assertFalse(attribute.is_valid())

    # Test creation of ListAttribute from xml and test validation function
    def test_list_attribute(self):
        attribute = self.temp_dict_mmcm["bandwidth"]

        # Test "values" attribute
        self.assertTrue(attribute.values == ["OPTIMIZED", "HIGH", "LOW"])

        # Set value to something valid and test
        attribute.set_value("OPTIMIZED")
        self.assertTrue(attribute.is_valid())

        # Set value to something invalid and test
        attribute.set_value("OTTO")
        self.assertFalse(attribute.is_valid())


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
        with open(paths["dummy_fpga.xml"]) as file:
            temp_str = "".join(file.readlines())
        self.dummy_model = FPGAModel.from_xml(temp_str)

    # Test if attributes were read correctly from xml
    def test_dummy_model_attribute(self):
        self.assertEqual(self.dummy_model.name, "dummy")
        self.assertEqual(self.dummy_model.mmcm_f_in_min, 10)

    # Test if values for specific limitations are validated correctly
    def test_dummy_model_value_verification(self):
        self.assertTrue(self.dummy_model.validate_mmcm_input_frequency(55))
        self.assertFalse(self.dummy_model.validate_pll_input_frequency(1337))
