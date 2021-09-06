from fpga_primitives import ClockPrimitive
from fpga_model import FPGAModel
from math import floor, ceil
from operator import attrgetter
from utility import relative_error


class ClockingConfigurator:

    def __init__(self, fpga: FPGAModel, primitive: ClockPrimitive):
        self.fpga = fpga
        self.primitive = primitive
        # Caching f_out_min and max since they will be used a lot (this reduces unnecessary calls and code duplicates)
        self.f_out_min = fpga.get_f_out_min(self.primitive.specification)
        self.f_out_max = fpga.get_f_out_max(self.primitive.specification)
        self.configuration_candidates = []
        self.selected_candidate = None
        self.f_in_1 = None
        self.d_min = None

    def configure_primitive(self, frequency_args: dict, phase_shift_args: dict, duty_cycle_args: dict,
                            other_args: dict):
        """
        Wrapper method for the configuration methods.
        They are called sequentially.
        :param frequency_args: Arguments for "configure_frequency_parameters" as a kwargs dict
        :param phase_shift_args: Arguments for "configure_phase_shift_parameters" as a kwargs dict
        :param duty_cycle_args: Arguments for "configure_duty_cycle_parameters" as a kwargs dict
        :param other_args: Arguments for "configure_other_parameters" as a kwargs dict
        :return: The most fitting configuration candidate
        """

        # This call is not part of the loop below because the frequency_args should never be empty
        # and this call is obligatory
        self.configure_frequency_parameters(**frequency_args)

        for dic, method in zip([phase_shift_args, duty_cycle_args], [self.configure_phase_shift_parameters,
                                                                     self.configure_duty_cycle_parameters]):
            # Call the method with the arguments if the argument dict is not empty
            if dic:
                method(**dic)

        self.select_candidate()
        # Those "other" arguments are independent of previous steps, which is why they are added only at the end.
        self.configure_other_parameters(**other_args)

        return self.selected_candidate

    def configure_primitive_like_vivado(self, frequency_args: dict, phase_shift_args: dict, duty_cycle_args: dict,
                                        other_args: dict, granularity: int = 10):
        """
        Similar to configure_primitive but deltas are not chosen from the argument dictionaries.
        Instead delta values are chosen by this this method.
        This Method tries to chose configuration values in a way that is similar to vivados clocking wizard.
        It stops when a fitting configuration was found or when delta values overstep a certain limit.
        Output ports of higher index are considered less important.
        Taking many iterations makes this method potentially very slow
        :param frequency_args: Arguments for "configure_frequency_parameters" as a kwargs dict
        :param phase_shift_args: Arguments for "configure_phase_shift_parameters" as a kwargs dict
        :param duty_cycle_args: Arguments for "configure_duty_cycle_parameters" as a kwargs dict
        :param other_args: Arguments for "configure_other_parameters" as a kwargs dict
        :param granularity: Step size for the increase of delta. Higher granularity means longer computation time
        :return: The most fitting configuration candidate
        """
        # Get the list of output frequencies that are used
        frequency_indexes = [key[-1] for key in frequency_args if "f_out_" in key]
        # Get index of output ports that also demand a certain phase shift or duty cycle
        phase_shift_indexes = [key[-1] for key in phase_shift_args if "phase_shift_" in key]
        duty_cycle_indexes = [key[-1] for key in duty_cycle_args if "duty_cycle_" in key]
        base_weight = 0.1 / granularity

        # The deltas increase with each loop the following way:
        # Iteration 1: delta_0: 0, delta_1: 0, delta_2: 0 ... delta_6: 0
        # Iteration granularity / 2: delta_0: 0.05, delta_1: 0.1, delta_2: 0.15, ... delta_6: 0.35
        # Last Iteration: delta_0: 0.1, delta_1: 0.2, delta_2: 0.3 ... delta_6: 0.7
        for weight_factor in range(granularity + 1):
            # Frequency deltas
            deltas_args = {f"deltas_{index}": base_weight * (index + 1) * weight_factor for index in frequency_indexes}

            # Deltas for phase shifts and duty cycles are more generous (this behavior is also typical for vivado)
            # Deltas for phase shifts
            delta_phase_shift_args = {f"delta_{index}": base_weight * (index + 1) * weight_factor * 2
                                      for index in phase_shift_indexes}
            # Deltas for duty cycles
            delta_duty_cycle_args = {f"delta_{index}": base_weight * (index + 1) * weight_factor * 2 for
                                     index in duty_cycle_indexes}

            # Try to find a configuration using the generated deltas
            config = self.configure_primitive({**frequency_args, **deltas_args},
                                              {**phase_shift_args, **delta_phase_shift_args},
                                              {**duty_cycle_args, **delta_duty_cycle_args},
                                              other_args)
            if config:
                return config

        # This line is only reached if no config was found by the end of the loop
        # Return None because configuration was found even with rather high delta values
        return None

    def configure_frequency_parameters(self, f_in_1: float, f_out_0: float,
                                       f_out_1: float = None, f_out_2: float = None, f_out_3: float = None,
                                       f_out_4: float = None, f_out_5: float = None, f_out_6: float = None,
                                       delta_0: float = 0.15, delta_1: float = 0.15,
                                       delta_2: float = 0.15, delta_3: float = 0.15,
                                       delta_4: float = 0.15, delta_5: float = 0.15,
                                       delta_6: float = 0.15, f_out_4_cascade=False) -> list:

        # Set f_in_1 for later usage
        self.f_in_1 = f_in_1

        # Filter desired output values that have not been set
        output_frequencies = {index: value
                              for index, value
                              in enumerate([f_out_0, f_out_1, f_out_2, f_out_3, f_out_4, f_out_5, f_out_6])
                              if value is not None}

        deltas = {index: value
                  for index, value
                  in enumerate([delta_0, delta_1, delta_2, delta_3, delta_4, delta_5, delta_6])
                  }

        # Raise Error
        # Happens if number of demanded number of ports do not fit the model
        if 6 in output_frequencies and self.primitive.specification == "pll":
            raise ValueError(f"Error, too many ports. {self.primitive.specification} does not support more than "
                             "6 output ports.")

        # Get some boundary values based on the input frequency, pfd and vco
        # Also d_min is saved as in an attribute for later usage in the "select_candidate" method
        self.d_min, d_max, m_min, m_max = self.get_d_m_min_max(f_in_1)

        # This list contains fractions that have already been evaluated as not fitting
        # So m = 2, d = 5 wont be evaluated if 0.4 is already in this list
        checked_m_d_combinations = []
        valid_configurations = []

        for m_temp in self.primitive.get_m_generator(start=m_min, end=m_max):
            for d_temp in self.primitive.get_d_generator(start=self.d_min, end=d_max):
                # The generator does limit m and d already
                # But there are still m, d combinations that are filtered here
                if not (self.fpga.get_vco_min(self.primitive.specification) <= (f_in_1 * m_temp) / d_temp
                        <= self.fpga.get_vco_max(self.primitive.specification)):
                    continue
                if m_temp / d_temp in checked_m_d_combinations:
                    continue
                config = self.get_new_configuration_with_o_dividers(f_in_1, m_temp, d_temp, output_frequencies, deltas)

                # config is either empty, an error code ("4") or a viable configuration
                if config and config != "4":
                    valid_configurations.append(config)
                # The block below is only relevant if the cascade of the divider 6 into the divider 4 is activated
                elif self.primitive.specification == "mmcm" and f_out_4_cascade and 4 in output_frequencies \
                        and config == "4":
                    # Use a copy of the dictionary which uses a different value for the output frequency 4
                    # though the actual output frequency 4 will not change because of the cascade
                    temp_output_frequencies = output_frequencies.copy()
                    temp_conf = self.primitive.get_new_instance()

                    # Take the output target output frequency 6 into account (if it exists)
                    if 6 in output_frequencies and output_frequencies[6] > output_frequencies[4]:
                        o6_value = temp_conf.approximate_o_divider(6, m_temp, d_temp, f_in_1, output_frequencies[6],
                                                                   deltas[6], self.f_out_min, self.f_out_max)

                        if o6_value is not None:
                            temp_output_frequencies[4] = temp_output_frequencies[4] * o6_value

                            config = self.get_new_configuration_with_o_dividers(f_in_1, m_temp, d_temp,
                                                                                temp_output_frequencies, deltas)
                            # Set cascade manually
                            if config and config != "4":
                                config.clkout4_cascade.set_value(True)

                    elif 6 not in output_frequencies:
                        # Another support function will compute o4 and o6 in this specific case and set them manually
                        tupl = self.precompute_o6_divider(f_in_1, m_temp, d_temp, output_frequencies[4],
                                                                        deltas[4])
                        if tupl is not None:
                            o4_value, o6_value = tupl

                            # Remove output 4 from dictionary since it will be set manually
                            temp_output_frequencies.pop(6, None)
                            temp_output_frequencies.pop(4, None)
                            # Try to create new config
                            config = self.get_new_configuration_with_o_dividers(f_in_1, m_temp, d_temp,
                                                                                temp_output_frequencies, deltas)
                            if config and config != "4":
                                # Set o4 and o6 manually
                                config.clkout4_divide.value = o4_value
                                config.clkout4_divide.on = True
                                config.clkout6_divide.value = o6_value
                                config.clkout6_divide.on = True
                                # Set cascade manually
                                config.clkout4_cascade.set_value(True)

                    if config and config != "4":
                        valid_configurations.append(config)

                checked_m_d_combinations.append(m_temp / d_temp)

        self.configuration_candidates = valid_configurations
        return valid_configurations

    # Compute min and max values for m and d according to Xilinx
    def get_d_m_min_max(self, f_in: float):

        # find the min and max values for the frequency divider d (DIVCLK_DIVIDE)
        d_min = ceil(f_in / self.fpga.get_pfd_max(self.primitive.specification))
        d_max = floor(f_in / self.fpga.get_pfd_min(self.primitive.specification))

        # find the min and values for the frequency divider m (CLKFBOUT_MULT_F or CLKFBOUT_MULT,
        # aka frequency multiplier)
        m_min = ceil((self.fpga.get_vco_min(self.primitive.specification) * d_min) / f_in)
        m_max = floor((self.fpga.get_vco_max(self.primitive.specification) * d_max) / f_in)

        return d_min, d_max, m_min, m_max

    def get_new_configuration_with_o_dividers(self, f_in_1: float, m, d, output_frequencies: dict, deltas: dict):
        config = self.primitive.get_new_instance()
        config.set_in_period_based_on_frequency(f_in_1)
        found = config.configure_approximated_o_dividers(m, d, f_in_1, output_frequencies, deltas, self.f_out_min,
                                                         self.f_out_max)
        if found:
            return config
        elif 4 in output_frequencies and \
                relative_error(output_frequencies[4], config.get_output_frequency(4)) > deltas[4]:
            # Error code for higher level function
            return "4"
        return False

    def precompute_o6_divider(self, f_in_1: float, m, d, target_f_out_4, delta_4):
        """
        Compute a output divider value for o6 with no respect to the output frequency 6 itself
        The goal is to find a fitting o6 for a target output frequency 4
        """
        # Make sure the target frequency is within the technical limitations

        f_vco = (f_in_1 * m) / d
        # o_64 represents the product of o4 and o6
        lower_o_64 = f_vco / (target_f_out_4 + target_f_out_4 * delta_4)
        upper_o_64 = f_vco / (target_f_out_4 - target_f_out_4 * delta_4)

        # Many combinations of o4 and o6 will lead to the same o64 which is why we use a nested for loop
        # The goal is to find o64 with o4 as big as possible (this will enable finer duty cycle and ps values later)
        for o4 in range(128, 1, -1):
            if f_vco / o4 < self.f_out_min:
                continue
            for o6 in range(1, 128):
                # o6 values that are too small have to be skipped
                if f_vco / o6 > self.f_out_max:
                    continue
                # Break the inner o6 loop if o6 gets too big
                if f_vco / o6 < self.f_out_min:
                    break
                if lower_o_64 <= o4 * o6 <= upper_o_64 and self.f_out_min <= f_vco / (o6 * o4) <= self.f_out_max:
                    # found the biggest fitting o6 with a fitting o4 for o64
                    return o4, o6

    def configure_phase_shift_parameters(self, phase_shift_0: float = None, phase_shift_1: float = None,
                                         phase_shift_2: float = None, phase_shift_3: float = None,
                                         phase_shift_4: float = None, phase_shift_5: float = None,
                                         phase_shift_6: float = None, delta_0: float = 0.15, delta_1: float = 0.15,
                                         delta_2: float = 0.15, delta_3: float = 0.15, delta_4: float = 0.15,
                                         delta_5: float = 0.15, delta_6: float = 0.15):

        # Create dictionary of used phase shifts for quick access
        phase_shifts = {index: value
                        for index, value
                        in enumerate([phase_shift_0, phase_shift_1, phase_shift_2, phase_shift_3, phase_shift_4,
                                      phase_shift_5, phase_shift_6])
                        if value is not None}
        # Create a dictionary of used dictionaries for quick access
        deltas = {index: value
                  for index, value
                  in enumerate([delta_0, delta_1, delta_2, delta_3, delta_4, delta_5, delta_6])}

        # Initiate new List
        updated_candidates = []

        for config in self.configuration_candidates:
            # The clkfbout_phase is used in order to make the the most out of the clock primitives attributes
            config.clkfbout_phase.increment = 45 / config.d.value

            viable_candidate = True
            for index in phase_shifts:
                # Quicksave reference to current phase shift in order to not call a get function over and over again
                current_pshift = config.get_phase_shift(index)

                # Initiate increment and end value (in degrees)
                divider_value = config.get_output_divider(index).value
                current_pshift.increment = 45 / divider_value

                if divider_value > 64:
                    current_pshift.end = (63 / divider_value) * 360 + 7 * (45 / divider_value)

                # Set next best phase shift
                # The cp_value is subtracted from the target value since all clocks will the shifted backwards by
                # the value of clkfbout_phase (which is cp_value)
                current_pshift.set_and_correct_value(phase_shifts[index])
                current_pshift.on = True

                # Reject this combination of clkfbout_phase and output phase shifts if it goes beyond delta
                if relative_error(phase_shifts[index], current_pshift.value) > deltas[index]:
                    viable_candidate = False
                    break

            if viable_candidate:
                updated_candidates.append(config)

        self.configuration_candidates = updated_candidates
        return updated_candidates

    def configure_duty_cycle_parameters(self, duty_cycle_0: float = None, duty_cycle_1: float = None,
                                        duty_cycle_2: float = None, duty_cycle_3: float = None,
                                        duty_cycle_4: float = None, duty_cycle_5: float = None,
                                        duty_cycle_6: float = None, delta_0: float = 0.15, delta_1: float = 0.15,
                                        delta_2: float = 0.15, delta_3: float = 0.15, delta_4: float = 0.15,
                                        delta_5: float = 0.15, delta_6: float = 0.15):
        # Create a dictionary of used duty_cycles for quick access
        duty_cycles = {index: value
                       for index, value
                       in enumerate([duty_cycle_0, duty_cycle_1, duty_cycle_2, duty_cycle_3, duty_cycle_4, duty_cycle_5,
                                     duty_cycle_6])
                       if value is not None}
        # Create a dictionary of used deltas for quick access
        deltas = {index: value
                  for index, value
                  in enumerate([delta_0, delta_1, delta_2, delta_3, delta_4, delta_5, delta_6])}

        # Initiate new List
        updated_candidates = []

        for config in self.configuration_candidates:
            viable_candidate = True
            for index in duty_cycles:
                # Quicksave reference to current duty cycle in order to not call the same function over and over again
                current_dc = config.get_duty_cycle(index)

                # Initiate the increment attribute based on the duty cycle restrictions
                # WARNING: The next lines restriction is derived from a list of about 210 tests
                # It may be possible for this formula to not work in certain unknown edge cases
                divider_value = config.get_output_divider(index).value
                current_dc.increment = 1 / (divider_value * 2)
                if divider_value >= 64:
                    current_dc.start = 0.5 - (128 - divider_value) * (0.5 / divider_value)
                else:
                    current_dc.start = 1 / divider_value

                # Set the next best duty cycle value
                current_dc.set_and_correct_value(duty_cycles[index])
                current_dc.on = True

                # Reject the entire configuration if the result is not within the error margin of delta
                if relative_error(duty_cycles[index], current_dc.value) > deltas[index]:
                    viable_candidate = False
                    break

            if viable_candidate:
                updated_candidates.append(config)

        self.configuration_candidates = updated_candidates
        return updated_candidates

    def configure_other_parameters(self, bandwidth: str = None, ref_jitter1: float = None, startup_wait: bool = None):
        if bandwidth is not None:
            self.selected_candidate.bandwidth.set_value(bandwidth)
        if ref_jitter1 is not None:
            self.selected_candidate.ref_jitter1.set_value(ref_jitter1)
        if startup_wait is not None:
            self.selected_candidate.startup_wait.set_value(startup_wait)

    def select_candidate(self):
        """
        Sorts configurations by fitness according to Xilinx' criteria then returns the most fitting configuration.
        Then Sets the most fitting candidate and also returns them.
        :return: The most fitting configuration candidate of self.configuration_candidates
        """
        # "Skip" if there is only 1 or 0 candidates
        if len(self.configuration_candidates) == 0:
            return
        elif len(self.configuration_candidates) > 1:
            # According to Xilinx:
            # D has to be as small as possible.
            # M also should be as small as possible but more importantly, it has to be as close as possible to m_ideal

            # m_ideal according to Xilinx:
            m_ideal = (self.d_min * self.fpga.get_vco_max(self.primitive.specification)) / self.f_in_1

            # Sorting could be done by using weights for "smallness" of M, D and relative error between M and m_ideal
            # But instead priority is used here:
            # 1. Closeness to m_ideal
            # 2. D ascending
            # 3. M ascending

            # First sort the list by D and secondarily by M using the operator function "attrgetter"
            self.configuration_candidates = sorted(self.configuration_candidates, key=attrgetter("d.value", "m.value"))

            # Then sort the list again by the relative error of m_ideal and M
            self.configuration_candidates = sorted(self.configuration_candidates,
                                                   key=lambda config: relative_error(m_ideal, config.m.value))

        self.selected_candidate = self.configuration_candidates[0]
        return self.selected_candidate

    def generate_template(self):
        return self.selected_candidate.generate_template()

    def get_properties_dict(self):
        return self.selected_candidate.get_properties_dict()

    def get_m_ideal(self):
        """
        Method computes and returns m_ideal based on f_in_1 and the fpga model vco maximum frequency
        Note: This will work after using "configure_frequency_parameters", since only then f_in_1 will be set
        :return: The ideal value of the Clocking Tiles Multiplier M, based on the input frequency
        """
        return (self.d_min * self.fpga.get_vco_max(self.primitive.specification)) / self.f_in_1
