import unittest
from fpga_configurator import ClockingConfigurator
import fpga_primitives
from fpga_globals import FPGA_MODELS


class OtherParameterTests(unittest.TestCase):
    model_keys = [('artix-7', '#-2LE', '0.9V'), ('kintex', '#-2', '1.0V'), ('virtex-7', '-2')]
    bandwidths = ["OPTIMIZED", "HIGH", "LOW"]
    ref_jitters = [0.0, 0.5, 0.999]

    def setUp(self) -> None:
        self.test_candidates = [ClockingConfigurator(FPGA_MODELS[primitive], model.get_new_instance())
                                for primitive in self.model_keys
                                for model in [fpga_primitives.MmcmBlockConfiguration, fpga_primitives.PllBlockConfiguration]
                                ]
        for config in self.test_candidates:
            config.set_blank_selected_candidate()

    def test_blank(self):
        for config in self.test_candidates:
            self.assertEqual(config.selected_candidate.bandwidth.value, "OPTIMIZED")
            self.assertEqual(config.selected_candidate.ref_jitter1.value, 0.01)
            self.assertEqual(config.selected_candidate.startup_wait.value, False)

    def test_bandwidth(self):
        for config in self.test_candidates:
            for value in self.bandwidths:
                config.configure_other_parameters(bandwidth=value)
                self.assertEqual(config.selected_candidate.bandwidth.value, value)

            # Test exception
            with self.assertRaises(ValueError) as context:
                config.configure_other_parameters(bandwidth="GUNTHER")

    def test_ref_jitter(self):
        for config in self.test_candidates:
            for value in self.ref_jitters:
                config.configure_other_parameters(ref_jitter1=value)
                self.assertEqual(config.selected_candidate.ref_jitter1.value, value)

            # Test exception
            with self.assertRaises(TypeError) as context:
                config.configure_other_parameters(ref_jitter1="Gunther")

    # Startup is not tested in an isolated test case since it is just a boolean value

    # Test multiple combinations of values at the same time
    def test_combinations(self):
        for config in self.test_candidates:
            for bandwidth in self.bandwidths:
                for rj in self.ref_jitters:
                    for startup_w in [True, False]:
                        config.configure_other_parameters(bandwidth=bandwidth, ref_jitter1=rj, startup_wait=startup_w)
                        self.assertEqual(config.selected_candidate.bandwidth.value, bandwidth)
                        self.assertEqual(config.selected_candidate.ref_jitter1.value, rj)
                        self.assertEqual(config.selected_candidate.startup_wait.value, startup_w)



