from fpgaobjects import FPGAModel, ClockPrimitive
from math import floor, ceil

class ClockingConfiguration:

    def __init__(self, fpga: FPGAModel, primitive: ClockPrimitive):
        self.fpga = fpga
        self.primitive = primitive
        self.configuration_candidates = []

    def get_configurations_for_output_frequencies(self, f_in_1: float,  f_out_0: float, f_out_1:float = None, f_out_2:float = None,
                                 f_out_3:float = None, f_out_4:float = None, f_out_5:float = None, f_out_6:float = None,
                                 deviation: float = 0.5, f_out_4_cascade=False) -> list:

        # Filter desired output values that have not been set
        output_frequencies = {index: value
                             for index, value
                             in enumerate([f_out_0, f_out_1, f_out_2, f_out_3, f_out_4, f_out_5, f_out_6])
                             if value is not None}

        if self.primitive.get_output_clk_count() == 6 and 6 in output_frequencies:
            return []

        d_min, d_max, m_min, m_max = self.get_d_m_min_max(f_in_1)

        # This list contains fractions that have already been evaluated as not fitting
        # So m = 2, d = 5 wont be evaluated if 0.4 is already in this list
        checked_m_d_combinations = []
        valid_configurations = []
        for m_temp in self.primitive.get_m_generator(start=m_min, end=m_max):
            for d_temp in self.primitive.get_d_generator(start=d_min, end=d_max):
                if (m_temp, d_temp) in checked_m_d_combinations:
                    continue

                config = self.primitive.calc_approximated_o_dividers(m_temp, d_temp, f_in_1, output_frequencies, deviation=deviation)
                if config is None:
                    checked_m_d_combinations.append((m_temp, d_temp))
                else:
                    valid_configurations.append(config)

        return valid_configurations



    # Compute min and max values for m and d according to Xilinx
    def get_d_m_min_max(self, f_in):

        # find the min and max values for the frequency divider d (DIVCLK_DIVIDE)
        d_min = ceil(f_in / self.fpga.get_pfd_max(self.primitive.specification))
        d_max = floor(f_in / self.fpga.get_pfd_min(self.primitive.specification))

        # find the min and values for the frequency divider m (CLKFBOUT_MULT_F or CLKFBOUT_MULT, aka frequency multiplier)
        m_min = ceil((self.fpga.get_vco_min(self.primitive.specification) * d_min) / f_in)
        m_max = floor((self.fpga.get_vco_max(self.primitive.specification) * d_max) / f_in)

        return d_min, d_max, m_min, m_max