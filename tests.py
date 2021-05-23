import unittest
import pathlib
from otto import *
from fpgaobjects import FPGAModel, PrimitiveAttribute, Primitive


paths = {"dummy_fpga.xml": pathlib.Path(__file__).parent.joinpath("fpga_models", "dummy_fpga.xml"),
         "mmcme2_base_attributes.xml": pathlib.Path(__file__).parent.joinpath("primitives", "mmcme2_base_attributes.xml")}


# This test case checks if all necessary files are available
class PathTest(unittest.TestCase):
    def setUp(self) -> None:
        self.file_dict = {key: open(value) for key,value in paths.items()}

    def tearDown(self) -> None:
        for key in self.file_dict:
            self.file_dict[key].close()

    def test_paths(self):
        for key in self.file_dict:
            self.assertTrue(self.file_dict[key].readable())


# Test Case for the FPGAModel class
class FPGAModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_model = FPGAModel.from_xml(paths["dummy_fpga.xml"])

    # Test if attributes were read correctly from xml
    def test_dummy_model_attribute(self):
        self.assertEqual(self.dummy_model.name, "dummy")
        self.assertEqual(self.dummy_model.mmcm_f_in_min, 10)

    # Test if values for specific limitations are validated correctly
    def test_dummy_model_value_verification(self):
        self.assertTrue(self.dummy_model.validate_mmcm_input_frequency(55))
        self.assertFalse(self.dummy_model.validate_pll_vco(799))


# Test Cases for the PrimitiveAttribute classes (and others that inherit from PrimitiveAttribute)
class PrimitiveAttributeTest(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_range_attribute(self):
        attribute = PrimitiveAttribute.from_xml("<primitive_attribute>\
            <attribute_type>RangeAttribute</attribute_type>\
            <name>clkfbout_mult_f</name>\
            <type>float</type>\
            <default>5.000</default>\
            <step_size>0.001</step_size> <!-- needs to be overlooked -->\
            <start>2.000</start>\
            <end>64.000</end>\
        </primitive_attribute>")

        # Set value to something valid and test
        attribute.set_value("11.5")
        self.assertTrue(attribute.is_valid())

        # Set value to something invalid and test
        attribute.set_value("64.001")
        self.assertTrue(attribute.is_valid())

    # Test creation of ListAttribute from xml and test validation function
    def test_list_attribute(self):
        attribute = PrimitiveAttribute.from_xml("<primitive_attribute>\
            <attribute_type>ListAttribute</attribute_type>\
            <name>bandwith</name>\
            <type>str</type>\
            <default>OPTIMIZED</default>\
            <values>\
                <value>OPTIMIZED</value>\
                <value>HIGH</value>\
                <value>LOW</value>\
            </values>\
        </primitive_attribute>")

        # Set value to something valid and test
        attribute.set_value("OPTIMIZED")
        self.assertTrue(attribute.is_valid())

        # Set value to something invalid and test
        attribute.set_value("OTTO")
        self.assertTrue(attribute.is_valid())


# Test Cases for the Primitive class
# This also tests the existing xml files for Primitives
class PrimitiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mmcme2_base_primitive = Primitive.from_xml(paths["mmcme2_base_attributes.xml"])
        # self.plle2_base_primitive = Primitive.from_xml(paths["plle2_base_attributes.xml"])

    # Test if all the necessary attributes were loaded from the xml
    def test_mmcme2_base_attributes(self):
        for attribute_name in ["bandwith", "clkfbout_mult_f", "clkfbout_phase", "clkin1_period", "clkout0_divide_f",
                               "clkout1_divide", "clkout2_divide", "clkout3_divide", "clkout4_divide",
                               "clkout5_divide", "clkout0_duty_cycle", "clkout1_duty_cycle", "clkout2_duty_cycle",
                               "clkout3_duty_cycle", "clkout4_duty_cycle", "clkout5_duty_cycle", "clkout6_duty_cycle",
                               "clkout0_phase", "clkout1_phase", "clkout2_phase", "clkout3_phase", "clkout4_phase",
                               "clkout5_phase", "clkout6_phase", "clkout4_cascade", "divclk_divide", "ref_jitter1",
                               "startup_wait"]:
            self.assertIn(attribute_name, self.mmcme2_base_primitive.__dict__)


if __name__ == '__main__':
    unittest.main()
