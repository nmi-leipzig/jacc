import unittest
from fpgaconfigurations import *
from pathtests import paths
from fpgaobjects import FPGAModel, Primitive


# Test attribute generation for a configuration that only asks for specific frequencies
class ConfigurationBasedOnFrequenciesOnlyTest(unittest.TestCase):

    def setUp(self) -> None:
        # Load the dummly fpga model
        with open(paths["dummy_fpga.xml"]) as file:
            temp_str = "".join(file.readlines())
        self.fpga = FPGAModel.from_xml(temp_str)

        # Load the Mmcme2Base block
        with open(paths["mmcme2_base_attributes.xml"]) as file:
            temp_str = "".join(file.readlines())
        self.primitive = Primitive.from_xml(temp_str)

        self.configuration = ClockingConfiguration(fpga, primitive)

    def test_setting_attributes(self):
        self.assertFalse(self.configuration.set_input_frequencies(f_in_1=5))
        self.assertTrue(self.configuration.set_input_frequencies(f_in_1=100))

        self.assertFalse(self.configuration.set_output_frequencies(f_out_1=2000))
        self.assertTrue(self.configuration.set_output_frequencies(f_out_1=500, f_out_2=332))
        self.assertTrue(self.configuration.set_output_frequencies(f_out_1=500, f_out_2=332, f_out_3=900, f_out_4=553,
                                                                  f_out_5=756, f_out_6=120))
        self.assertFalse(self.configuration.set_output_frequencies(f_out_1=500, f_out_2=332, f_out_3=900, f_out_4=553,
                                                                   f_out_5=756, f_out_6=120, f_out_7=124, f_out_8=80,
                                                                   f_out_9=100))

    def test_generating_for_one_frequency(self):
        self.configuration.set_input_frequencies(f_in_1=100)
        self.configuration.set_output_frequencies(f_out_1=527)

        self.configuration.generate_attributes()
        self.assertEqual(self.configuration.to_attribute_dict(), {".BANDWIDTH": "OPTIMIZED",
                                                                  ".CLKOUT4_CASCADE": "FALSE",
                                                                  ".STARTUP_WAIT": "FALSE",
                                                                  ".DIVCLK_DIVIDE ": 3,
                                                                  ".CLKFBOUT_MULT_F": 41.500,
                                                                  ".CLKFBOUT_PHASE": 0.000,
                                                                  ".CLKOUT0_DIVIDE_F": 2.625,
                                                                  ".CLKOUT0_PHASE": 0.000,
                                                                  ".CLKOUT0_DUTY_CYCLE": 0.500,
                                                                  ".CLKIN1_PERIOD": 10.000})

    def test_generating_for_multiple_outputs(self):
        self.configuration.set_input_frequencies(f_in_1=100)
        self.configuration.set_output_frequencies(f_out_1=500, f_out_2=328.125, f_out_3=178.5)
        self.configuration.generate_attributes()
        self.assertEqual(self.configuration.to_attribute_dict(), {".BANDWIDTH": "OPTIMIZED",
                                                                  ".CLKOUT4_CASCADE": "FALSE",
                                                                  ".STARTUP_WAIT": "FALSE",
                                                                  ".DIVCLK_DIVIDE": 1,
                                                                  ".CLKFBOUT_MULT_F": 13.125,
                                                                  ".CLKFBOUT_PHASE": 0.000,
                                                                  ".CLKOUT0_DIVIDE_F": 2.625,
                                                                  ".CLKOUT0_PHASE": 0.000,
                                                                  ".CLKOUT0_DUTY_CYCLE": 0.500,
                                                                  ".CLKOUT1_DIVIDE": 4,
                                                                  ".CLKOUT1_PHASE": 0.000,
                                                                  ".CLKOUT1_DUTY_CYCLE": 0.500,
                                                                  ".CLKOUT2_DIVIDE": 7,
                                                                  ".CLKOUT2_PHASE": 0.000,
                                                                  ".CLKOUT2_DUTY_CYCLE": 0.500,
                                                                  ".CLKIN1_PERIOD": 10.000})
