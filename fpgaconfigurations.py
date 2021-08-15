from fpgaprimitives import ClockPrimitive
from fpgamodel import FPGAModel
from math import floor, ceil
from utility import relative_error


class ClockingConfiguration:

    def __init__(self, fpga: FPGAModel, primitive: ClockPrimitive):
        self.fpga = fpga
        self.primitive = primitive
        self.configuration_candidates = []
        self.selected_candidate = None

    def configure_frequency_parameters(self, f_in_1: float, f_out_0: float,
                                       f_out_1: float = None, f_out_2: float = None, f_out_3: float = None,
                                       f_out_4: float = None, f_out_5: float = None, f_out_6: float = None,
                                       delta_0: float = 0.5, delta_1: float = 0.5,
                                       delta_2: float = 0.5, delta_3: float = 0.5,
                                       delta_4: float = 0.5, delta_5: float = 0.5,
                                       delta_6: float = 0.5, f_out_4_cascade=False) -> list:

        # Filter desired output values that have not been set
        output_frequencies = {index: value
                              for index, value
                              in enumerate([f_out_0, f_out_1, f_out_2, f_out_3, f_out_4, f_out_5, f_out_6])
                              if value is not None}

        deltas = {index: value
                  for index, value
                  in enumerate([delta_0, delta_1, delta_2, delta_3, delta_4, delta_5, delta_6])
                  }

        if self.primitive.get_output_clk_count() == 6 and 6 in output_frequencies:
            return []

        d_min, d_max, m_min, m_max = self.get_d_m_min_max(f_in_1)

        # This list contains fractions that have already been evaluated as not fitting
        # So m = 2, d = 5 wont be evaluated if 0.4 is already in this list
        checked_m_d_combinations = []
        valid_configurations = []

        for m_temp in self.primitive.get_m_generator(start=m_min, end=m_max):
            for d_temp in self.primitive.get_d_generator(start=d_min, end=d_max):

                if (m_temp / d_temp) in checked_m_d_combinations:
                    continue

                config = self.primitive.get_new_instance()
                config.set_in_period_based_on_frequency(f_in_1)
                found = config.calc_approximated_o_dividers(m_temp, d_temp, f_in_1, output_frequencies, deltas,
                                                            self.fpga.get_f_out_min(self.primitive.specification),
                                                            self.fpga.get_f_out_max(self.primitive.specification))

                if found:
                    valid_configurations.append(config)
                checked_m_d_combinations.append(m_temp / d_temp)

        self.configuration_candidates = valid_configurations
        return valid_configurations

    # Compute min and max values for m and d according to Xilinx
    def get_d_m_min_max(self, f_in):

        # find the min and max values for the frequency divider d (DIVCLK_DIVIDE)
        d_min = ceil(f_in / self.fpga.get_pfd_max(self.primitive.specification))
        d_max = floor(f_in / self.fpga.get_pfd_min(self.primitive.specification))

        # find the min and values for the frequency divider m (CLKFBOUT_MULT_F or CLKFBOUT_MULT,
        # aka frequency multiplier)
        m_min = ceil((self.fpga.get_vco_min(self.primitive.specification) * d_min) / f_in)
        m_max = floor((self.fpga.get_vco_max(self.primitive.specification) * d_max) / f_in)

        return d_min, d_max, m_min, m_max

    def configure_phase_shift_parameters(self, phase_shift_0: float = None, phase_shift_1: float = None,
                                         phase_shift_2: float = None, phase_shift_3: float = None,
                                         phase_shift_4: float = None, phase_shift_5: float = None,
                                         phase_shift_6: float = None, delta_0: float = 0.5, delta_1: float = 0.5,
                                         delta_2: float = 0.5, delta_3: float = 0.5, delta_4: float = 0.5,
                                         delta_5: float = 0.5, delta_6: float = 0.5):
        pass

    def configure_duty_cycle_parameters(self, duty_cycle_0: float = None, duty_cycle_1: float = None,
                                        duty_cycle_2: float = None, duty_cycle_3: float = None,
                                        duty_cycle_4: float = None, duty_cycle_5: float = None,
                                        duty_cycle_6: float = None, delta_0: float = 0.5, delta_1: float = 0.5,
                                        delta_2: float = 0.5, delta_3: float = 0.5, delta_4: float = 0.5,
                                        delta_5: float = 0.5, delta_6: float = 0.5):
        duty_cycles = {index: value
                       for index, value
                       in enumerate([duty_cycle_0, duty_cycle_1, duty_cycle_2,
                                     duty_cycle_3, duty_cycle_4, duty_cycle_5, duty_cycle_6])
                       if value is not None}
        deltas = {index: value
                  for index, value
                  in enumerate([delta_0, delta_1, delta_2, delta_3, delta_4, delta_5, delta_6])
                  }

        updated_candidates = []

        for configuration in self.configuration_candidates:
            viable_candidate = True
            for index in duty_cycles:
                # TODO write get duty cycles
                configuration.get_properties_dict[f"clkout{index}_divide"].set_and_correct_value(duty_cycles[index])
                if relative_error(duty_cycles[index], configuration.get_properties_dict[f"clkout{index}_divide"].value) > deltas[index]:
                    viable_candidate = False
                    break

            if viable_candidate:
                updated_candidates.append(configuration)

    def configure_other_parameters(self, bandwidth: str = None, ref_jitter1: float = None, startup_wait: bool = None):
        if bandwidth is not None:
            self.selected_candidate.bandwidth.set_value(bandwidth)
        if ref_jitter1 is not None:
            self.selected_candidate.ref_jitter1.set_value(ref_jitter1)
        if startup_wait is not None:
            self.selected_candidate.startup_wait.set_value(startup_wait)

    def generate_template(self):
        return self.configuration_candidates[0].generate_template()

    def get_properties_dict(self):
        return self.configuration_candidates[0].get_properties_dict()

    # Method was made for testing purposes only
    def set_blank_selected_candidate(self):
        self.selected_candidate = self.primitive.get_new_instance()
