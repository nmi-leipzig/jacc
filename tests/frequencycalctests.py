import unittest
from fpgaconfigurations import *
from fpgaglobals import FPGA_MODELS
from fpgaprimitives import Plle2Base, Mmcme2Base
from fpgaconfigurations import ClockingConfiguration


# Test attribute generation for a configuration that only asks for specific frequencies
class ConfigurationBasedOnFrequenciesOnlyTest(unittest.TestCase):

    def setUp(self) -> None:
        self.fpga = FPGA_MODELS[("dummy", "dummy")]

        # Create the Mmcme2Base and Plle2Base block
        self.mmcme_2_base = Mmcme2Base.get_new_instance()
        self.plle_2_base = Plle2Base.get_new_instance()

    def test_output_f_calc(self):

        # Input dictionaries, each dictionary is a test with a different number of output ports
        desired_values_dicts = [{"f_in_1": 505.5, "f_out_0": 700, "delta_0": 0.1},
                                {"f_in_1": 650, "f_out_0": 345.8, "f_out_1": 690, "delta_1": 1,
                                 "f_out_2": 200, "delta_2": 4},
                                {"f_in_1": 400, "f_out_0": 345, "delta_0": 10, "f_out_1": 690, "delta_1": 6,
                                 "f_out_2": 200, "delta_2": 6, "f_out_3": 700, "delta_3": 12, "f_out_4": 250,
                                 "delta_4": 50},
                                {"f_in_1": 400, "f_out_0": 400, "delta_0": 0, "f_out_1": 540, "delta_1": 50,
                                 "f_out_2": 200, "delta_2": 20, "f_out_3": 633, "delta_3": 100, "f_out_4": 250,
                                 "delta_4": 50, "f_out_5": 456, "delta_5": 200, "f_out_6": 245, "delta_6": 100},
                                {"f_in_1": 19, "f_out_0": 600, "f_out_1": 300, "delta_0": 3, "delta_1": 3}
                                ]
        # Used primitive for each test case
        used_primitives = [self.mmcme_2_base, self.plle_2_base, self.plle_2_base, self.mmcme_2_base, self.plle_2_base]
        # output clock counter for each test case
        output_count = [1, 3, 5, 7, 2]

        for input_dict, primitive, outputs in zip(desired_values_dicts, used_primitives, output_count):
            clk_configuration = ClockingConfiguration(self.fpga, primitive)
            result_list = clk_configuration.configure_frequency_parameters(**input_dict)
            self.assertGreater(len(result_list), 0)
            for confi in result_list:
                output_frequencies = confi.get_output_frequency_dict()
                for i in range(outputs):
                    if f"delta_{i}" in input_dict:
                        self.assertAlmostEqual(input_dict[f"f_out_{i}"], output_frequencies[i],
                                               delta=input_dict[f"delta_{i}"])
                    else:
                        self.assertAlmostEqual(input_dict[f"f_out_{i}"], output_frequencies[i], delta=0.5)

    def test_min_max_medium_frequency_pll(self):
        # PLL
        f_in_values = [19, 400, 800]
        f_out_values = [6.25, 400, 800]
        # Fitting delta values are taken from the clk wiz
        deltas = [0.2, 1, 210, 0, 0, 0, 0, 0, 0]
        delta_count = 0
        for in_value in f_in_values:
            for out_value in f_out_values:
                clk_configuration = ClockingConfiguration(self.fpga, self.plle_2_base)
                result_list = clk_configuration.configure_frequency_parameters(in_value, out_value,
                                                                               delta_0=deltas[delta_count])
                self.assertGreater(len(result_list), 0)
                for confi in result_list:
                    output_frequencies = confi.get_output_frequency_dict()
                    self.assertAlmostEqual(out_value, output_frequencies[0], delta=deltas[delta_count])
                delta_count += 1

        # This specific test verifies that the max out frequency is not exceeded:
        clk_configuration = ClockingConfiguration(self.fpga, self.plle_2_base)
        result_list = clk_configuration.configure_frequency_parameters(19, 800, delta_0=100)
        self.assertEqual(len(result_list), 0)

        # MMCM
        f_in_values = [10, 400, 800]
        f_out_values = [4.69, 400, 800]
        # Fitting delta values are taken from the clk wiz
        deltas = [0.2, 100, 201, 0.2, 0, 0, 0.2, 0, 0]
        delta_count = 0
        for in_value in f_in_values:
            for out_value in f_out_values:
                clk_configuration = ClockingConfiguration(self.fpga, self.mmcme_2_base)
                result_list = clk_configuration.configure_frequency_parameters(in_value, out_value,
                                                                               delta_0=deltas[delta_count])
                self.assertGreater(len(result_list), 0)
                for confi in result_list:
                    output_frequencies = confi.get_output_frequency_dict()
                    self.assertAlmostEqual(out_value, output_frequencies[0], delta=deltas[delta_count])
                delta_count += 1


        # This specific test verifies that the max out frequency is not exceeded:
        clk_configuration = ClockingConfiguration(self.fpga, self.mmcme_2_base)
        result_list = clk_configuration.configure_frequency_parameters(10, 800, delta_0=150)
        self.assertEqual(len(result_list), 0)

        # This specific test verifies that the max out frequency is not exceeded:
        clk_configuration = ClockingConfiguration(self.fpga, self.mmcme_2_base)
        result_list = clk_configuration.configure_frequency_parameters(10, 400, delta_0=50)
        self.assertEqual(len(result_list), 0)

