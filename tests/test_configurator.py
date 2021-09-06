import unittest
from fpga_primitives import *
from fpga_globals import FPGA_MODELS
from fpga_configurator import *


class FrequencyConfigurationTest(unittest.TestCase):
    """
    One huge class for all tests regarding configuration since most of these tests use result values from previous ones
    """

    def frequency_setup(self):
        """
        A manually called replacement for setUp that is called before tests for configure_frequency_parameters
        """
        self.fpga = FPGA_MODELS[("artix-7", "-3", "1.0V")]

        # Create the Mmcme2Base and Plle2Base block
        self.mmcme_2_base = Mmcme2Base.get_new_instance()
        self.plle_2_base = Plle2Base.get_new_instance()

    def after_frequency_setup(self):
        """
        A manually called replacement for setUp that is only called before tests for configure_phase_shift_parameters
        or configure_duty_cycle_parameters
        """
        self.frequency_setup()
        self.configurator_pll = ClockingConfigurator(self.fpga, self.plle_2_base)
        self.configurator_mmcm = ClockingConfigurator(self.fpga, self.mmcme_2_base)
        # Create some configurations with frequency parameters from another test
        self.configurator_pll.configure_frequency_parameters(**{"f_in_1": 400, "f_out_0": 345, "delta_0": 0.1,
                                                                "f_out_1": 690, "delta_1": 0.01, "f_out_2": 200,
                                                                "delta_2": 0.05, "f_out_3": 700, "delta_3": 0.15,
                                                                "f_out_4": 250, "delta_4": 0.2})
        self.configurator_mmcm.configure_frequency_parameters(
            **{"f_in_1": 400, "f_out_0": 400, "delta_0": 0, "f_out_1": 540, "delta_1": 0.1,
               "f_out_2": 200, "delta_2": 0.1, "f_out_3": 633, "delta_3": 0.17, "f_out_4": 250,
               "delta_4": 0.2, "f_out_5": 456, "delta_5": 0.5, "f_out_6": 245, "delta_6": 0.5})

    def setup_configurator_with_specific_config(self, m, d, o0, o1):
        """
        This is used for some duty_cycle and phase shift tests
        A configurator with only one configuration in its list with specific will created
        m, d, o0 and o1 are set directly which means all precautions and checks are skipped since it is for tests only
        But this does imply that only possible values are set through these tests
        """
        # Mmcm has basically all the features that pll has and will therefore be preferred here
        configurator_mmcm = ClockingConfigurator(FPGA_MODELS[("artix-7", "-3", "1.0V")], Mmcme2Base.get_new_instance())
        configuration = Mmcme2Base.get_new_instance()
        configuration.d.value = d
        configuration.d.on = True
        configuration.m.value = m
        configuration.m.on = True
        configuration.get_output_divider(0).value = o0
        configuration.get_output_divider(1).value = o1
        configuration.get_output_divider(0).on = True
        configuration.get_output_divider(1).on = True

        # Append configuration to configurator
        configurator_mmcm.configuration_candidates = [configuration]

        return configurator_mmcm

    def test_output_f_calc(self):
        self.frequency_setup()

        # Input dictionaries, each dictionary is a test with a different number of output ports
        desired_values_dicts = [{"f_in_1": 505.5, "f_out_0": 700, "delta_0": 0.2},
                                {"f_in_1": 650, "f_out_0": 345.8, "f_out_1": 690, "delta_1": 0.2,
                                 "f_out_2": 200, "delta_2": 0.05},
                                {"f_in_1": 400, "f_out_0": 345, "delta_0": 0.1, "f_out_1": 690, "delta_1": 0.01,
                                 "f_out_2": 200, "delta_2": 0.05, "f_out_3": 700, "delta_3": 0.15, "f_out_4": 250,
                                 "delta_4": 0.2},
                                {"f_in_1": 400, "f_out_0": 400, "delta_0": 0, "f_out_1": 540, "delta_1": 0.1,
                                 "f_out_2": 200, "delta_2": 0.1, "f_out_3": 633, "delta_3": 0.17, "f_out_4": 250,
                                 "delta_4": 0.2, "f_out_5": 456, "delta_5": 0.5, "f_out_6": 245, "delta_6": 0.5},
                                {"f_in_1": 19, "f_out_0": 600, "f_out_1": 300, "delta_0": 0.005, "delta_1": 0.01}
                                ]
        # Used primitive for each test case
        used_primitives = [self.mmcme_2_base, self.plle_2_base, self.plle_2_base, self.mmcme_2_base, self.plle_2_base]
        # output clock counter for each test case
        output_count = [1, 3, 5, 7, 2]

        for input_dict, primitive, outputs in zip(desired_values_dicts, used_primitives, output_count):
            clk_configurator = ClockingConfigurator(self.fpga, primitive)
            result_list = clk_configurator.configure_frequency_parameters(**input_dict)
            self.assertGreater(len(result_list), 0)
            for confi in result_list:
                output_frequencies = confi.get_output_frequency_dict()
                for i in range(outputs):
                    if f"delta_{i}" in input_dict:
                        self.assertAlmostEqual(input_dict[f"f_out_{i}"], output_frequencies[i],
                                               delta=input_dict[f"delta_{i}"] * input_dict[f"f_out_{i}"])

    def test_frequency_calc_with_cascade(self):
        self.frequency_setup()

        # Test precompute_o6_divider
        clk_configurator = ClockingConfigurator(self.fpga, self.mmcme_2_base)
        o4, o6 = clk_configurator.precompute_o6_divider(800, 2, 1, 4.69, 0.005)
        self.assertAlmostEqual((800 * 2) / (o4 * o6), 4.69, delta=4.69 * 0.005)

        # Test with f_out_4_cascade=False
        # This should lead to no results
        results = clk_configurator.configure_frequency_parameters(800, f_out_0=750, f_out_1=800, f_out_4=4.69,
                                                                  delta_0=0.1, delta_1=0, delta_4=0.005)
        self.assertEqual(len(results), 0)

        # Test with f_out_4_cascade=True and a output frequency 6 in use that allows the output frequency 4
        results = clk_configurator.configure_frequency_parameters(800, f_out_0=750, f_out_1=800, f_out_4=4.69,
                                                                  f_out_6=19, delta_0=0.1, delta_1=0, delta_4=0.05,
                                                                  delta_6=0.1, f_out_4_cascade=True)
        self.assertGreater(len(results), 0)

        # Test with f_out_4_cascade=True and a output frequency 6 in use that does NOT allow the output frequency 4
        results = clk_configurator.configure_frequency_parameters(800, f_out_0=750, f_out_1=800, f_out_4=4.69,
                                                                  f_out_6=800, delta_0=0.1, delta_1=0, delta_4=0.05,
                                                                  delta_6=0, f_out_4_cascade=True)
        self.assertEqual(len(results), 0)

        # Test with f_out_4_cascade=True and output frequency 6 NOT in use
        results = clk_configurator.configure_frequency_parameters(800, f_out_0=750, f_out_1=800, f_out_4=4.69,
                                                                  delta_0=0.1, delta_1=0, delta_4=0.05,
                                                                  f_out_4_cascade=True)
        self.assertGreater(len(results), 0)
        # Also to be sure check their output value for the frequency 4 and assure that cascade is used and out6 is on
        for confi in results:
            self.assertTrue(confi.clkout4_cascade.on)
            self.assertTrue(confi.clkout6_divide.on)
            self.assertAlmostEqual(4.69, confi.get_output_frequency(4), delta=4.69 * 0.05)

    def test_min_max_medium_frequency_pll(self):
        self.frequency_setup()

        # PLL
        f_in_values = [19, 400, 800]
        f_out_values = [6.25, 400, 800]
        # Fitting delta values are taken from the clk wiz
        deltas = [0.04, 0.003, 0.27, 0, 0, 0, 0, 0, 0]
        delta_count = 0
        for in_value in f_in_values:
            for out_value in f_out_values:
                clk_configurator = ClockingConfigurator(self.fpga, self.plle_2_base)
                result_list = clk_configurator.configure_frequency_parameters(in_value, out_value,
                                                                              delta_0=deltas[delta_count])
                self.assertGreater(len(result_list), 0)
                for confi in result_list:
                    output_frequencies = confi.get_output_frequency_dict()
                    self.assertAlmostEqual(out_value, output_frequencies[0], delta=deltas[delta_count] * out_value)
                delta_count += 1

        # This specific test verifies that the max out frequency is not exceeded:
        clk_configurator = ClockingConfigurator(self.fpga, self.plle_2_base)
        result_list = clk_configurator.configure_frequency_parameters(19, 800, delta_0=0.125)
        self.assertEqual(len(result_list), 0)

        # MMCM
        f_in_values = [10, 400, 800]
        f_out_values = [4.69, 400, 800]
        # Fitting delta values are taken from the clk wiz
        deltas = [0.02, 0.25, 0.26, 0.05, 0, 0, 0.05, 0, 0]
        delta_count = 0
        for in_value in f_in_values:
            for out_value in f_out_values:
                clk_configuration = ClockingConfigurator(self.fpga, self.mmcme_2_base)
                result_list = clk_configuration.configure_frequency_parameters(in_value, out_value,
                                                                               delta_0=deltas[delta_count])
                self.assertGreater(len(result_list), 0)
                for confi in result_list:
                    output_frequencies = confi.get_output_frequency_dict()
                    self.assertAlmostEqual(out_value, output_frequencies[0], delta=deltas[delta_count] * out_value)
                delta_count += 1

        # This specific test verifies that the max out frequency is not exceeded:
        clk_configuration = ClockingConfigurator(self.fpga, self.mmcme_2_base)
        result_list = clk_configuration.configure_frequency_parameters(10, 800, delta_0=0.1875)
        self.assertEqual(len(result_list), 0)

        # This specific test verifies that the max out frequency is not exceeded:
        clk_configuration = ClockingConfigurator(self.fpga, self.mmcme_2_base)
        result_list = clk_configuration.configure_frequency_parameters(10, 400, delta_0=0.125)
        self.assertEqual(len(result_list), 0)

    def test_duty_cycle_after_frequency_calc(self):
        self.after_frequency_setup()

        # PLL test
        input_dict = {"duty_cycle_0": 0.4, "duty_cycle_1": 0.8, "duty_cycle_2": 0.13, "duty_cycle_3": 0.5,
                      "duty_cycle_4": 0.66, "delta_0": 0.1, "delta_1": 0.16, "delta_2": 0.15, "delta_3": 0,
                      "delta_4": 0.015}
        results = self.configurator_pll.configure_duty_cycle_parameters(**input_dict)

        self.assertGreater(len(results), 0)
        # Test each candidate
        for confi in results:
            for i in range(5):
                self.assertAlmostEqual(confi.get_duty_cycle(i).value, input_dict[f"duty_cycle_{i}"],
                                       delta=input_dict[f"delta_{i}"] * input_dict[f"duty_cycle_{i}"])

        self.after_frequency_setup()
        # MMCM test
        input_dict = {"duty_cycle_0": 0.7, "duty_cycle_1": 0.75, "duty_cycle_2": 0.13, "duty_cycle_3": 0.62,
                      "duty_cycle_4": 0.66, "duty_cycle_5": 0.3, "duty_cycle_6": 0.2, "delta_0": 0.06, "delta_1": 0.001,
                      "delta_2": 0.3, "delta_3": 0.35, "delta_4": 0.065, "delta_5": 0.12, "delta_6": 0.001}
        results = self.configurator_mmcm.configure_duty_cycle_parameters(**input_dict)

        self.assertGreater(len(results), 0)
        # Test each candidate
        for confi in results:
            for i in range(5):
                self.assertAlmostEqual(confi.get_duty_cycle(i).value, input_dict[f"duty_cycle_{i}"],
                                       delta=input_dict[f"delta_{i}"] * input_dict[f"duty_cycle_{i}"])

    def test_phase_shift_after_frequency_calc(self):
        self.after_frequency_setup()
        # PLL test
        input_dict = {"phase_shift_0": -133.7, "phase_shift_1": -30, "phase_shift_2": -69, "phase_shift_3": -42,
                      "phase_shift_4": 101, "delta_0": 0.11, "delta_1": 0.25, "delta_2": 0.16,
                      "delta_3": 0.075, "delta_4": 0.04}
        results = self.configurator_pll.configure_phase_shift_parameters(**input_dict)

        self.assertGreater(len(results), 0)
        # Test each candidate
        for confi in results:
            for i in range(5):
                self.assertAlmostEqual(confi.get_phase_shift(i).value, input_dict[f"phase_shift_{i}"],
                                       delta=abs(input_dict[f"delta_{i}"] * input_dict[f"phase_shift_{i}"]))

        self.after_frequency_setup()
        # MMCM test
        input_dict = {"phase_shift_0": 77.5, "phase_shift_1": 30, "phase_shift_2": -90, "phase_shift_3": -350,
                      "phase_shift_4": -360, "phase_shift_5": 66.5, "phase_shift_6": -270, "delta_0": 0.055,
                      "delta_1": 0.255, "delta_2": 0.001, "delta_3": 0.038, "delta_4": 0.001, "delta_5": 0.016,
                      "delta_6": 0.001}
        results = self.configurator_mmcm.configure_phase_shift_parameters(**input_dict)

        self.assertGreater(len(results), 0)
        # Test each candidate
        for confi in results:
            for i in range(5):
                self.assertAlmostEqual(confi.get_phase_shift(i).value, input_dict[f"phase_shift_{i}"],
                                       delta=abs(input_dict[f"delta_{i}"] * input_dict[f"phase_shift_{i}"]))

    def test_duty_cycle_others(self):
        # Tests are written through these lists
        # Values of the same test should have the same index in all lists
        # New values can be added here
        m_values = [49.875, 46.5, 19.375]
        d_values = [25, 25, 7]
        o0_values = [38, 62, 64]
        o1_values = [1, 48, 101]
        o0_duty_cycles = [0.02, 0.01, 0.01]
        o1_duty_cycles = [0.8, 0.8, 0.47]
        # All those really tiny delta values are because of tiny floating point differences
        o0_deltas = [0.32, 0.62, 0.22]
        o1_deltas = [0.41, 0.00261, 0.0007]

        for i in range(len(m_values)):
            configurator = self.setup_configurator_with_specific_config(m_values[i], d_values[i], o0_values[i],
                                                                        o1_values[i])
            configurator.configure_duty_cycle_parameters(duty_cycle_0=o0_duty_cycles[i], duty_cycle_1=o1_duty_cycles[i],
                                                         delta_0=o0_deltas[i], delta_1=o1_deltas[i])
            confi = configurator.configuration_candidates[0]
            self.assertAlmostEqual(confi.get_duty_cycle(0).value, o0_duty_cycles[i],
                                   delta=o0_deltas[i] * o0_duty_cycles[i])
            self.assertAlmostEqual(confi.get_duty_cycle(1).value, o1_duty_cycles[i],
                                   delta=o1_deltas[i] * o1_duty_cycles[i])

    def test_phase_shift_others(self):
        # Tests are written through these lists
        # Values of the same test should have the same index in all lists
        # New values can be added here
        m_values = [46.25, 46.25, 46.25]
        d_values = [3, 3, 3]
        o0_values = [3.75, 3.75, 3.75]
        o1_values = [7, 7, 7]
        o0_phase_shift = [-360, 360, 360]
        o1_phase_shift = [360, -360, 180]
        # All those really tiny delta values are because of tiny floating point differences
        o0_deltas = [0.001, 0.001, 0.001]
        o1_deltas = [0.001, 0.001, 0.001]

        for i in range(len(m_values)):
            configurator = self.setup_configurator_with_specific_config(m_values[i], d_values[i], o0_values[i],
                                                                        o1_values[i])
            configurator.configure_phase_shift_parameters(phase_shift_0=o0_phase_shift[i],
                                                          phase_shift_1=o1_phase_shift[i],
                                                          delta_0=o0_deltas[i], delta_1=o1_deltas[i])

            confi = configurator.configuration_candidates[0]
            self.assertAlmostEqual(confi.get_phase_shift(0).value, o0_phase_shift[i],
                                   delta=abs(o0_deltas[i] * o0_phase_shift[i]))
            self.assertAlmostEqual(confi.get_phase_shift(1).value, o1_phase_shift[i],
                                   delta=abs(o1_deltas[i] * o1_phase_shift[i]))

    def test_candidate_selection(self):
        """
        Tests the "select_candidate" method
        :return: None
        """
        self.after_frequency_setup()

        # Putting mmcm and pll into a list in order to reduce duplicate code a little
        for configurator in [self.configurator_mmcm, self.configurator_pll]:
            candidate = configurator.select_candidate()
            for config in configurator.configuration_candidates:
                # Check that relative error between m_ideal and m of the candidate is leq than relative error between
                # m_ideal and m of the config
                m_ideal = configurator.get_m_ideal()
                self.assertLessEqual(relative_error(m_ideal, candidate.m.value),
                                     relative_error(m_ideal, config.m.value))

                if candidate.m.value == config.m.value:
                    # Also check that D of the candidate is smaller compared to "config" in case of equal M values
                    self.assertLessEqual(candidate.d.value, config.d.value)

    def test_configure_primitive(self):
        """
        Tests the "configure_primitive" method
        :return: None
        """
        self.frequency_setup()

        # Define input dictionaries for MMCM test case
        mmcm_frequency_dict = {"f_in_1": 237.5, "f_out_0": 133.7, "f_out_1": 69, "f_out_2": 500, "f_out_3": 180,
                               "f_out_4": 80, "f_out_5": 160, "f_out_6": 370}
        mmcm_frequency_delta_dict = {"delta_0": 0.005, "delta_1": 0.016, "delta_2": 0.02, "delta_3": 0.023,
                                     "delta_4": 0.05, "delta_5": 0.025, "delta_6": 0.009}
        mmcm_phase_shift_delta_dict = {"delta_1": 0, "delta_3": 0}
        mmcm_duty_cycle_delta_dict = {"delta_0": 0.095, "delta_1": 0.005}

        # Define input dictionaries for PLL test case
        pll_frequency_dict = {"f_in_1": 237.5, "f_out_0": 133.7, "f_out_1": 69, "f_out_2": 500, "f_out_3": 180,
                              "f_out_4": 80, "f_out_5": 160}
        pll_frequency_delta_dict = {"delta_0": 0.003, "delta_1": 0.0005, "delta_2": 0.0009, "delta_3": 0.012,
                                    "delta_4": 0.001, "delta_5": 0.044}
        pll_phase_shift_delta_dict = {"delta_1": 0.0022, "delta_3": 0}
        pll_duty_cycle_delta_dict = {"delta_0": 0.07, "delta_1": 0.005}

        # Define input dictionaries that are for both tests
        phase_shift_dict = {"phase_shift_1": 240, "phase_shift_3": -360}
        duty_cycle_dict = {"duty_cycle_0": 0.125, "duty_cycle_1": 0.67}
        other_args = {"bandwidth": "OPTIMIZED", "startup_wait": True}

        # Put them into a "super" dict in order to be able to put both tests (and possibly future tests) into one loop
        mmcm_dict = {"fpga": self.fpga,
                     "primitive": self.mmcme_2_base,
                     "frequency_args": {**mmcm_frequency_dict, **mmcm_frequency_delta_dict},
                     "phase_shift_args": {**phase_shift_dict, **mmcm_phase_shift_delta_dict},
                     "duty_cycle_args": {**duty_cycle_dict, **mmcm_duty_cycle_delta_dict},
                     "other_args": other_args}
        pll_dict = {"fpga": self.fpga,
                    "primitive": self.plle_2_base,
                    "frequency_args": {**pll_frequency_dict, **pll_frequency_delta_dict},
                    "phase_shift_args": {**phase_shift_dict, **pll_phase_shift_delta_dict},
                    "duty_cycle_args": {**duty_cycle_dict, **pll_duty_cycle_delta_dict},
                    "other_args": other_args}

        for d in [mmcm_dict, pll_dict]:
            configurator = ClockingConfigurator(d["fpga"], d["primitive"])
            configurator.configure_primitive(d["frequency_args"], d["phase_shift_args"], d["duty_cycle_args"],
                                             d["other_args"])
            config = configurator.selected_candidate

            # Check frequencies:
            for index in [int(key[-1]) for key in d["frequency_args"] if "f_out_" in key]:
                key = f"f_out_{index}"
                self.assertAlmostEqual(config.get_output_frequency(index),
                                       d["frequency_args"][key],
                                       delta=d["frequency_args"][f"delta_{index}"] * d["frequency_args"][key])

            # Check phase_shifts:
            for index in [int(key[-1]) for key in d["phase_shift_args"] if "phase_shift_" in key]:
                key = f"phase_shift_{index}"
                self.assertAlmostEqual(config.get_phase_shift(index).value,
                                       d["phase_shift_args"][key],
                                       delta=d["phase_shift_args"][f"delta_{index}"] * d["phase_shift_args"][key])

            # Check duty_cycles:
            for index in [int(key[-1]) for key in d["duty_cycle_args"] if "duty_cycle_" in key]:
                key = f"duty_cycle_{index}"
                self.assertAlmostEqual(config.get_duty_cycle(index).value,
                                       d["duty_cycle_args"][key],
                                       delta=d["duty_cycle_args"][f"delta_{index}"] * d["duty_cycle_args"][key])

    def test_configure_primitive_like_vivado(self):
        """
        Tests the method "configure_primitive_like_vivado.
        Test is similar to "test_configure_primitive" but deltas are now automatically generated
        :return: None
        """
        self.frequency_setup()

        # Define input dictionaries for MMCM test case
        mmcm_frequency_dict = {"f_in_1": 237.5, "f_out_0": 133.7, "f_out_1": 69, "f_out_2": 500, "f_out_3": 180,
                               "f_out_4": 80, "f_out_5": 160, "f_out_6": 370}
        mmcm_frequency_delta_dict = {"delta_0": 0.005, "delta_1": 0.016, "delta_2": 0.02, "delta_3": 0.023,
                                     "delta_4": 0.05, "delta_5": 0.025, "delta_6": 0.009}
        mmcm_phase_shift_delta_dict = {"delta_1": 0, "delta_3": 0}
        mmcm_duty_cycle_delta_dict = {"delta_0": 0.095, "delta_1": 0.005}

        # Define input dictionaries for PLL test case
        pll_frequency_dict = {"f_in_1": 237.5, "f_out_0": 133.7, "f_out_1": 69, "f_out_2": 500, "f_out_3": 180,
                              "f_out_4": 80, "f_out_5": 160}
        pll_frequency_delta_dict = {"delta_0": 0.003, "delta_1": 0.0005, "delta_2": 0.0009, "delta_3": 0.012,
                                    "delta_4": 0.001, "delta_5": 0.044}
        pll_phase_shift_delta_dict = {"delta_1": 0.0022, "delta_3": 0}
        pll_duty_cycle_delta_dict = {"delta_0": 0.07, "delta_1": 0.005}

        # Define input dictionaries that are for both tests
        phase_shift_dict = {"phase_shift_1": 240, "phase_shift_3": -360}
        duty_cycle_dict = {"duty_cycle_0": 0.125, "duty_cycle_1": 0.67}
        other_args = {"bandwidth": "OPTIMIZED", "startup_wait": True}

        # Put them into a "super" dict in order to be able to put both tests (and possibly future tests) into one loop
        mmcm_dict = {"fpga": self.fpga,
                     "primitive": self.mmcme_2_base,
                     "frequency_args": {**mmcm_frequency_dict},
                     "phase_shift_args": {**phase_shift_dict},
                     "duty_cycle_args": {**duty_cycle_dict},
                     "other_args": other_args}
        pll_dict = {"fpga": self.fpga,
                    "primitive": self.plle_2_base,
                    "frequency_args": {**pll_frequency_dict},
                    "phase_shift_args": {**phase_shift_dict},
                    "duty_cycle_args": {**duty_cycle_dict},
                    "other_args": other_args}

        for d in [mmcm_dict, pll_dict]:
            configurator = ClockingConfigurator(d["fpga"], d["primitive"])
            configurator.configure_primitive(d["frequency_args"], d["phase_shift_args"], d["duty_cycle_args"],
                                             d["other_args"])
            config = configurator.selected_candidate

            # Test deltas values are chosen in a rather arbitrary way here.
            # This test is mostly about checking whether or not errors come up
            # Check frequencies:
            for index in [int(key[-1]) for key in d["frequency_args"] if "f_out_" in key]:
                key = f"f_out_{index}"
                self.assertAlmostEqual(config.get_output_frequency(index),
                                       d["frequency_args"][key],
                                       delta=0.07 * d["frequency_args"][key])

            # Check phase_shifts:
            for index in [int(key[-1]) for key in d["phase_shift_args"] if "phase_shift_" in key]:
                key = f"phase_shift_{index}"
                self.assertAlmostEqual(config.get_phase_shift(index).value,
                                       d["phase_shift_args"][key],
                                       delta=0.14 * d["phase_shift_args"][key])

            # Check duty_cycles:
            for index in [int(key[-1]) for key in d["duty_cycle_args"] if "duty_cycle_" in key]:
                key = f"duty_cycle_{index}"
                self.assertAlmostEqual(config.get_duty_cycle(index).value,
                                       d["duty_cycle_args"][key],
                                       delta=0.14 * d["duty_cycle_args"][key])


