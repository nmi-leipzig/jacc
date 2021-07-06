import unittest
from fpgaconfigurations import *
from pathtests import paths
from fpgaobjects import FPGAModel, Plle2Base, Mmcme2Base
from fpgaconfigurations import ClockingConfiguration


# Test attribute generation for a configuration that only asks for specific frequencies
class ConfigurationBasedOnFrequenciesOnlyTest(unittest.TestCase):

    def setUp(self) -> None:
        # Load the dummy fpga model
        with open(paths["dummy_fpga.xml"]) as file:
            temp_str = "".join(file.readlines())
        self.fpga = FPGAModel.from_xml(temp_str)

        # Create the Mmcme2Base and Plle2Base block
        #self.mmcme_2_base = Mmcme2Base()
        self.plle_2_base = Plle2Base()

    def test_output_f_calc(self):
        clk_configuration = ClockingConfiguration(self.fpga, self.plle_2_base)
        result_list = clk_configuration.get_configurations_for_output_frequencies(500.5, 700, deviation=0.7)
        print(result_list)
        print(len(result_list))



